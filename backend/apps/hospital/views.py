from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import HospitalResource
from .serializers import HospitalResourceSerializer
from core.permissions import IsAdmin, IsAdminOrManagement

class HospitalResourceViewSet(viewsets.ModelViewSet):
    queryset = HospitalResource.objects.all()
    serializer_class = HospitalResourceSerializer
    permission_classes = [IsAuthenticated, IsAdminOrManagement]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated(), IsAdminOrManagement()]
        return [IsAuthenticated(), IsAdmin()]
