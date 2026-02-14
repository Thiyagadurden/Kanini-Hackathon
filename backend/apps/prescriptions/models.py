from django.db import models
from core.utils import generate_prescription_id

class Prescription(models.Model):
    prescription_id = models.CharField(max_length=20, unique=True, editable=False)
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey('doctors.Doctor', on_delete=models.CASCADE, related_name='prescriptions')
    diagnosis = models.TextField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'prescriptions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.prescription_id} - {self.patient.patient_id}"
    
    def save(self, *args, **kwargs):
        if not self.prescription_id:
            self.prescription_id = generate_prescription_id()
        super().save(*args, **kwargs)

class PrescriptionMedicine(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='medicines')
    medicine_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration_days = models.IntegerField()
    instructions = models.TextField(blank=True)
    
    class Meta:
        db_table = 'prescription_medicines'
    
    def __str__(self):
        return f"{self.medicine_name} - {self.dosage}"
