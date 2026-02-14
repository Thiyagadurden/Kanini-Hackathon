from celery import shared_task
from apps.doctors.models import Doctor
from apps.patients.models import Patient
from itertools import cycle

@shared_task
def redistribute_patients_task(doctor_id):
    try:
        doctor = Doctor.objects.get(id=doctor_id)
        patients = Patient.objects.filter(doctor_assigned=doctor)
        
        available_doctors = Doctor.objects.filter(
            specialization=doctor.specialization,
            availability_status='available'
        ).exclude(id=doctor_id)
        
        if not available_doctors.exists():
            return {'message': 'No available doctors for redistribution'}
        
        doctor_cycle = cycle(available_doctors)
        reassigned_count = 0
        
        for patient in patients:
            new_doctor = next(doctor_cycle)
            patient.doctor_assigned = new_doctor
            patient.save()
            reassigned_count += 1
        
        from apps.notifications.services import NotificationService
        notification_service = NotificationService()
        
        for patient in patients:
            notification_service.create_notification(
                user=patient.user,
                notification_type='doctor_availability',
                title='Doctor Assignment Update',
                message=f'You have been reassigned to Dr. {patient.doctor_assigned.user.get_full_name()}',
                related_id=patient.id
            )
        
        return {'reassigned_count': reassigned_count}
    except Doctor.DoesNotExist:
        return {'error': 'Doctor not found'}
