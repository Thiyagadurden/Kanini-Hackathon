from django.db import models
from django.conf import settings

class Nurse(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='nurse_profile')
    license_number = models.CharField(max_length=100, unique=True)
    department = models.CharField(max_length=100)
    shift = models.CharField(max_length=20, choices=(('day', 'Day'), ('night', 'Night')))
    years_of_experience = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'nurses'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.department}"

class NurseTask(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    TASK_TYPE_CHOICES = (
        ('medicine_delivery', 'Medicine Delivery'),
        ('vitals_check', 'Vitals Check'),
        ('patient_care', 'Patient Care'),
        ('emergency_response', 'Emergency Response'),
    )
    
    nurse = models.ForeignKey(Nurse, on_delete=models.CASCADE, related_name='tasks')
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE)
    task_type = models.CharField(max_length=50, choices=TASK_TYPE_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.IntegerField(default=1, help_text="1=Low, 5=High")
    due_date = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'nurse_tasks'
        ordering = ['-priority', 'due_date']
    
    def __str__(self):
        return f"{self.nurse.user.get_full_name()} - {self.task_type} - {self.patient.patient_id}"
