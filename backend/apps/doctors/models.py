from django.db import models
from django.conf import settings

class Doctor(models.Model):
    SPECIALIZATION_CHOICES = (
        ('general', 'General Physician'),
        ('cardiology', 'Cardiology'),
        ('neurology', 'Neurology'),
        ('orthopedics', 'Orthopedics'),
        ('pediatrics', 'Pediatrics'),
        ('emergency', 'Emergency Medicine'),
    )
    
    AVAILABILITY_STATUS = (
        ('available', 'Available'),
        ('unavailable', 'Unavailable'),
        ('on_leave', 'On Leave'),
    )
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile')
    license_number = models.CharField(max_length=100, unique=True)
    specialization = models.CharField(max_length=100, choices=SPECIALIZATION_CHOICES)
    department = models.CharField(max_length=100)
    years_of_experience = models.IntegerField()
    qualification = models.TextField()
    availability_status = models.CharField(max_length=20, choices=AVAILABILITY_STATUS, default='available')
    max_patients_per_day = models.IntegerField(default=20)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'doctors'
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.specialization}"

class DoctorAvailability(models.Model):
    DAY_CHOICES = (
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    )
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='availability_schedule')
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'doctor_availability'
        unique_together = ['doctor', 'day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.doctor.user.get_full_name()} - {self.day_of_week}"

class DoctorLeaveRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='leave_requests')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'doctor_leave_requests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.doctor.user.get_full_name()} - {self.start_date} to {self.end_date}"
