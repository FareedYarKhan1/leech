from bs4 import *
import pickle
import concurrent.futures
import time,datetime
import os,cv2
import pandas as pd

import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from datetime import datetime
import concurrent.futures
import boto3
from botocore.exceptions import NoCredentialsError
import datetime
from bs4 import *
import pickle
import concurrent.futures
import time,datetime
import os,cv2
from .download import Downloading
import requests
import shutil
import requests
from bs4 import BeautifulSoup
import re
from urllib.request import urlopen
import requests
import random
import time
import json
import pandas as pd
# Import the Images module from pillow
from PIL import Image
import os
import datetime
from pathlib import Path
import shutil
from tasks.models import notice,task,results
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer



ACCESS_KEY = 'AKIAT5TA5GAZOLYT4SNY'
SECRET_KEY = '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'
BUKET_NAME= "searchimagesscraper"

def upload_images_on_aws(local_filename):
    
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)

    try:
        
        folder="scrappingImages/"
        
        s3.upload_file(local_filename,BUKET_NAME, folder+local_filename)
        url=f"https://{BUKET_NAME}.s3.amazonaws.com/{folder}{local_filename}"
        return url
    except FileNotFoundError:
        
        return False
    except NoCredentialsError:
       
        return False
    
    
# Open the image by specifying the image path.
def resolution(image_list):
    main_response=[]
    
    resoluion = [30,60]
    date=datetime.datetime.now().strftime("%H_%M_%S_%Y_%m_%d")
    folder_name ="Temp/uploads/users/"+date+"/"
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
    count = 0
    for img in range(len(image_list)):
        inner_response=[]
        read = image_list[img]
        image_file = Image.open(read)
        name = Path(read).name.split('.')[0]
        
        # Path(read).suffix
        
        if image_file.mode in ("RGBA", "P"):
            image_file = image_file.convert("RGB")


        #making dir
        image_path = folder_name+str(count)+"/"
        if not os.path.exists(image_path):
            os.mkdir(image_path)

        #copy main image to dir
        copy_main_img = Path(read).name
        copy_path = os.path.join(image_path,copy_main_img)
        shutil.copyfile(read, copy_path) 
        data=cv2.imread(copy_path)
        main_image_link=upload_images_on_aws(copy_path)
        inner_response.append(data)
        link_array=[]
        main_link=f'https://lens.google.com/uploadbyurl?url={main_image_link}'
        link_array.append(main_link)
        for re in resoluion:
            
            new_name = f'{name}_'+str(re)+'.jpg'
            sav_path =image_path+new_name
            image_file.save(sav_path, quality=re)
            resp=upload_images_on_aws(sav_path)
            link=f'https://lens.google.com/uploadbyurl?url={resp}'
            link_array.append(link)
        inner_response.append(link_array)
        count+=1
        main_response.append(inner_response)
    return(main_response)



def send_first_notice(data_csv_address,temp_csv_address,task_pk,link_length):
     task_obj=task.objects.get(pk=task_pk)
     results.objects.create(task=task_obj,result_file=data_csv_address)
     try:
        not_obj=notice.objects.get(task=task_obj)
     except notice.DoesNotExist:
        notice.objects.create(task=task_obj,links=temp_csv_address,unread_links=link_length)
        
     channel_layer=get_channel_layer()
     
     async_to_sync(channel_layer.group_send)(
            'client_'+str(task_obj.user.username),{'type':'send_notification','message':link_length,'task':task_obj.pk}
                    )      
     
def send_created_temp_csv(temp_csv_address,task_pk,links_length):
    
                try:
                    task_obj=task.objects.get(pk=task_pk) 
                    try:
                        not_obj=notice.objects.get(task=task_obj)
                        not_obj.unread_links=links_length+not_obj.unread_links
                        not_obj.save()
                    except notice.DoesNotExist:
                        not_obj=notice.objects.create(task=task_obj,links=temp_csv_address,unread_links=links_length)

                    channel_layer=get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                    'client_'+str(task_obj.user.username),{'type':'send_notification','message':not_obj.unread_links,'task':task_obj.pk}
                    )
                    print("+++++++++++++++++++++++ TRY OF SAVING temp.csv ++++++++++++++++++++++++++++++++")
                except task.DoesNotExist:
                    print("+++++++++++++++++++++++ EXCEPT OF SAVING temp.csv ++++++++++++++++++++++++++++++++")


def send_normal_notice(temp_csv_address,task_pk,links_length):
    try:
        
        task_obj=task.objects.get(pk=task_pk)
        try:
            not_obj=notice.objects.get(task=task_obj)
            not_obj.unread_links=links_length+not_obj.unread_links
            not_obj.save()
        except notice.DoesNotExist:
            not_obj=notice.objects.create(task=task_obj,links=temp_csv_address,unread_links=links_length)
                            
        channel_layer=get_channel_layer()
                       
        async_to_sync(channel_layer.group_send)(
        'client_'+str(task_obj.user.username),{'type':'send_notification','message':not_obj.unread_links,'task':task_obj.pk}
        )
        print("+++++++++++++++++++++++ TRY OF DF3 ++++++++++++++++++++++++++++++++")
    except task.DoesNotExist:
            print("+++++++++++++++++++++++ EXCEPT OF DF3 ++++++++++++++++++++++++++++++++")