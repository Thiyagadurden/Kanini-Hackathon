from celery import shared_task
from apps.emergency.models import EmergencyRequest
from apps.notifications.services import NotificationService
from django.contrib.auth import get_user_model

User = get_user_model()

@shared_task
def notify_emergency_task(emergency_id, recipient_type):
    try:
        emergency = EmergencyRequest.objects.get(id=emergency_id)
        notification_service = NotificationService()
        
        if recipient_type == 'nurse' and emergency.nurse:
            notification_service.create_notification(
                user=emergency.nurse.user,
                notification_type='emergency',
                title='Emergency Alert',
                message=f'Emergency request from patient {emergency.patient.patient_id}',
                related_id=emergency.id
            )
        elif recipient_type == 'doctor' and emergency.doctor:
            notification_service.create_notification(
                user=emergency.doctor.user,
                notification_type='emergency',
                title='Emergency Escalation',
                message=f'Emergency escalated from patient {emergency.patient.patient_id}',
                related_id=emergency.id
            )
    except EmergencyRequest.DoesNotExist:
        pass

@shared_task
def escalate_emergency_task(emergency_id):
    from django.utils import timezone
    from datetime import timedelta
    
    try:
        emergency = EmergencyRequest.objects.get(id=emergency_id)
        if emergency.status == 'nurse_notified':
            time_elapsed = timezone.now() - emergency.nurse_notified_at
            if time_elapsed > timedelta(minutes=5):
                from apps.emergency.services import EmergencyService
                service = EmergencyService()
                service.escalate_to_doctor(emergency, "No nurse response after 5 minutes")
    except EmergencyRequest.DoesNotExist:
        pass

@shared_task
def check_emergency_escalation():
    from django.utils import timezone
    from datetime import timedelta
    
    pending_emergencies = EmergencyRequest.objects.filter(status='nurse_notified')
    
    for emergency in pending_emergencies:
        time_elapsed = timezone.now() - emergency.nurse_notified_at
        if time_elapsed > timedelta(minutes=5):
            from apps.emergency.services import EmergencyService
            service = EmergencyService()
            service.escalate_to_doctor(emergency, "Automatic escalation - no response")
