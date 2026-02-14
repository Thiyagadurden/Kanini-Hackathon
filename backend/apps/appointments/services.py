from .models import Appointment
from core.utils import get_next_available_slot
from datetime import datetime

class AppointmentService:
    def create_appointment(self, patient, doctor, date, time, reason):
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            appointment_date=date,
            appointment_time=time,
            reason=reason
        )
        return appointment
    
    def get_available_slots(self, doctor, date):
        from datetime import time, timedelta
        slots = []
        current_time = datetime.combine(date, time(9, 0))
        end_time = datetime.combine(date, time(17, 0))
        
        existing = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=date,
            status__in=['scheduled', 'confirmed']
        ).values_list('appointment_time', flat=True)
        
        while current_time.time() < end_time.time():
            if current_time.time() not in existing:
                slots.append(current_time.time())
            current_time += timedelta(minutes=30)
        
        return slots
