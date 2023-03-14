from celery import shared_task
from .models import task,results,notice
from scrapper.functions_v2 import resolution
from scrapper.functions import main_runner
from scrapper.functions_v3 import main
from leech import celery_app
from bs4 import *
import pickle
import concurrent.futures
import time,datetime
import os,cv2
from scrapper.download import Downloading

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
# importing modules
import urllib.request
import pandas as pd


@shared_task(bind=True)
def run_monitor(self):
    try:
        tasks=task.objects.filter(monitoring_enabled=True)
        qury=[]
        image_list=[]
        for t in tasks:
            if t.monitoring_enabled:
                if t.task_type=='1':
                    qury.append(t.query)
                    scrapp_query.delay(qury,t.pk)
                    qury.clear()
                elif t.task_type=='2':
               
                    image_url=t.search_image.url
                    image_name=t.search_image.name
                    local_path="Temp/saved_img_temp/"+image_name
                    urllib.request.urlretrieve(image_url,local_path)
                    image_list.append(local_path)
                    scrapp_image.delay(t.pk,image_list)
                    image_list.clear()
                    
    except task.DoesNotExist:
        pass
    


@celery_app.task()
def scrapp_query(query,task_pk):
    task_obj=task.objects.get(pk=task_pk)
    filename=main_runner(query,task_pk)
    if filename == False:
        pass
    else:
        results.objects.create(task=task_obj,result_file=filename)
        task_obj=task.objects.get(pk=task_pk)
        df=pd.read_csv(filename)
        try:
            not_obj=notice.objects.get(task=task_obj)
        except notice.DoesNotExist:
            
            not_obj=notice.objects.create(task=task_obj,links=f'Temp/task-{task_obj.pk}/temp.csv',unread_links=len(df))
       
        channel_layer=get_channel_layer()
        async_to_sync(channel_layer.group_send)(
        'client_'+str(task_obj.user.username),{'type':'send_notification','message':not_obj.unread_links,'task':task_obj.pk}
                )
    


@celery_app.task()
def scrapp_image(task_pk,image_list):
    
    urls=resolution(image_list)
    #multiple images from user
    # urls1 = [['array_main_image',['googl_link','googl_link','googl_link']],['array_main_image',['googl_link','googl_link','googl_link']]]
    #single image from user
    # urls1 = [['array_main_image',['googl_link','googl_link','googl_link']]]

    data = main(urls,task_pk)
    
   