from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Doctor, DoctorAvailability, DoctorLeaveRequest
from .serializers import DoctorSerializer, DoctorAvailabilitySerializer, DoctorLeaveRequestSerializer
from .services import DoctorService
from core.permissions import IsDoctor, IsAdmin, IsAdminOrManagement

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], permission_classes=[IsDoctor])
    def my_profile(self, request):
        try:
            doctor = Doctor.objects.get(user=request.user)
            serializer = self.get_serializer(doctor)
            return Response(serializer.data)
        except Doctor.DoesNotExist:
            return Response({'error': 'Doctor profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'], permission_classes=[IsDoctor])
    def toggle_availability(self, request, pk=None):
        doctor = self.get_object()
        if doctor.user != request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        new_status = request.data.get('status')
        if new_status not in ['available', 'unavailable']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        service = DoctorService()
        result = service.request_availability_change(doctor, new_status, request.data.get('reason'))
        return Response(result)
    
    @action(detail=True, methods=['get'])
    def patients(self, request, pk=None):
        doctor = self.get_object()
        from apps.patients.serializers import PatientSerializer
        patients = doctor.patients.all()
        serializer = PatientSerializer(patients, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def schedule(self, request, pk=None):
        doctor = self.get_object()
        availability = DoctorAvailability.objects.filter(doctor=doctor, is_active=True)
        serializer = DoctorAvailabilitySerializer(availability, many=True)
        return Response(serializer.data)

class DoctorAvailabilityViewSet(viewsets.ModelViewSet):
    queryset = DoctorAvailability.objects.all()
    serializer_class = DoctorAvailabilitySerializer
    permission_classes = [IsAuthenticated]

class DoctorLeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = DoctorLeaveRequest.objects.all()
    serializer_class = DoctorLeaveRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'doctor':
            return DoctorLeaveRequest.objects.filter(doctor__user=user)
        return DoctorLeaveRequest.objects.all()
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def approve(self, request, pk=None):
        leave_request = self.get_object()
        service = DoctorService()
        result = service.approve_leave_request(leave_request, request.user)
        return Response(result)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def reject(self, request, pk=None):
        leave_request = self.get_object()
        leave_request.status = 'rejected'
        leave_request.approved_by = request.user
        leave_request.save()
        return Response({'message': 'Leave request rejected'})
