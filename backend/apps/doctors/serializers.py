from rest_framework import serializers
from .models import Doctor, DoctorAvailability, DoctorLeaveRequest
from apps.users.serializers import UserSerializer

class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    patient_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Doctor
        fields = '__all__'
    
    def get_patient_count(self, obj):
        return obj.patients.count()

class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorAvailability
        fields = '__all__'

class DoctorLeaveRequestSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = DoctorLeaveRequest
        fields = '__all__'
        read_only_fields = ['approved_by', 'created_at', 'updated_at']
    
    def get_doctor_name(self, obj):
        return obj.doctor.user.get_full_name()
    
    def get_approved_by_name(self, obj):
        if obj.approved_by:
            return obj.approved_by.get_full_name()
        return None
