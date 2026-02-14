import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder
import pickle
import os
import joblib
from .preprocessing import TriagePreprocessor

DATA_PATH = os.path.join(os.path.dirname(__file__), '../data/synthetic_triage_data.csv')
MODEL_DIR = os.path.join(os.path.dirname(__file__), '../models')

def generate_synthetic_data(n_samples=1000):
    # Check if data already exists
    if os.path.exists(DATA_PATH):
        print(f"Loading data from {DATA_PATH}...")
        try:
            df = pd.read_csv(DATA_PATH, on_bad_lines='skip')
            print(f"Loaded {len(df)} rows.")
            
            # Additional cleaning: drop rows where critical columns have NaNs
            # or where target is invalid
            df = df.dropna(subset=['risk_level', 'department'])
            valid_risks = ['High', 'Medium', 'Low']
            df = df[df['risk_level'].isin(valid_risks)]
            
            # Drop rows where 'age' is not numeric (sanity check)
            df['age'] = pd.to_numeric(df['age'], errors='coerce')
            df = df.dropna(subset=['age'])
            
            return df
        except Exception as e:
            print(f"Error loading CSV: {e}")
            print("Falling back to synthetic generation.")

    np.random.seed(42)
    
    data = {
        'age': np.random.randint(18, 90, n_samples),
        'gender': np.random.choice(['Male', 'Female'], n_samples),
        'blood_pressure_systolic': np.random.randint(90, 180, n_samples),
        'blood_pressure_diastolic': np.random.randint(60, 120, n_samples),
        'heart_rate': np.random.randint(50, 130, n_samples),
        'temperature': np.random.uniform(36.0, 40.0, n_samples),
        'spo2': np.random.randint(85, 100, n_samples),
        
        'symptom_chest_pain': np.random.choice([0, 1], n_samples, p=[0.8, 0.2]),
        'symptom_fever': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
        'symptom_cough': np.random.choice([0, 1], n_samples, p=[0.6, 0.4]),
        'symptom_breathing_difficulty': np.random.choice([0, 1], n_samples, p=[0.8, 0.2]),
        'symptom_headache': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
        'symptom_dizziness': np.random.choice([0, 1], n_samples, p=[0.8, 0.2]),
        'symptom_vomiting': np.random.choice([0, 1], n_samples, p=[0.9, 0.1]),
        'pain_level': np.random.randint(1, 10, n_samples),
        
        'diabetes': np.random.choice([0, 1], n_samples, p=[0.85, 0.15]),
        'hypertension': np.random.choice([0, 1], n_samples, p=[0.75, 0.25]),
        'heart_disease': np.random.choice([0, 1], n_samples, p=[0.9, 0.1]),
        'asthma': np.random.choice([0, 1], n_samples, p=[0.9, 0.1]),
        'pregnant': np.random.choice([0, 1], n_samples, p=[0.95, 0.05]),
        'smoker': np.random.choice([0, 1], n_samples, p=[0.8, 0.2]),
        
        'visit_type': np.random.choice(['Routine', 'Emergency', 'Follow-up'], n_samples),
        'insurance_provider': np.random.choice(['Provider A', 'Provider B', 'None'], n_samples),
        'recent_diagnosis': np.random.choice(['None', 'Flu', 'Infection'], n_samples),
        'chronic_disease_history': np.random.choice(['None', 'Diabetes', 'Hypertension'], n_samples),
        'family_medical_history': np.random.choice(['None', 'Heart Disease', 'Cancer'], n_samples),
    }
    
    df = pd.DataFrame(data)
    
    # Logic for Risk Level
    conditions = [
        (df['symptom_chest_pain'] == 1) | (df['symptom_breathing_difficulty'] == 1) | (df['spo2'] < 90) | (df['heart_rate'] > 110),
        (df['symptom_fever'] == 1) | (df['temperature'] > 38.5) | (df['blood_pressure_systolic'] > 150),
    ]
    choices = ['High', 'Medium']
    df['risk_level'] = np.select(conditions, choices, default='Low')
    
    # Logic for Department
    dept_conditions = [
        (df['symptom_chest_pain'] == 1) | (df['heart_disease'] == 1),
        (df['symptom_breathing_difficulty'] == 1) | (df['asthma'] == 1),
        (df['symptom_fever'] == 1) & (df['symptom_cough'] == 1),
        (df['risk_level'] == 'High')
    ]
    dept_choices = ['Cardiology', 'Pulmonology', 'General Medicine', 'Emergency']
    df['department'] = np.select(dept_conditions, dept_choices, default='General Medicine')
    
    return df

def train_models():
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    print("Generating/Loading data...")
    df = generate_synthetic_data(2000)
    if not os.path.exists(DATA_PATH):
        df.to_csv(DATA_PATH, index=False)
    
    # Columns to drop (IDs, dates, targets)
    drop_cols = ['risk_level', 'department', 'patient_id', 'doctor_assigned', 
                 'hospital_clinic_id', 'last_checkup_date', 'next_appointment_date']
    # Filter only columns present in dataframe
    drop_cols = [col for col in drop_cols if col in df.columns]
    
    X = df.drop(drop_cols, axis=1)
    y_risk = df['risk_level']
    y_dept = df['department']
    
    print("Dropped columns:", drop_cols)
    print("X columns:", X.columns.tolist())
    print("X dtypes:\n", X.dtypes)
    print("X head:\n", X.head())

    print("Preprocessing data...")
    preprocessor = TriagePreprocessor()
    preprocessor.build_pipeline()
    
    # Fit pipeline
    preprocessor.pipeline.fit(X)
    X_transformed = preprocessor.transform(X)
    
    # Encode targets
    le_risk = preprocessor.label_encoder # We need separate encoders
    y_risk_encoded = le_risk.fit_transform(y_risk)
    
    le_dept = LabelEncoder()
    y_dept_encoded = le_dept.fit_transform(y_dept)
    
    # Split
    X_train, X_test, y_risk_train, y_risk_test, y_dept_train, y_dept_test = train_test_split(
        X_transformed, y_risk_encoded, y_dept_encoded, test_size=0.2, random_state=42
    )
    
    print("Training Risk Model (XGBoost)...")
    risk_model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='mlogloss')
    risk_model.fit(X_train, y_risk_train)
    
    risk_pred = risk_model.predict(X_test)
    print("Risk Model Accuracy:", accuracy_score(y_risk_test, risk_pred))
    print(classification_report(y_risk_test, risk_pred, target_names=le_risk.classes_))
    
    print("Training Department Model (XGBoost)...")
    dept_model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='mlogloss')
    dept_model.fit(X_train, y_dept_train)
    
    dept_pred = dept_model.predict(X_test)
    print("Department Model Accuracy:", accuracy_score(y_dept_test, dept_pred))
    print(classification_report(y_dept_test, dept_pred, target_names=le_dept.classes_))
    
    # Save artifacts
    print("Saving models...")
    preprocessor.save(os.path.join(MODEL_DIR, 'preprocessor.pkl'))
    joblib.dump(risk_model, os.path.join(MODEL_DIR, 'risk_model.joblib'))
    joblib.dump(dept_model, os.path.join(MODEL_DIR, 'dept_model.joblib'))
    joblib.dump(le_risk, os.path.join(MODEL_DIR, 'le_risk.joblib'))
    joblib.dump(le_dept, os.path.join(MODEL_DIR, 'le_dept.joblib'))
    
    # Save feature names for SHAP
    feature_names = (preprocessor.numerical_features + 
                     list(preprocessor.pipeline.named_transformers_['cat']['onehot'].get_feature_names_out(preprocessor.categorical_features)) + 
                     preprocessor.boolean_features)
    joblib.dump(feature_names, os.path.join(MODEL_DIR, 'feature_names.joblib'))
    
    print("Training complete.")

if __name__ == "__main__":
    train_models()
