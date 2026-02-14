from django.contrib import admin
from .models import Doctor, DoctorAvailability, DoctorLeaveRequest

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'department', 'availability_status']
    list_filter = ['specialization', 'availability_status']
    search_fields = ['user__email', 'license_number']

@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'day_of_week', 'start_time', 'end_time', 'is_active']
    list_filter = ['day_of_week', 'is_active']

@admin.register(DoctorLeaveRequest)
class DoctorLeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'start_date', 'end_date', 'status', 'created_at']
    list_filter = ['status', 'created_at']
