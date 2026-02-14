from rest_framework import serializers
from .models import EmergencyRequest

class EmergencyRequestSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    nurse_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    
    class Meta:
        model = EmergencyRequest
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_patient_name(self, obj):
        return obj.patient.user.get_full_name()
    
    def get_nurse_name(self, obj):
        return obj.nurse.user.get_full_name() if obj.nurse else None
    
    def get_doctor_name(self, obj):
        return obj.doctor.user.get_full_name() if obj.doctor else None
