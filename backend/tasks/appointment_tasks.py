from celery import shared_task
from apps.appointments.models import Appointment
from apps.notifications.services import NotificationService
from datetime import datetime, timedelta

@shared_task
def send_appointment_reminders():
    tomorrow = datetime.now().date() + timedelta(days=1)
    appointments = Appointment.objects.filter(
        appointment_date=tomorrow,
        status__in=['scheduled', 'confirmed'],
        reminder_sent=False
    )
    
    notification_service = NotificationService()
    
    for appointment in appointments:
        notification_service.create_notification(
            user=appointment.patient.user,
            notification_type='appointment',
            title='Appointment Reminder',
            message=f'You have an appointment tomorrow at {appointment.appointment_time}',
            related_id=appointment.id
        )
        
        appointment.reminder_sent = True
        appointment.save()
