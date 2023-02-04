
from django.db.models.signals import pre_save, pre_delete, post_save
from django.dispatch import receiver, Signal

from tasks.models import task,results
from tasks.tasks import scrapp_query,scrapp_image
from scrapper.functions import resolution
from leech import settings
def runTask(sender,instance,created,**kwrgs):
    if created:
        if instance.task_type=="1":
            query=[]
            query.append(instance.query)
            scrapp_query.delay(query,instance.pk)
  
    
post_save.connect(receiver=runTask,sender=task)
