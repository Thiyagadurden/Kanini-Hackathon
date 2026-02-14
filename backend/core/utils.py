import random
import string
import requests
from django.conf import settings
from django.core.mail import send_mail
from datetime import datetime, timedelta

def generate_patient_id():
    return 'P' + ''.join(random.choices(string.digits, k=8))

def generate_appointment_id():
    return 'A' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def generate_prescription_id():
    return 'RX' + ''.join(random.choices(string.digits, k=8))

def send_notification_email(to_email, subject, message):
    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [to_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email sending failed: {str(e)}")
        return False

def translate_text(text, target_language):
    if not settings.TRANSLATION_API_URL:
        return text
    
    try:
        response = requests.post(
            settings.TRANSLATION_API_URL,
            json={
                'text': text,
                'target_language': target_language
            },
            headers={'Authorization': f'Bearer {settings.TRANSLATION_API_KEY}'},
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get('translated_text', text)
    except Exception as e:
        print(f"Translation failed: {str(e)}")
    
    return text

def calculate_risk_score(patient_data):
    score = 0
    
    # Vital signs scoring
    bp_sys = patient_data.get('blood_pressure_systolic', 120)
    if bp_sys > 180 or bp_sys < 90:
        score += 3
    elif bp_sys > 140 or bp_sys < 100:
        score += 2
    
    hr = patient_data.get('heart_rate', 70)
    if hr > 120 or hr < 50:
        score += 3
    elif hr > 100 or hr < 60:
        score += 1
    
    temp = patient_data.get('temperature', 98.6)
    if temp > 103 or temp < 95:
        score += 3
    elif temp > 100.4:
        score += 2
    
    spo2 = patient_data.get('spo2', 98)
    if spo2 < 90:
        score += 3
    elif spo2 < 94:
        score += 2
    
    # Symptoms scoring
    critical_symptoms = ['chest_pain', 'breathing_difficulty']
    for symptom in critical_symptoms:
        if patient_data.get(f'symptom_{symptom}', False):
            score += 3
    
    moderate_symptoms = ['fever', 'dizziness', 'vomiting']
    for symptom in moderate_symptoms:
        if patient_data.get(f'symptom_{symptom}', False):
            score += 1
    
    # Chronic conditions
    chronic_conditions = ['heart_disease', 'diabetes', 'hypertension', 'asthma']
    for condition in chronic_conditions:
        if patient_data.get(condition, False):
            score += 1
    
    if patient_data.get('pregnant', False):
        score += 2
    
    # Risk level determination
    if score >= 10:
        return 'critical', score
    elif score >= 6:
        return 'high', score
    elif score >= 3:
        return 'medium', score
    else:
        return 'low', score

def get_next_available_slot(doctor, date=None):
    from apps.appointments.models import Appointment
    from datetime import datetime, time, timedelta
    
    if date is None:
        date = datetime.now().date()
    
    working_hours = [(9, 0), (17, 0)]  # 9 AM to 5 PM
    slot_duration = 30  # minutes
    
    existing_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=date,
        status__in=['scheduled', 'confirmed']
    ).values_list('appointment_time', flat=True)
    
    current_time = datetime.combine(date, time(working_hours[0][0], working_hours[0][1]))
    end_time = datetime.combine(date, time(working_hours[1][0], working_hours[1][1]))
    
    while current_time < end_time:
        if current_time.time() not in existing_appointments:
            return current_time.time()
        current_time += timedelta(minutes=slot_duration)
    
    return None
