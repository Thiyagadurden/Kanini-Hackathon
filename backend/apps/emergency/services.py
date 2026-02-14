from django.utils import timezone
from .models import EmergencyRequest
from apps.patients.models import Patient
from apps.nurses.models import Nurse
from tasks.celery_tasks import notify_emergency_task, escalate_emergency_task

class EmergencyService:
    def create_emergency_request(self, user, description, severity='medium'):
        patient = Patient.objects.get(user=user)
        
        emergency = EmergencyRequest.objects.create(
            patient=patient,
            description=description,
            severity=severity,
            status='pending'
        )
        
        assigned_nurse = self.get_assigned_nurse(patient)
        if assigned_nurse:
            emergency.nurse = assigned_nurse
            emergency.status = 'nurse_notified'
            emergency.nurse_notified_at = timezone.now()
            emergency.save()
            
            notify_emergency_task.delay(emergency.id, 'nurse')
        
        escalate_emergency_task.apply_async(args=[emergency.id], countdown=300)
        
        return emergency
    
    def get_assigned_nurse(self, patient):
        if patient.doctor_assigned:
            nurses = Nurse.objects.filter(department=patient.doctor_assigned.department)
            if nurses.exists():
                return nurses.first()
        return Nurse.objects.first()
    
    def nurse_respond(self, emergency, nurse, notes):
        emergency.nurse = nurse
        emergency.status = 'nurse_responded'
        emergency.nurse_responded_at = timezone.now()
        emergency.response_notes = notes
        emergency.save()
    
    def escalate_to_doctor(self, emergency, reason):
        emergency.status = 'doctor_escalated'
        emergency.escalation_reason = reason
        emergency.doctor_notified_at = timezone.now()
        
        if emergency.patient.doctor_assigned:
            emergency.doctor = emergency.patient.doctor_assigned
        
        emergency.save()
        
        notify_emergency_task.delay(emergency.id, 'doctor')
    
    def resolve_emergency(self, emergency, notes):
        emergency.status = 'resolved'
        emergency.resolved_at = timezone.now()
        emergency.response_notes = notes
        emergency.save()
