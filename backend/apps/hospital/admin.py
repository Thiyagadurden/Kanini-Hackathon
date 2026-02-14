from django.contrib import admin
from .models import HospitalResource

@admin.register(HospitalResource)
class HospitalResourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'resource_type', 'department', 'total_quantity', 'available_quantity']
    list_filter = ['resource_type', 'department']
