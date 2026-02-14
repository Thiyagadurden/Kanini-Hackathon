from django.contrib import admin
from .models import EmergencyRequest

@admin.register(EmergencyRequest)
class EmergencyRequestAdmin(admin.ModelAdmin):
    list_display = ['patient', 'status', 'severity', 'nurse', 'doctor', 'created_at']
    list_filter = ['status', 'severity', 'created_at']
    search_fields = ['patient__patient_id']
