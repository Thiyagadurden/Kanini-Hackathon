import joblib
import numpy as np

# Load model and encoder
model = joblib.load("models/triage_xgboost_model.pkl")
encoder = joblib.load("models/risk_label_encoder.pkl")

def predict_risk(patient_data):

    features = np.array([[
        patient_data["age"],
        patient_data["blood_pressure_systolic"],
        patient_data["blood_pressure_diastolic"],
        patient_data["heart_rate"],
        patient_data["temperature"],
        patient_data["spo2"],
        patient_data["pain_level"],

        patient_data["symptom_chest_pain"],
        patient_data["symptom_fever"],
        patient_data["symptom_cough"],
        patient_data["symptom_breathing_difficulty"],
        patient_data["symptom_headache"],
        patient_data["symptom_dizziness"],
        patient_data["symptom_vomiting"],

        patient_data["diabetes"],
        patient_data["hypertension"],
        patient_data["heart_disease"],
        patient_data["asthma"],
        patient_data["pregnant"],
        patient_data["smoker"]
    ]])

    prediction = model.predict(features)
    probability = model.predict_proba(features)

    risk = encoder.inverse_transform(prediction)[0]
    confidence = float(np.max(probability))

    return risk, confidence
