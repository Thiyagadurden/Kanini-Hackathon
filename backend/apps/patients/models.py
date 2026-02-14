from django.db import models
from django.conf import settings
from core.utils import generate_patient_id
from core.validators import validate_blood_pressure, validate_heart_rate, validate_temperature, validate_spo2

class Patient(models.Model):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    
    RISK_LEVEL_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    
    VISIT_TYPE_CHOICES = (
        ('emergency', 'Emergency'),
        ('outpatient', 'Outpatient'),
        ('inpatient', 'Inpatient'),
        ('followup', 'Follow-up'),
    )
    
    patient_id = models.CharField(max_length=20, unique=True, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile')
    
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    
    blood_pressure_systolic = models.IntegerField(null=True, blank=True)
    blood_pressure_diastolic = models.IntegerField(null=True, blank=True)
    heart_rate = models.IntegerField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    spo2 = models.IntegerField(null=True, blank=True)
    
    symptom_chest_pain = models.BooleanField(default=False)
    symptom_fever = models.BooleanField(default=False)
    symptom_cough = models.BooleanField(default=False)
    symptom_breathing_difficulty = models.BooleanField(default=False)
    symptom_headache = models.BooleanField(default=False)
    symptom_dizziness = models.BooleanField(default=False)
    symptom_vomiting = models.BooleanField(default=False)
    
    diabetes = models.BooleanField(default=False)
    hypertension = models.BooleanField(default=False)
    heart_disease = models.BooleanField(default=False)
    asthma = models.BooleanField(default=False)
    pregnant = models.BooleanField(default=False)
    smoker = models.BooleanField(default=False)
    
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, default='low')
    risk_score = models.IntegerField(default=0)
    
    doctor_assigned = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patients'
    )
    
    department = models.CharField(max_length=100, blank=True)
    hospital_clinic_id = models.CharField(max_length=100, blank=True)
    visit_type = models.CharField(max_length=20, choices=VISIT_TYPE_CHOICES, default='outpatient')
    insurance_provider = models.CharField(max_length=200, blank=True)
    
    last_checkup_date = models.DateField(null=True, blank=True)
    next_appointment_date = models.DateField(null=True, blank=True)
    
    pain_level = models.IntegerField(default=0, help_text="Pain level from 0-10")
    recent_diagnosis = models.TextField(blank=True)
    chronic_disease_history = models.TextField(blank=True)
    family_medical_history = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'patients'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.patient_id} - {self.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.patient_id:
            self.patient_id = generate_patient_id()
        super().save(*args, **kwargs)

class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    record_type = models.CharField(max_length=100)
    description = models.TextField()
    file = models.FileField(upload_to='medical_records/', null=True, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'medical_records'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.patient.patient_id} - {self.record_type}"

class VitalsHistory(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='vitals_history')
    blood_pressure_systolic = models.IntegerField()
    blood_pressure_diastolic = models.IntegerField()
    heart_rate = models.IntegerField()
    temperature = models.FloatField()
    spo2 = models.IntegerField()
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'vitals_history'
        ordering = ['-recorded_at']
    
    def __str__(self):
        return f"{self.patient.patient_id} - {self.recorded_at}"
