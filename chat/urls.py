from rest_framework.routers import DefaultRouter
from django.urls import path , include
from .views import ConversationData , TaskConversationListView , GroupConversationListView , ConversationMessagesAPIView

urlpatterns = [
    
    path('taskConversationdata/' , TaskConversationListView.as_view()),
    path('groupConversationdata/' , GroupConversationListView.as_view()),
    path('Conversationdata/' , ConversationData.as_view()),
    path(
            "conversations/<int:conversation_id>/messages/",
            ConversationMessagesAPIView.as_view(),
            name="conversation-messages"
        ),


]


