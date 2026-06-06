from rest_framework.routers import DefaultRouter
from django.urls import path , include
from .views import ProjectView , SubProjetView
router = DefaultRouter()
router.register('project', ProjectView, basename='project')
router.register('subproject',SubProjetView , basename='subproject')


urlpatterns = [
    path('', include(router.urls)),
]