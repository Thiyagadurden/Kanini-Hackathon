from django.contrib import admin
from .models import Patient, MedicalRecord, VitalsHistory

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_id', 'user', 'age', 'gender', 'risk_level', 'doctor_assigned', 'created_at']
    list_filter = ['risk_level', 'gender', 'visit_type']
    search_fields = ['patient_id', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['patient_id', 'created_at', 'updated_at']

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'record_type', 'uploaded_by', 'created_at']
    list_filter = ['record_type', 'created_at']
    search_fields = ['patient__patient_id']

@admin.register(VitalsHistory)
class VitalsHistoryAdmin(admin.ModelAdmin):
    list_display = ['patient', 'blood_pressure_systolic', 'heart_rate', 'temperature', 'spo2', 'recorded_at']
    list_filter = ['recorded_at']
    search_fields = ['patient__patient_id']
