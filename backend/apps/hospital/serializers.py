from rest_framework import serializers
from .models import HospitalResource

class HospitalResourceSerializer(serializers.ModelSerializer):
    utilization_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = HospitalResource
        fields = '__all__'
    
    def get_utilization_rate(self, obj):
        if obj.total_quantity > 0:
            return ((obj.total_quantity - obj.available_quantity) / obj.total_quantity) * 100
        return 0
