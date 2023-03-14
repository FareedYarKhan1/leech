from django.shortcuts import render
from .models import task,task_images,notice
from leech import settings
# Create your views here.
from scrapper.functions import resolution
from scrapper.functions_v3 import append_new_links
from .tasks import scrapp_image
from django.contrib.auth.decorators import login_required
from .models import results
from django.views.decorators.csrf import csrf_exempt
import os
# importing modules
import urllib.request
from django.http import JsonResponse
import pandas as pd
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import HttpResponse
from .consumers import * 

import numpy as np
from django.shortcuts import redirect

@login_required(login_url='login')
def upload(request):
    results_obj=task.objects.filter(user=request.user)
    for results in results_obj:
         print(results.get_unread_links)
    return render(request,'dashboard.html', context=({'results':results_obj}))

@login_required(login_url='login')
def uploadView(request):

    
    return render(request,'index.html')

def add_task(request):
    img=[]
    media_url = settings.MEDIA_URL
    type=request.POST.get('type')
    msg=''
    if type=='1':
    
        query=request.POST.get('query')
        if query=='':
            msg="Please Enter keyword to search"
            
        else:
            task_obj=task.objects.create(user=request.user,task_type=type,query=query)
            msg="Query Searching Task Added"
            return redirect('/')
            
    elif type=='2':
        file=request.FILES.getlist('task_img')
        if file:
            for f in file:
                task_obj=task.objects.create(user=request.user,task_type=type)
                task_obj.search_image=f
                task_obj.save()
                image_url=task_obj.search_image.url
                image_name=task_obj.search_image.name
                local_path="Temp/saved_img_temp/"+image_name
                urllib.request.urlretrieve(image_url,local_path)
                img.append(local_path)
                msg="Image Search Task Added"
                scrapp_image.delay(task_obj.pk,img)
                img.clear()
            return redirect('/')
        else:
            msg="Please Upload At Lease 1 image"
    
    return render(request,'index.html',context=({'status':msg}))

@csrf_exempt
def view_task(request):
    
    id=request.POST.get('id')
    t_type=request.POST.get('type')
    response=""
    query=''
    task_type=''
    if t_type=="view":
        
        task_obj=task.objects.get(pk=id)
        query=task_obj.query
        result=results.objects.select_related('task').filter(task=task_obj)
        response=[]
        task_type=-1
        for result in result:
            #local_path="Temp/temp_save_csvfile/"+str(result.task.pk)+".csv"
            #urllib.request.urlretrieve(result.result_file,local_path)
            df = pd.read_csv(result.result_file)
            df.fillna(method='bfill',inplace=True)
            df = df.reset_index()  # make sure indexes pair with number of rows

            if result.task.task_type=="1":
                task_type=0
                print("1")
                for index, row in df.iterrows():
                    
                    each={'urls':row['url'],'titles':row['title'],'occurance':row['occurance']}
                    response.append(each)
            elif result.task.task_type=="2":
                print("2")
                task_type=1
                
                for index, row in df.iterrows():
                    link=row['urls']
                    type=row['type']

                    each={'similar':link,'exact':type}
                    response.append(each)
                print(response)
    elif t_type=="edit":
        task_obj=task.objects.get(pk=id)
        if(task_obj.monitoring_enabled):
            task_obj.monitoring_enabled=False
            response=f'<button class="btn btn-sm btn-danger"  onclick="editTask({task_obj.pk})">OFF</button>'
        elif(task_obj.monitoring_enabled==False):
            task_obj.monitoring_enabled=True
            response=f'<button class="btn btn-sm btn-success"  onclick="editTask({task_obj.pk})">ON</button>'
        task_obj.save()
    elif t_type=="delete":
        task_obj=task.objects.get(pk=id).delete()
        response=1
    elif t_type=="view_images":
        response=[]
        task_obj=task.objects.get(pk=id)
        image=task_images.objects.filter(task=task_obj)
        for img in image:
            res={'image':img.picture.url}
            response.append(res)
      
    
    return JsonResponse({'response':response,'query':query,'task_type':task_type})
@csrf_exempt
def viewNotice(request):
    response="<table class='table'><thead><tr><th scope='col'>Links</th><th>Type</th></tr<tbody>"
    id=request.POST.get('id')
    task_obj=task.objects.get(pk=id)
    nt_obj=None
    
        
    if task_obj.task_type=='1':
            try:
                nt_obj=notice.objects.get(task=task_obj)
                if not os.path.exists(nt_obj.links):
                        
                    if not os.path.exists(f'Temp/task-{task_obj.pk}/task-{task_obj.pk}-first_notice.csv'):
                            response="<p clas='text-center'>No Data To Show</p>"
                    else:
                            df = pd.read_csv(f'Temp/task-{task_obj.pk}/task-{task_obj.pk}-first_notice.csv')
                            df.fillna(method='bfill',inplace=True)
                            df = df.reset_index()  # make sure indexes pair with number of rows

        
            
                            for index, row in df.iterrows():    
                                tr=f'<tr><td style="max-width:200px; overflow-x:auto !important;"><a href="{row["url"]}">{row["url"] }</a></td><td>{row["title"] }</td></tr>'
                                response=response+tr
                            response=response+"</tbody></table>"
                            task_obj.clear_links()
                            os.remove(f'Temp/task-{task_obj.pk}/task-{task_obj.pk}-first_notice.csv')
                else:
                    df = pd.read_csv(nt_obj.links)
                    df.fillna(method='bfill',inplace=True)
                    df = df.reset_index()  # make sure indexes pair with number of rows


           
                    for index, row in df.iterrows():    
                        tr=f'<tr><td style="max-width:200px; overflow-x:auto !important;"><a href="{row["url"]}">{row["url"] }</a></td><td>{row["title"] }</td></tr>'
                        response=response+tr
                    response=response+"</tbody></table>"
                    task_obj.clear_links()
            except notice.DoesNotExist:
                pass
                        
                
    elif task_obj.task_type=='2':
            try:
                print(task_obj.pk)
                nt_obj=notice.objects.get(task=task_obj)
                if not os.path.exists(nt_obj.links):
                    if os.path.exists(f'Temp/task-{task_obj.pk}/image1/first_notice.csv'):
                        df = pd.read_csv(f'Temp/task-{task_obj.pk}/image1/first_notice.csv')
                        df.fillna(method='bfill',inplace=True)
                        df = df.reset_index()  # make sure indexes pair with number of rows
                        for index, row in df.iterrows():    
                            tr=f'<tr><td style="max-width:200px; overflow-x:auto !important;"><a href="{row["urls"]}">{ row["urls"] }</a></td><td>{row["type"] }</td></tr>'
                            response=response+tr
                        response=response+"</tbody></table>"
                        task_obj.set_unread_links=0
                        os.remove(f'Temp/task-{task_obj.pk}/image1/first_notice.csv')
                        task_obj.clear_links()
                    else:
                        response="<p clas='text-center'>No Data To Show</p>" 
                else:
                    print('temp and first notice')
                    df = pd.read_csv(nt_obj.links)
                    df.fillna(method='bfill',inplace=True)
                    df = df.reset_index()  # make sure indexes pair with number of rows
                    df_temp=None
                    if os.path.exists(f'Temp/task-{task_obj.pk}/image1/first_notice.csv'):
                        first_df = pd.read_csv(f'Temp/task-{task_obj.pk}/image1/first_notice.csv')
                        df_temp=pd.concat([df,first_df])
                        
                        print('concating is done')
                        print(df_temp)
                        for index, row in df_temp.iterrows():    
                            tr=f'<tr><tr><td style="max-width:200px; overflow-x:auto"><a href="{row["urls"]}">{ row["urls"] }</a></td><td>{row["type"] }</td></tr>'
                            response=response+tr
                        
                    else:
                        for index, row in df.iterrows():    
                            tr=f'<tr><tr><td><a href="{row["urls"]}">{ row["urls"] }</a></td><td>{row["type"] }</td></tr>'
                            response=response+tr

                    response=response+"</tbody></table>"
                    print('loop run successfully')
                    if os.path.exists(f'Temp/task-{task_obj.pk}/image1/first_notice.csv'):
                        os.remove(f'Temp/task-{task_obj.pk}/image1/first_notice.csv')
                    append_new_links(f'Temp/task-{id}/image1/data.csv',f'Temp/task-{id}/image1/temp.csv')
                    task_obj.clear_links()
                    print('whole code run successfully')
            except notice.DoesNotExist:
                 pass
    
    
    return JsonResponse({'response':response})