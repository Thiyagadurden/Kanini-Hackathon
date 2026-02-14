from celery import shared_task
from django.utils import timezone
from datetime import timedelta

@shared_task
def check_emergency_escalation(emergency_id):
    from .models import EmergencyRequest
    from .services import EmergencyService
    
    try:
        emergency = EmergencyRequest.objects.get(id=emergency_id)
        if emergency.status == 'nurse_notified':
            time_elapsed = timezone.now() - emergency.nurse_notified_at
            if time_elapsed > timedelta(minutes=5):
                service = EmergencyService()
                service.escalate_to_doctor(emergency, "No nurse response after 5 minutes")
    except EmergencyRequest.DoesNotExist:
        pass
