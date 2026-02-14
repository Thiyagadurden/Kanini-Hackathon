from rest_framework import serializers
from .models import Prescription, PrescriptionMedicine

class PrescriptionMedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionMedicine
        fields = '__all__'

class PrescriptionSerializer(serializers.ModelSerializer):
    medicines = PrescriptionMedicineSerializer(many=True, read_only=True)
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Prescription
        fields = '__all__'
        read_only_fields = ['prescription_id', 'created_at', 'updated_at']
    
    def get_patient_name(self, obj):
        return obj.patient.user.get_full_name()
    
    def get_doctor_name(self, obj):
        return obj.doctor.user.get_full_name()
