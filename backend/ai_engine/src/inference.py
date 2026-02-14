import pandas as pd
import numpy as np
import joblib
import os
from .preprocessing import TriagePreprocessor
from .rag_engine import MedicalRAG
from .explainability import TriageExplainer

# Load paths
MODEL_DIR = os.path.join(os.path.dirname(__file__), '../models')
MODEL_PATH = os.path.join(MODEL_DIR, 'risk_model.joblib')
DEPT_PATH = os.path.join(MODEL_DIR, 'dept_model.joblib')
PREPROCESSOR_PATH = os.path.join(MODEL_DIR, 'preprocessor.pkl')

class InferenceEngine:
    def __init__(self):
        self.risk_model = None
        self.dept_model = None
        self.preprocessor = None
        self.le_risk = None
        self.le_dept = None
        self.le_dept = None
        self.rag = MedicalRAG()
        self.explainer = TriageExplainer()
        
    def load_models(self):
        if self.risk_model is None:
            if os.path.exists(MODEL_PATH):
                self.risk_model = joblib.load(MODEL_PATH)
                print(f"Risk model loaded from {MODEL_PATH}")
            else:
                print(f"Model not found at {MODEL_PATH}")
                
            if os.path.exists(DEPT_PATH):
                self.dept_model = joblib.load(DEPT_PATH)
            
            if os.path.exists(PREPROCESSOR_PATH):
                with open(PREPROCESSOR_PATH, 'rb') as f:
                    import pickle
                    self.preprocessor = pickle.load(f)
            else:
                # Default empty
                self.preprocessor = TriagePreprocessor()

            try:
                self.le_risk = joblib.load(os.path.join(MODEL_DIR, 'le_risk.joblib'))
                self.le_dept = joblib.load(os.path.join(MODEL_DIR, 'le_dept.joblib'))
            except:
                print("Label encoders not found.")

            # Load RAG index if exists
            self.rag.load_index()
            try:
                self.explainer.load_explainer()
            except Exception as e:
                print(f"Failed to load explainer: {e}")

    def predict(self, input_data):
        self.load_models()
        self.rag.load_index() # Re-check if index exists or was built

        # Convert dict input to DataFrame
        df = pd.DataFrame([input_data])
        
        # Preprocess
        X_transformed = self.preprocessor.transform(df)
        
        # Risk Prediction
        risk_proba = self.risk_model.predict_proba(X_transformed)[0]
        risk_class_idx = np.argmax(risk_proba)
        
        if self.le_risk:
            risk_label = self.le_risk.inverse_transform([risk_class_idx])[0]
        else:
            # Fallback if no label encoder
            risk_label = "Unknown" 
        
        confidence = float(np.max(risk_proba))
        
        # Department Prediction
        dept_proba = self.dept_model.predict_proba(X_transformed)[0]
        dept_class_idx = np.argmax(dept_proba)
        
        if self.le_dept:
            department = self.le_dept.inverse_transform([dept_class_idx])[0]
        else:
            department = "General Medicine"

        # RAG Context
        symptoms = []
        for key in input_data:
            if key.startswith('symptom_') and input_data[key] == 1:
                symptoms.append(key.replace('symptom_', ''))
        
        query = f"Patient presents with {', '.join(symptoms)}. Predicted risk: {risk_label}."
        if 'pain_level' in input_data:
             query += f" Pain level: {input_data['pain_level']}."
        
        context = self.rag.retrieve(query, k=2)
        
        # Explanation
        try:
            explanation = self.explainer.explain_prediction(X_transformed)
            # Add simple reasoning text
            explanation["reasoning"] = f"Risk predicted as {risk_label} with {confidence*100:.1f}% confidence."
            explanation["contributing_factors"] = symptoms
        except Exception as e:
            print(f"Explanation failed: {e}")
            explanation = {
                "reasoning": f"Risk predicted as {risk_label} with {confidence*100:.1f}% confidence based on vital signs and symptoms.",
                "contributing_factors": symptoms,
                "error": str(e)
            }

        return {
            'risk_level': risk_label,
            'confidence': confidence,
            'department': department,
            'explanation': explanation,
            'retrieved_medical_context': context
        }

if __name__ == "__main__":
    engine = InferenceEngine()
    # Dummy input
    data = {'age': 45, 'gender': 'Male', 'blood_pressure_systolic': 160, 'blood_pressure_diastolic': 95, 
            'heart_rate': 88, 'temperature': 37.5, 'spo2': 98, 'symptom_chest_pain': 1, 
            'symptom_fever': 0, 'symptom_cough': 0, 'symptom_breathing_difficulty': 0,
            'symptom_headache': 1, 'symptom_dizziness': 0, 'symptom_vomiting': 0,
            'diabetes': 1, 'hypertension': 1, 'heart_disease': 0, 'asthma': 0, 'pregnant': 0, 'smoker': 1,
            'visit_type': 'Emergency', 'insurance_provider': 'None', 'recent_diagnosis': 'None',
            'chronic_disease_history': 'Diabetes', 'family_medical_history': 'None'}
    print(engine.predict(data))
