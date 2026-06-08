from django.urls import path , include
from .views import TaskView , StatusView , TaskDataView , EmergencyTask , UsersTask
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('task', TaskView, basename='task')
router.register('status',StatusView , basename='status')


urlpatterns = [
    path('', include(router.urls)),
    path('taskdata/', TaskDataView.as_view()),
    path('emergencytask/' , EmergencyTask.as_view()),
    path('usertasks/' , UsersTask.as_view()),

]