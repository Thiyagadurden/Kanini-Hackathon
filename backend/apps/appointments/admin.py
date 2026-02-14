from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['appointment_id', 'patient', 'doctor', 'appointment_date', 'status']
    list_filter = ['status', 'appointment_date']
    search_fields = ['appointment_id', 'patient__patient_id']
