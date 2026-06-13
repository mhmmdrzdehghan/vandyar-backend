from django.urls import path , include
from .views import ListNotification

urlpatterns = [
    path('', ListNotification.as_view()),

]