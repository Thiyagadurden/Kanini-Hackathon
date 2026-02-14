from django.db import models

class EmergencyRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('nurse_notified', 'Nurse Notified'),
        ('nurse_responded', 'Nurse Responded'),
        ('doctor_escalated', 'Doctor Escalated'),
        ('resolved', 'Resolved'),
        ('cancelled', 'Cancelled'),
    )
    
    SEVERITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='emergency_requests')
    nurse = models.ForeignKey('nurses.Nurse', on_delete=models.SET_NULL, null=True, blank=True, related_name='emergency_requests')
    doctor = models.ForeignKey('doctors.Doctor', on_delete=models.SET_NULL, null=True, blank=True, related_name='emergency_requests')
    
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    
    nurse_notified_at = models.DateTimeField(null=True, blank=True)
    nurse_responded_at = models.DateTimeField(null=True, blank=True)
    doctor_notified_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    response_notes = models.TextField(blank=True)
    escalation_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'emergency_requests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Emergency - {self.patient.patient_id} - {self.status}"
