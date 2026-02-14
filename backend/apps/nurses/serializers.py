from rest_framework import serializers
from .models import Nurse, NurseTask

class NurseSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    task_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Nurse
        fields = '__all__'
    
    def get_user_name(self, obj):
        return obj.user.get_full_name()
    
    def get_task_count(self, obj):
        return obj.tasks.filter(status__in=['pending', 'in_progress']).count()

class NurseTaskSerializer(serializers.ModelSerializer):
    nurse_name = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()
    
    class Meta:
        model = NurseTask
        fields = '__all__'
    
    def get_nurse_name(self, obj):
        return obj.nurse.user.get_full_name()
    
    def get_patient_name(self, obj):
        return obj.patient.user.get_full_name()
