from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import EmergencyRequest
from .serializers import EmergencyRequestSerializer
from .services import EmergencyService
from core.permissions import IsPatient, IsNurse, IsDoctor

class EmergencyRequestViewSet(viewsets.ModelViewSet):
    queryset = EmergencyRequest.objects.all()
    serializer_class = EmergencyRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'patient':
            return EmergencyRequest.objects.filter(patient__user=user)
        elif user.role == 'nurse':
            return EmergencyRequest.objects.filter(status__in=['nurse_notified', 'pending'])
        elif user.role == 'doctor':
            return EmergencyRequest.objects.filter(status='doctor_escalated')
        return EmergencyRequest.objects.all()
    
    @action(detail=False, methods=['post'], permission_classes=[IsPatient])
    def create_emergency(self, request):
        service = EmergencyService()
        emergency = service.create_emergency_request(
            request.user,
            request.data.get('description'),
            request.data.get('severity', 'medium')
        )
        return Response(EmergencyRequestSerializer(emergency).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[IsNurse])
    def respond(self, request, pk=None):
        emergency = self.get_object()
        service = EmergencyService()
        service.nurse_respond(emergency, request.user, request.data.get('notes'))
        return Response({'message': 'Emergency response recorded'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsNurse])
    def escalate(self, request, pk=None):
        emergency = self.get_object()
        service = EmergencyService()
        service.escalate_to_doctor(emergency, request.data.get('reason'))
        return Response({'message': 'Emergency escalated to doctor'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsDoctor])
    def resolve(self, request, pk=None):
        emergency = self.get_object()
        service = EmergencyService()
        service.resolve_emergency(emergency, request.data.get('notes'))
        return Response({'message': 'Emergency resolved'})
