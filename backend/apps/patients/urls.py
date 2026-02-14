from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, MedicalRecordViewSet, VitalsHistoryViewSet

router = DefaultRouter()
router.register(r'', PatientViewSet, basename='patient')
router.register(r'records', MedicalRecordViewSet, basename='medical-record')
router.register(r'vitals', VitalsHistoryViewSet, basename='vitals-history')

urlpatterns = router.urls
