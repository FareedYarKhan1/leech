from django.shortcuts import render
from .models import task,task_images
from leech import settings
# Create your views here.
from scrapper.functions import resolution
from .tasks import scrapp_image
from django.contrib.auth.decorators import login_required
from .models import results
from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse

@login_required(login_url='login')
def upload(request):
    results_obj=task.objects.filter(user=request.user)
    
    return render(request,'dashboard.html', context=({'results':results_obj}))

@login_required(login_url='login')
def uploadView(request):

    
    return render(request,'index.html')

def add_task(request):
    img=[]
    media_url = settings.MEDIA_URL
    type=request.POST.get('type')
    file=request.FILES.getlist('task_img')
    if file:
        task_obj=task.objects.create(user=request.user,task_type=type)
    else:
        query=request.POST.get('query')
        task_obj=task.objects.create(user=request.user,task_type=type,query=query)
    if file:
        for f in file:
            img_obj=task_images.objects.create(task=task_obj,picture=f)
            image=img_obj.picture.name
            img.append(media_url+image)
        scrapp_image.delay(task_obj.pk,img)
    return render(request,'index.html',context=({'status':1}))

@csrf_exempt
def view_task(request):
    
    id=request.POST.get('id')
    type=request.POST.get('type')
    response=""
    if type=="view":
        task_obj=task.objects.get(pk=id)
        result=results.objects.select_related('task').filter(task=task_obj)
        response= list(result.values())
        if task_obj.task_type=="1":
            response.append(str(task_obj.query))
        else:
            response.append(str(task_obj))
      
    elif type=="edit":
        task_obj=task.objects.get(pk=id)
        if(task_obj.monitoring_enabled):
            task_obj.monitoring_enabled=False
            response=f'<button class="btn btn-sm btn-danger"  onclick="editTask({task_obj.pk})">OFF</button>'
        elif(task_obj.monitoring_enabled==False):
            task_obj.monitoring_enabled=True
            response=f'<button class="btn btn-sm btn-success"  onclick="editTask({task_obj.pk})">ON</button>'
        task_obj.save()
    elif type=="delete":
        task_obj=task.objects.get(pk=id).delete()
        response=1
    elif type=="view_images":
        response=[]
        task_obj=task.objects.get(pk=id)
        image=task_images.objects.filter(task=task_obj)
        for img in image:
            res={'image':img.picture.url}
            response.append(res)
      
    
    return JsonResponse({'response':response})