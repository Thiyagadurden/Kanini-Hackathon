from rest_framework.routers import DefaultRouter
from .views import EmergencyRequestViewSet

router = DefaultRouter()
router.register(r'', EmergencyRequestViewSet, basename='emergency')

urlpatterns = router.urls
