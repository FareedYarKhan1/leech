
from django.db.models.signals import pre_save, pre_delete, post_save,pre_save,post_delete
from django.dispatch import receiver, Signal

from tasks.models import task,results,notice
from tasks.tasks import scrapp_query,scrapp_image
from scrapper.functions import resolution
from leech import settings
import pandas as  pd
from .functions import compare,compareQuery
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import shutil
import os
def runTask(sender,instance,created,**kwrgs):
    if created:
        if instance.task_type=="1":
            query=[]
            query.append(instance.query)
            scrapp_query.delay(query,instance.pk)


def newLinks(sender,instance,**kwrgs):
        pass

def removeFiles(sender,instance,**kwrgs):
        
        path=f'Temp/task-{instance.pk}'
      
        if os.path.exists(path):
              shutil.rmtree(path)
              
        else:
              print('files not found')
post_save.connect(receiver=runTask,sender=task)
post_save.connect(receiver=newLinks,sender=notice)
post_delete.connect(receiver=removeFiles,sender=task)