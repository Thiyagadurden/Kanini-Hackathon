from django.contrib import admin
from .models import Prescription, PrescriptionMedicine

class PrescriptionMedicineInline(admin.TabularInline):
    model = PrescriptionMedicine
    extra = 1

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['prescription_id', 'patient', 'doctor', 'created_at']
    search_fields = ['prescription_id', 'patient__patient_id']
    inlines = [PrescriptionMedicineInline]
