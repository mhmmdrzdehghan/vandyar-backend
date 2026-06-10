from rest_framework.routers import DefaultRouter
from django.urls import path , include
from .views import ConversationData , TaskConversationListView , GroupConversationListView

urlpatterns = [
    
    path('taskConversationdata/' , TaskConversationListView.as_view()),
    path('groupConversationdata/' , GroupConversationListView.as_view()),
    path('Conversationdata/' , ConversationData.as_view()),

]


