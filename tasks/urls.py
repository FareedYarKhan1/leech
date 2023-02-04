
from django.urls import path 
from .views import upload,add_task,uploadView,view_task

urlpatterns = [

    path('',upload,name="devide_images"),
    path('upload',uploadView,name="upload"),
    path('add_task',add_task,name="submit_task"),
    path('view_task',view_task,name="view_task"),
]
