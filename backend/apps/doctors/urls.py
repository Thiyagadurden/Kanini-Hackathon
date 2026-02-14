from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import DoctorViewSet, DoctorAvailabilityViewSet, DoctorLeaveRequestViewSet

router = DefaultRouter()
router.register(r'', DoctorViewSet, basename='doctor')
router.register(r'availability', DoctorAvailabilityViewSet, basename='doctor-availability')
router.register(r'leave-requests', DoctorLeaveRequestViewSet, basename='leave-request')

urlpatterns = router.urls
