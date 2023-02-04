from celery import shared_task
from .models import task,results
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


@shared_task(bind=True)
def run_monitor(self):
    try:
        tasks=task.objects.filter(monitoring_enabled=True)
        qury=[]
        for t in tasks:
            qury.append(t.query)
            scrapp_query.delay(qury,t.pk)
            
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
    


@celery_app.task()
def scrapp_image(task_pk,image_list):
    
    urls=resolution(image_list)
    #multiple images from user
    # urls1 = [['array_main_image',['googl_link','googl_link','googl_link']],['array_main_image',['googl_link','googl_link','googl_link']]]
    #single image from user
    # urls1 = [['array_main_image',['googl_link','googl_link','googl_link']]]

    data = main(urls)
    urls=data[0]['urls']
    task_obj=task.objects.get(pk=task_pk)
    for url in urls:
        results.objects.create(task=task_obj,result_file=url)
        