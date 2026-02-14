from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Appointment
from .serializers import AppointmentSerializer
from core.permissions import IsPatient, IsDoctor

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'patient':
            return Appointment.objects.filter(patient__user=user)
        elif user.role == 'doctor':
            return Appointment.objects.filter(doctor__user=user)
        return Appointment.objects.all()
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        appointment.status = 'cancelled'
        appointment.save()
        return Response({'message': 'Appointment cancelled'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsDoctor])
    def complete(self, request, pk=None):
        appointment = self.get_object()
        appointment.status = 'completed'
        appointment.notes = request.data.get('notes', appointment.notes)
        appointment.save()
        return Response({'message': 'Appointment completed'})
