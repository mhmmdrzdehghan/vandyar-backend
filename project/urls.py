from rest_framework.routers import DefaultRouter
from django.urls import path , include
from .views import ProjectView , SubProjetView , ProjectDataView , SubProjectReport , AllSubprojectReport
router = DefaultRouter()
router.register('project', ProjectView, basename='project')
router.register('subproject',SubProjetView , basename='subproject')


urlpatterns = [
    path('', include(router.urls)),
    path('projectdata/', ProjectDataView.as_view()),
    path('projectdata/<int:project_id>/', ProjectDataView.as_view()),
    path('subprojectreport/<int:subproject_id>/', SubProjectReport.as_view()),
    path('allsubprojectreport/', AllSubprojectReport.as_view()),
]