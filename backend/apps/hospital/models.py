from django.db import models

class HospitalResource(models.Model):
    RESOURCE_TYPE_CHOICES = (
        ('bed', 'Hospital Bed'),
        ('ventilator', 'Ventilator'),
        ('icu', 'ICU'),
        ('equipment', 'Medical Equipment'),
        ('medicine', 'Medicine Stock'),
    )
    
    resource_type = models.CharField(max_length=50, choices=RESOURCE_TYPE_CHOICES)
    name = models.CharField(max_length=200)
    total_quantity = models.IntegerField()
    available_quantity = models.IntegerField()
    department = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'hospital_resources'
    
    def __str__(self):
        return f"{self.name} - {self.department}"
