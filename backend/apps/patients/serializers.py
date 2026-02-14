from rest_framework import serializers
from .models import Patient, MedicalRecord, VitalsHistory
from apps.users.serializers import UserSerializer

class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    doctor_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['patient_id', 'created_at', 'updated_at', 'risk_score']
    
    def get_doctor_name(self, obj):
        if obj.doctor_assigned:
            return obj.doctor_assigned.user.get_full_name()
        return None

class PatientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        exclude = ['patient_id', 'created_at', 'updated_at']

class MedicalRecordSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = MedicalRecord
        fields = '__all__'
        read_only_fields = ['created_at']
    
    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by:
            return obj.uploaded_by.get_full_name()
        return None

class VitalsHistorySerializer(serializers.ModelSerializer):
    recorded_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = VitalsHistory
        fields = '__all__'
        read_only_fields = ['recorded_at']
    
    def get_recorded_by_name(self, obj):
        if obj.recorded_by:
            return obj.recorded_by.get_full_name()
        return None
