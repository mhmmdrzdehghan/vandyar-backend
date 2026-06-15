from rest_framework.routers import DefaultRouter
from django.urls import path , include
from .views import ConversationData , TaskConversationListView , GroupConversationListView , ConversationMessagesAPIView , ConversationMemberView

urlpatterns = [
    
    path('taskConversationdata/' , TaskConversationListView.as_view()),
    path('groupConversationdata/' , GroupConversationListView.as_view()),
    path('Conversationdata/' , ConversationData.as_view()),
    path(
            "conversations/<int:conversation_id>/messages/",
            ConversationMessagesAPIView.as_view(),
            name="conversation-messages"
        ),
    path(
        "conversation/<int:conversation_id>/members/",
        ConversationMemberView.as_view(),
        name="conversation-members"
    ),    
]


