from django.db import models
from django.contrib.auth.models import User
from crons.tasks import scrapp_query
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
    result_file=models.URLField(max_length = 300,default=None,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        
        return str(self.task.user)+"|"+str(self.created_at)