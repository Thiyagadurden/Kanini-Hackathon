from .models import Doctor, DoctorLeaveRequest
from apps.patients.models import Patient
from tasks.redistribution_tasks import redistribute_patients_task

class DoctorService:
    def request_availability_change(self, doctor, new_status, reason=None):
        if new_status == 'unavailable':
            leave_request = DoctorLeaveRequest.objects.create(
                doctor=doctor,
                start_date=timezone.now().date(),
                end_date=timezone.now().date(),
                reason=reason or 'Temporary unavailability',
                status='pending'
            )
            return {
                'message': 'Availability change request submitted for admin approval',
                'leave_request_id': leave_request.id
            }
        else:
            doctor.availability_status = new_status
            doctor.save()
            return {'message': 'Availability updated successfully'}
    
    def approve_leave_request(self, leave_request, approved_by):
        leave_request.status = 'approved'
        leave_request.approved_by = approved_by
        leave_request.save()
        
        doctor = leave_request.doctor
        doctor.availability_status = 'on_leave'
        doctor.save()
        
        redistribute_patients_task.delay(doctor.id)
        
        return {
            'message': 'Leave approved and patient redistribution initiated',
            'doctor_id': doctor.id
        }
    
    def reassign_patients(self, doctor):
        patients = Patient.objects.filter(doctor_assigned=doctor)
        available_doctors = Doctor.objects.filter(
            specialization=doctor.specialization,
            availability_status='available'
        ).exclude(id=doctor.id)
        
        if not available_doctors.exists():
            return {'message': 'No available doctors for reassignment'}
        
        doctor_cycle = cycle(available_doctors)
        reassigned_count = 0
        
        for patient in patients:
            new_doctor = next(doctor_cycle)
            patient.doctor_assigned = new_doctor
            patient.save()
            reassigned_count += 1
        
        return {
            'message': f'{reassigned_count} patients reassigned',
            'reassigned_count': reassigned_count
        }

from itertools import cycle
from django.utils import timezone
