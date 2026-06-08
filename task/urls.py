from django.urls import path , include
from .views import TaskView , StatusView , TaskDataView , EmergencyTask , UsersTask , TaskGroupPerson , ForwardTaskView
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('task', TaskView, basename='task')
router.register('status',StatusView , basename='status')


urlpatterns = [
    path('', include(router.urls)),
    path('taskdata/', TaskDataView.as_view()),
    path('emergencytask/' , EmergencyTask.as_view()),
    path('usertasks/' , UsersTask.as_view()),
    path('taskgroup/' , TaskGroupPerson.as_view()),
    path("tasks/<int:task_id>/forward/", ForwardTaskView.as_view()),


]