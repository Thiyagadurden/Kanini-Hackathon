from django.db import models

class HospitalMetrics(models.Model):
    date = models.DateField(unique=True)
    total_patients = models.IntegerField(default=0)
    new_patients = models.IntegerField(default=0)
    total_appointments = models.IntegerField(default=0)
    completed_appointments = models.IntegerField(default=0)
    emergency_requests = models.IntegerField(default=0)
    average_wait_time = models.FloatField(default=0)
    patient_satisfaction_score = models.FloatField(default=0)
    
    class Meta:
        db_table = 'hospital_metrics'
        ordering = ['-date']
    
    def __str__(self):
        return f"Metrics - {self.date}"
