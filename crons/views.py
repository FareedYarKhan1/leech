from django.shortcuts import render,HttpResponse
# Create your views here.
from django_celery_beat.models import PeriodicTask,CrontabSchedule

def index(request):
    
    return HttpResponse("Done")


def schedual_task(request):
    import datetime
    now = datetime.datetime.today()
    hour=now.hour
    minute=now.minute
    runminute=minute+1
    schedual,created=CrontabSchedule.objects.get_or_create(hour=hour,minute=runminute)
    task=PeriodicTask.objects.create(crontab=schedual,name="task#"+str(minute),task='crons.tasks.test')
    
    return HttpResponse(f"Task---{task.name}-- <br> set at {hour}:{runminute} to be run")