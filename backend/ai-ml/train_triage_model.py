import pandas as pd
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

# Load dataset
df = pd.read_csv("patients.csv")

# Encode target
le = LabelEncoder()
df["risk_level"] = le.fit_transform(df["risk_level"])

# Save encoder
joblib.dump(le, "risk_label_encoder.pkl")

# Select features
features = [
    "age",
    "blood_pressure_systolic",
    "blood_pressure_diastolic",
    "heart_rate",
    "temperature",
    "spo2",
    "pain_level",

    "symptom_chest_pain",
    "symptom_fever",
    "symptom_cough",
    "symptom_breathing_difficulty",
    "symptom_headache",
    "symptom_dizziness",
    "symptom_vomiting",

    "diabetes",
    "hypertension",
    "heart_disease",
    "asthma",
    "pregnant",
    "smoker"
]

X = df[features]
y = df["risk_level"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train XGBoost
model = XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    objective="multi:softprob",
    num_class=3
)

model.fit(X_train, y_train)

# Save model
joblib.dump(model, "triage_xgboost_model.pkl")

# Evaluate
y_pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

print("Model training completed.")
