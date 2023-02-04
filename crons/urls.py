from django.contrib import admin
from django.urls import path , include
from . import views
urlpatterns = [
    
    path('',views.index,name="home"),
    path('sc',views.schedual_task,name="schedual"),
]