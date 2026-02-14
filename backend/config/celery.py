import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

app = Celery('voicetriage')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-appointment-reminders': {
        'task': 'tasks.appointment_tasks.send_appointment_reminders',
        'schedule': crontab(hour=8, minute=0),
    },
    'send-medicine-reminders': {
        'task': 'tasks.notification_tasks.send_medicine_reminders',
        'schedule': crontab(hour='*/4'),
    },
    'check-emergency-escalation': {
        'task': 'tasks.celery_tasks.check_emergency_escalation',
        'schedule': crontab(minute='*/5'),
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
