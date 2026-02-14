from rest_framework.routers import DefaultRouter
from .views import HospitalResourceViewSet

router = DefaultRouter()
router.register(r'resources', HospitalResourceViewSet, basename='hospital-resource')

urlpatterns = router.urls
