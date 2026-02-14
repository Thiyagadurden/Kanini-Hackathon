from rest_framework import serializers
from .models import Appointment

class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['appointment_id', 'created_at', 'updated_at']
    
    def get_patient_name(self, obj):
        return obj.patient.user.get_full_name()
    
    def get_doctor_name(self, obj):
        return obj.doctor.user.get_full_name()
