from celery import shared_task
from apps.notifications.services import NotificationService
from apps.prescriptions.models import Prescription
from datetime import datetime

@shared_task
def send_medicine_reminders():
    notification_service = NotificationService()
    prescriptions = Prescription.objects.filter(
        created_at__gte=datetime.now().date()
    ).select_related('patient__user')
    
    for prescription in prescriptions:
        notification_service.create_notification(
            user=prescription.patient.user,
            notification_type='medicine',
            title='Medicine Reminder',
            message='Time to take your prescribed medication',
            related_id=prescription.id
        )
