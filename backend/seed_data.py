import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.patients.models import Patient
from apps.doctors.models import Doctor, DoctorAvailability
from apps.nurses.models import Nurse

User = get_user_model()

# Create Users
print("Creating seed data...")

# Admin User
admin_user, created = User.objects.get_or_create(
    email='admin@example.com',
    defaults={
        'first_name': 'Admin',
        'last_name': 'User',
        'role': 'admin',
        'is_staff': True,
        'is_superuser': True,
    }
)
if created:
    admin_user.set_password('admin123')
    admin_user.save()
    print("✓ Admin user created")

# Patient User
patient_user, created = User.objects.get_or_create(
    email='patient@example.com',
    defaults={
        'first_name': 'John',
        'last_name': 'Doe',
        'phone_number': '5551234567',
        'role': 'patient',
    }
)
if created:
    patient_user.set_password('patient123')
    patient_user.save()
    # Create patient profile
    Patient.objects.create(
        user=patient_user,
        age=35,
        gender='male',
        blood_pressure_systolic=120,
        blood_pressure_diastolic=80,
        heart_rate=72,
        temperature=98.6,
        spo2=98,
        diabetes=False,
        hypertension=False,
    )
    print("✓ Patient user created")

# Doctor User
doctor_user, created = User.objects.get_or_create(
    email='doctor@example.com',
    defaults={
        'first_name': 'Dr.',
        'last_name': 'Smith',
        'phone_number': '5559876543',
        'role': 'doctor',
    }
)
if created:
    doctor_user.set_password('doctor123')
    doctor_user.save()
    # Create doctor profile
    doctor, _ = Doctor.objects.get_or_create(
        user=doctor_user,
        defaults={
            'license_number': 'MD12345',
            'specialization': 'general',
            'department': 'General Medicine',
            'years_of_experience': 10,
            'qualification': 'MD in Medicine',
            'consultation_fee': 100.00,
        }
    )
    
    # Add availability
    for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
        DoctorAvailability.objects.get_or_create(
            doctor=doctor,
            day_of_week=day,
            defaults={
                'start_time': '09:00:00',
                'end_time': '17:00:00',
                'is_active': True,
            }
        )
    print("✓ Doctor user created")

# Nurse User
nurse_user, created = User.objects.get_or_create(
    email='nurse@example.com',
    defaults={
        'first_name': 'Jane',
        'last_name': 'Johnson',
        'phone_number': '5555551234',
        'role': 'nurse',
    }
)
if created:
    nurse_user.set_password('nurse123')
    nurse_user.save()
    # Create nurse profile
    Nurse.objects.create(
        user=nurse_user,
        license_number='RN54321',
        department='General Ward',
        shift='day',
        years_of_experience=8,
    )
    print("✓ Nurse user created")

# Management User
mgmt_user, created = User.objects.get_or_create(
    email='manager@example.com',
    defaults={
        'first_name': 'Manager',
        'last_name': 'User',
        'role': 'management',
    }
)
if created:
    mgmt_user.set_password('manager123')
    mgmt_user.save()
    print("✓ Management user created")

print("Seed data created successfully!")
print("\nTest Credentials:")
print("Admin: admin@example.com / admin123")
print("Patient: patient@example.com / patient123")
print("Doctor: doctor@example.com / doctor123")
print("Nurse: nurse@example.com / nurse123")
print("Manager: manager@example.com / manager123")
