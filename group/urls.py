from rest_framework.routers import DefaultRouter
from .views import GroupViewSet

router = DefaultRouter()
router.register('group', GroupViewSet, basename='group')

urlpatterns = router.urls