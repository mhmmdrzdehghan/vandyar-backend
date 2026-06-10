from django.urls import path , include
from .consumers import ChatConsumer

websocket_urlpatterns =[
    path("ws/chat/<int:conversation_id>/", ChatConsumer.as_asgi()),

]