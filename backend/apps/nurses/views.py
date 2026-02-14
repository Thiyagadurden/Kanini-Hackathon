from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Nurse, NurseTask
from .serializers import NurseSerializer, NurseTaskSerializer
from core.permissions import IsNurse, IsAdminOrManagement

class NurseViewSet(viewsets.ModelViewSet):
    queryset = Nurse.objects.all()
    serializer_class = NurseSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], permission_classes=[IsNurse])
    def my_profile(self, request):
        try:
            nurse = Nurse.objects.get(user=request.user)
            serializer = self.get_serializer(nurse)
            return Response(serializer.data)
        except Nurse.DoesNotExist:
            return Response({'error': 'Nurse profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        nurse = self.get_object()
        tasks = NurseTask.objects.filter(nurse=nurse)
        status_filter = request.query_params.get('status')
        if status_filter:
            tasks = tasks.filter(status=status_filter)
        serializer = NurseTaskSerializer(tasks, many=True)
        return Response(serializer.data)

class NurseTaskViewSet(viewsets.ModelViewSet):
    queryset = NurseTask.objects.all()
    serializer_class = NurseTaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'nurse':
            return NurseTask.objects.filter(nurse__user=user)
        return NurseTask.objects.all()
    
    @action(detail=True, methods=['post'], permission_classes=[IsNurse])
    def complete(self, request, pk=None):
        task = self.get_object()
        from django.utils import timezone
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.notes = request.data.get('notes', task.notes)
        task.save()
        return Response({'message': 'Task marked as completed'})
