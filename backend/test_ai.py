import requests
import json

BASE_URL = "http://localhost:8000/api/ai"

def test_prediction():
    print("\n--- Testing Prediction ---")
    data = {
        'age': 45, 
        'gender': 'Male', 
        'blood_pressure_systolic': 160, 
        'blood_pressure_diastolic': 95, 
        'heart_rate': 88, 
        'temperature': 37.5, 
        'spo2': 98, 
        'symptom_chest_pain': 1, 
        'symptom_fever': 0, 
        'symptom_cough': 0, 
        'symptom_breathing_difficulty': 0,
        'symptom_headache': 1, 
        'symptom_dizziness': 0, 
        'symptom_vomiting': 0,
        'diabetes': 1, 
        'hypertension': 1, 
        'heart_disease': 0, 
        'asthma': 0, 
        'pregnant': 0, 
        'smoker': 1,
        'visit_type': 'Emergency', 
        'insurance_provider': 'None', 
        'recent_diagnosis': 'None',
        'chronic_disease_history': 'Diabetes', 
        'family_medical_history': 'None'
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predict/", json=data)
        if response.status_code == 200:
            print("[SUCCESS] Prediction Response:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"[ERROR] Prediction failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"[ERROR] Exception: {e}")

def test_retrieval():
    print("\n--- Testing Retrieval ---")
    data = {
        "query": "What are the symptoms of myocardial infarction?"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/retrieve/", json=data)
        if response.status_code == 200:
            print("[SUCCESS] Retrieval Response:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"[ERROR] Retrieval failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"[ERROR] Exception: {e}")

if __name__ == "__main__":
    test_prediction()
    test_retrieval()
