from .models import Patient, VitalsHistory
from core.utils import calculate_risk_score

class PatientService:
    def update_patient_vitals(self, patient, vitals_data, recorded_by):
        patient.blood_pressure_systolic = vitals_data.get('blood_pressure_systolic', patient.blood_pressure_systolic)
        patient.blood_pressure_diastolic = vitals_data.get('blood_pressure_diastolic', patient.blood_pressure_diastolic)
        patient.heart_rate = vitals_data.get('heart_rate', patient.heart_rate)
        patient.temperature = vitals_data.get('temperature', patient.temperature)
        patient.spo2 = vitals_data.get('spo2', patient.spo2)
        patient.save()
        
        vitals = VitalsHistory.objects.create(
            patient=patient,
            blood_pressure_systolic=patient.blood_pressure_systolic,
            blood_pressure_diastolic=patient.blood_pressure_diastolic,
            heart_rate=patient.heart_rate,
            temperature=patient.temperature,
            spo2=patient.spo2,
            recorded_by=recorded_by,
            notes=vitals_data.get('notes', '')
        )
        
        self.calculate_patient_risk(patient)
        
        return vitals
    
    def calculate_patient_risk(self, patient):
        patient_data = {
            'blood_pressure_systolic': patient.blood_pressure_systolic,
            'blood_pressure_diastolic': patient.blood_pressure_diastolic,
            'heart_rate': patient.heart_rate,
            'temperature': patient.temperature,
            'spo2': patient.spo2,
            'symptom_chest_pain': patient.symptom_chest_pain,
            'symptom_breathing_difficulty': patient.symptom_breathing_difficulty,
            'symptom_fever': patient.symptom_fever,
            'symptom_dizziness': patient.symptom_dizziness,
            'symptom_vomiting': patient.symptom_vomiting,
            'heart_disease': patient.heart_disease,
            'diabetes': patient.diabetes,
            'hypertension': patient.hypertension,
            'asthma': patient.asthma,
            'pregnant': patient.pregnant,
        }
        
        risk_level, risk_score = calculate_risk_score(patient_data)
        patient.risk_level = risk_level
        patient.risk_score = risk_score
        patient.save()
        
        return risk_level, risk_score
    
    def assign_doctor(self, patient, doctor):
        patient.doctor_assigned = doctor
        patient.save()
        return patient
    
    def get_patient_summary(self, patient):
        return {
            'patient_id': patient.patient_id,
            'name': patient.user.get_full_name(),
            'age': patient.age,
            'gender': patient.gender,
            'risk_level': patient.risk_level,
            'risk_score': patient.risk_score,
            'doctor_assigned': patient.doctor_assigned.user.get_full_name() if patient.doctor_assigned else None,
            'last_vitals': {
                'bp': f"{patient.blood_pressure_systolic}/{patient.blood_pressure_diastolic}",
                'hr': patient.heart_rate,
                'temp': patient.temperature,
                'spo2': patient.spo2,
            } if patient.blood_pressure_systolic else None,
        }
