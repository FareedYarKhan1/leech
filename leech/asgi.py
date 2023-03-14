# core/asgi.py

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path, re_path
from tasks.consumers import *
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

websocket_urlpatterns = [
    re_path(r'ws/connect/(?P<room_name>\w+)/$',  MyConsumer.as_asgi())
]

application = ProtocolTypeRouter({
  'http': get_asgi_application(),
  'websocket': URLRouter(
      websocket_urlpatterns
    ),
})
