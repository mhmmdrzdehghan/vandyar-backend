from django.urls import path , include
from .views import( TaskView , StatusView , TaskDataView , EmergencyTask ,
     UsersTask , TaskGroupPerson , ForwardTaskView ,TaskGroupDefined , TaskGroupPersonByUserid,
     TaskPriortyAnalysis , TaskGRoupAnalysis)
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
    path("forward/<int:task_id>/", ForwardTaskView.as_view()),
    path("taskgroupdefined/<int:chat_id>/",TaskGroupDefined.as_view(),name="taskgroupdefined"),
    path("taskgroup/<int:user_id>/",TaskGroupPersonByUserid.as_view()),
    path("priorty-analysis/<int:user_id>/",TaskPriortyAnalysis.as_view()),
    path("group-analysis/<int:user_id>/",TaskGRoupAnalysis.as_view()),

]