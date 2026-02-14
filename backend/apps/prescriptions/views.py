from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Prescription, PrescriptionMedicine
from .serializers import PrescriptionSerializer, PrescriptionMedicineSerializer
from core.permissions import IsDoctor

class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'patient':
            return Prescription.objects.filter(patient__user=user)
        elif user.role == 'doctor':
            return Prescription.objects.filter(doctor__user=user)
        return Prescription.objects.all()
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsDoctor()]
        return super().get_permissions()

class PrescriptionMedicineViewSet(viewsets.ModelViewSet):
    queryset = PrescriptionMedicine.objects.all()
    serializer_class = PrescriptionMedicineSerializer
    permission_classes = [IsAuthenticated, IsDoctor]
