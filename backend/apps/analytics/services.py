from django.db.models import Count, Avg
from apps.patients.models import Patient
from apps.appointments.models import Appointment
from apps.emergency.models import EmergencyRequest
from apps.doctors.models import Doctor
from datetime import datetime, timedelta

class AnalyticsService:
    def get_dashboard_metrics(self):
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        
        return {
            'total_patients': Patient.objects.count(),
            'active_doctors': Doctor.objects.filter(availability_status='available').count(),
            'appointments_today': Appointment.objects.filter(appointment_date=today).count(),
            'emergency_requests_week': EmergencyRequest.objects.filter(created_at__gte=week_ago).count(),
            'pending_emergencies': EmergencyRequest.objects.filter(status__in=['pending', 'nurse_notified']).count(),
        }
    
    def get_patient_statistics(self):
        return {
            'by_risk_level': Patient.objects.values('risk_level').annotate(count=Count('id')),
            'by_department': Patient.objects.values('department').annotate(count=Count('id')),
            'by_gender': Patient.objects.values('gender').annotate(count=Count('id')),
        }
    
    def get_doctor_performance(self):
        doctors = Doctor.objects.all()
        performance = []
        
        for doctor in doctors:
            performance.append({
                'doctor_name': doctor.user.get_full_name(),
                'specialization': doctor.specialization,
                'patient_count': doctor.patients.count(),
                'appointments_completed': doctor.appointments.filter(status='completed').count(),
                'average_consultation_time': 30,
            })
        
        return performance
