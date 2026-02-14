from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Patient, MedicalRecord, VitalsHistory
from .serializers import PatientSerializer, PatientCreateSerializer, MedicalRecordSerializer, VitalsHistorySerializer
from .services import PatientService
from core.permissions import IsPatient, IsDoctorOrNurse, IsAdminOrManagement

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'patient':
            return Patient.objects.filter(user=user)
        elif user.role == 'doctor':
            return Patient.objects.filter(doctor_assigned__user=user)
        elif user.role == 'nurse':
            return Patient.objects.all()
        return Patient.objects.all()
    
    @action(detail=False, methods=['get'], permission_classes=[IsPatient])
    def my_profile(self, request):
        try:
            patient = Patient.objects.get(user=request.user)
            serializer = self.get_serializer(patient)
            return Response(serializer.data)
        except Patient.DoesNotExist:
            return Response({'error': 'Patient profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def medical_history(self, request, pk=None):
        patient = self.get_object()
        records = MedicalRecord.objects.filter(patient=patient)
        serializer = MedicalRecordSerializer(records, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def vitals_history(self, request, pk=None):
        patient = self.get_object()
        vitals = VitalsHistory.objects.filter(patient=patient)[:10]
        serializer = VitalsHistorySerializer(vitals, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsDoctorOrNurse])
    def update_vitals(self, request, pk=None):
        patient = self.get_object()
        service = PatientService()
        vitals = service.update_patient_vitals(patient, request.data, request.user)
        return Response(VitalsHistorySerializer(vitals).data)
    
    @action(detail=True, methods=['post'])
    def calculate_risk(self, request, pk=None):
        patient = self.get_object()
        service = PatientService()
        risk_level, risk_score = service.calculate_patient_risk(patient)
        patient.risk_level = risk_level
        patient.risk_score = risk_score
        patient.save()
        return Response({'risk_level': risk_level, 'risk_score': risk_score})

class MedicalRecordViewSet(viewsets.ModelViewSet):
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'patient':
            return MedicalRecord.objects.filter(patient__user=user)
        return MedicalRecord.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

class VitalsHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = VitalsHistory.objects.all()
    serializer_class = VitalsHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'patient':
            return VitalsHistory.objects.filter(patient__user=user)
        return VitalsHistory.objects.all()
