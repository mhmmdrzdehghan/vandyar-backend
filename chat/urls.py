from rest_framework.routers import DefaultRouter
from django.urls import path , include
from .views import MessageView 

urlpatterns = [
    path(
        'conversations/<int:conversation_id>/messages/',
        MessageView.as_view({'get': 'list', 'post': 'create'}),
    ),
]
