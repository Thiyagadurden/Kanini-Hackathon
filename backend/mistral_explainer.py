from mistralai import Mistral

API_KEY = "YOUR_MISTRAL_API_KEY"

client = Mistral(api_key=API_KEY)

def explain_prediction(patient_data, risk):

    prompt = f"""
    Patient details:
    Age: {patient_data['age']}
    Heart Rate: {patient_data['heart_rate']}
    BP: {patient_data['blood_pressure_systolic']}/{patient_data['blood_pressure_diastolic']}
    Temperature: {patient_data['temperature']}
    SPO2: {patient_data['spo2']}
    
    Predicted Risk: {risk}
    
    Explain clearly why this risk level was predicted in simple medical terms.
    """

    response = client.chat.complete(
        model="mistral-small",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
