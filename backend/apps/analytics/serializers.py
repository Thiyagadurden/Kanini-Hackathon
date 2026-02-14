from rest_framework import serializers
from .models import HospitalMetrics

class HospitalMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalMetrics
        fields = '__all__'
