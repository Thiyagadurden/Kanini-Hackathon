from rest_framework.routers import DefaultRouter
from .views import PrescriptionViewSet, PrescriptionMedicineViewSet

router = DefaultRouter()
router.register(r'', PrescriptionViewSet, basename='prescription')
router.register(r'medicines', PrescriptionMedicineViewSet, basename='prescription-medicine')

urlpatterns = router.urls
