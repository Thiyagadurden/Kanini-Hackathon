from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import HospitalMetrics
from .serializers import HospitalMetricsSerializer
from .services import AnalyticsService
from core.permissions import IsAdminOrManagement

class AnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HospitalMetrics.objects.all()
    serializer_class = HospitalMetricsSerializer
    permission_classes = [IsAuthenticated, IsAdminOrManagement]
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        service = AnalyticsService()
        data = service.get_dashboard_metrics()
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def patient_statistics(self, request):
        service = AnalyticsService()
        data = service.get_patient_statistics()
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def doctor_performance(self, request):
        service = AnalyticsService()
        data = service.get_doctor_performance()
        return Response(data)
