from django.contrib import admin
from .models import Nurse, NurseTask

@admin.register(Nurse)
class NurseAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'shift', 'created_at']
    list_filter = ['department', 'shift']

@admin.register(NurseTask)
class NurseTaskAdmin(admin.ModelAdmin):
    list_display = ['nurse', 'patient', 'task_type', 'status', 'priority', 'due_date']
    list_filter = ['status', 'task_type', 'priority']
