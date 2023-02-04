from celery import shared_task
from scrapper.functions import main_runner
from leech import celery_app
from django.apps import apps
from django.apps import apps


@celery_app.task()
def scrapp_query(query,task):
    filename=main_runner(query,task)
    