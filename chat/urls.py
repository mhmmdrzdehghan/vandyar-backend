from rest_framework.routers import DefaultRouter
from django.urls import path , include
from .views import MessageView , ConversationData

urlpatterns = [
    path(
        'messages/<int:conversation_id>/',
        MessageView.as_view({'get': 'list', 'post': 'create'}),
    ),

    path('Conversationdata/' , ConversationData.as_view()),

]


