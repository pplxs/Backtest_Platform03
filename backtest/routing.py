
from django.urls import path
from .consumers import MyConsumer

websocket_urlpatterns = [
    path('ws/myconsumer/', MyConsumer.as_asgi()),
]