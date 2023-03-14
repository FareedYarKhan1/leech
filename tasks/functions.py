import boto3
from botocore.exceptions import NoCredentialsError
import datetime
from django.contrib.auth.models import User
# import module
import pandas as pd

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import HttpResponse
from .consumers import * 

ACCESS_KEY = 'AKIAT5TA5GAZOLYT4SNY'
SECRET_KEY = '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'
BUKET_NAME= "searchimagesscraper"



'''
A function upload the local generated label pdf to aws s3 buket
:param filename str: local label pdf file path
.
.
.
:return str : url of uploaded file on s3

'''
def upload_to_aws(local_filename,file_name):
    
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)

    try:
        folder="scrappingResult/"
        s3.upload_file(local_filename,BUKET_NAME, folder+file_name)
        url=f"https://{BUKET_NAME}.s3.amazonaws.com/{folder}{file_name}"
        return url
    except FileNotFoundError:
        
        return False
    except NoCredentialsError:
     
        return False


def compare(old_file,new_file):
  response=False
  old_file_df = pd.read_csv(old_file)
  new_file_df = pd.read_csv(new_file)
  new_similer=[]
  old_similer=[]
  new_exact=[]
  old_exact=[]
  # count no. of lines
  print(str(len(new_file_df)))
  print(str(len(old_file_df)))
  if len(new_file_df) != len(old_file_df):
    
    for index, new_url in new_file_df.iterrows():
      new_similer_link=new_url['Similar_imgs_links']
      new_exact_link=new_url['Exact_imgs_links']
      new_similer.append(new_similer_link)
      new_exact.append(new_exact_link)


    for index, new_url in old_file_df.iterrows():
      old_similer_link=new_url['Similar_imgs_links']
      old_exact_link=new_url['Exact_imgs_links']
      old_similer.append(old_similer_link)
      old_exact.append(old_exact_link)

    
    
    new_similer_final=[]
    new_exact_final=[]
    similer_lis='<h2 class="text-center text-success">Similer Links</h2>'
    exact_lis='<br><br><h2 class="text-center text-success">Exact Links</h2>'
    for item in new_similer:
      if item not in old_similer:
          if str(item) != 'nan':
            item=f'<a href="{item}">{str(item)[0:200]}...</a>'
            similer_lis=similer_lis+f'<li>{item}</li>'
            new_similer_final.append(item)
    

    for item in new_exact:
      if item not in old_exact:
            if str(type(item)) =="<class 'float'>":
                    pass
            else:
              item=f'<a href="{item}">{str(item)[0:200]}...</a>'
              exact_lis=exact_lis+f'<li>{item}</li>'
              new_exact_final.append(item)
    full_respons=f'<ol>{similer_lis} {exact_lis}</ol>'
    total_links=len(new_exact_final)+len(new_similer_final)
    response={'full_respons':full_respons,'total_links':total_links}
  else:
      response=False
  return response 



def compareQuery(old_file,new_file):
  response=False
  old_file_df = pd.read_csv(old_file)
  new_file_df = pd.read_csv(new_file)
  new_links=[]
  old_links=[]
 
 
  if len(new_file_df) != len(old_file_df):
    
    for index, new_url in new_file_df.iterrows():
      new_link=new_url['url']
      
      new_links.append(new_link)


    for index, new_url in old_file_df.iterrows():
      old_link=new_url['url']
      
      old_links.append(old_link)

    
    
    new_links_final=[]
    
    new_lis='<h2 class="text-center text-success">NEW URLS</h2>'
    
    for item in new_links:
      if item not in old_links:
          if str(item) != 'nan':
            item=f'<a href="{item}">{str(item)[0:200]}...</a>'
            new_lis=new_lis+f'<li>{item}</li>'
            new_links_final.append(item)
    
    full_respons=f'<ol>{new_lis}</ol>'
    total_links=len(new_links_final)
    response={'full_respons':full_respons,'total_links':total_links}
  else:
      response=False
  return response 
    
    
    
       