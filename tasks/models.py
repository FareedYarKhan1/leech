from django.db import models
from django.contrib.auth.models import User
from crons.tasks import scrapp_query
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import pandas as pd
from .consumers import * 
# Create your models here.

# iterable
task_type =(
    ("1", "Keyword Search"),
    ("2", "Image Search"),
    
)
  
class task(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    task_type=models.CharField(choices=task_type, default='1', max_length=20)
    query=models.TextField(default=None,null=True,blank=True)
    search_image=models.ImageField(upload_to="query_images/",default=None,null=True,blank=True)
    monitoring_enabled=models.BooleanField(default=True)
    timestamp=models.DateTimeField(auto_now_add=True)
    @property
    def get_unread_links(self):
         counter=0
         try:
              notice_obj=notice.objects.get(task=self)
              
              counter=notice_obj.unread_links
         except:
             pass
         return counter  
    def set_unread_links(self,links):
         
         try:
              notice_obj=notice.objects.get(task=self)
              
              old=notice_obj.unread_links
              whole=old+links
              notice_obj.unread_links=whole
              notice_obj.save()
         except:
             pass
    def clear_links(self):
         
         try:
              notice_obj=notice.objects.get(task=self)
              
              notice_obj.unread_links=0
              notice_obj.save()
         except:
             pass
         
            
    def __str__(self):
        
        if self.task_type=="1":
             return str(self.user)+"|"+str(self.timestamp)+"|"+"Query Search"
        elif self.task_type=="2":
             return str(self.user)+"|"+str(self.timestamp)+"|"+"Image Search"
    def save(self, **kwargs):
        return super().save()


class task_images(models.Model):
    task=models.ForeignKey(task,on_delete=models.CASCADE)
    picture=models.ImageField(upload_to="query_images/")

   
class results(models.Model):
    task=models.ForeignKey(task,on_delete=models.CASCADE)
    is_completed=models.BooleanField(default=False)
    result_file=models.TextField(default=None,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        
        return str(self.task.user)+"|"+str(self.created_at)
    def save(self,**kwargs):
            return super().save()
        
class notice(models.Model):
    task=models.OneToOneField(task,on_delete=models.CASCADE)
    links=models.TextField(default='')
    unread_links=models.BigIntegerField(default=0)
    is_seen=models.BooleanField(default=False)

    def save(self,**kwargs):
            
            return super().save()