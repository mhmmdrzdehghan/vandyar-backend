from django.urls import path , include
from .views import TaskView , StatusView , TaskDataView
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('task', TaskView, basename='task')
router.register('status',StatusView , basename='status')


urlpatterns = [
    path('', include(router.urls)),
    # path('assignment/<int:pk>/', TaskAssignmentView.as_view()),
    # path('rate/<int:pk>/', TaskAssignmentView.as_view()),
    path('taskdata/', TaskDataView.as_view()),


]