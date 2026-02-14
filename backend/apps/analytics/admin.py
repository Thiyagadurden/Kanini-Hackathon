from django.contrib import admin
from .models import HospitalMetrics

@admin.register(HospitalMetrics)
class HospitalMetricsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_patients', 'total_appointments', 'emergency_requests']
