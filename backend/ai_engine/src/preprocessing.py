import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import pickle
import os

class TriagePreprocessor:
    def __init__(self):
        self.numerical_features = [
            'age', 'blood_pressure_systolic', 'blood_pressure_diastolic', 
            'heart_rate', 'temperature', 'spo2', 'pain_level'
        ]
        self.categorical_features = [
            'gender', 'visit_type', 'insurance_provider', 
            'recent_diagnosis', 'chronic_disease_history', 'family_medical_history'
        ]
        # Boolean features treated as numerical (0/1) or categorical? 
        # Usually XGBoost handles 0/1 well, but let's be explicit.
        self.boolean_features = [
            'symptom_chest_pain', 'symptom_fever', 'symptom_cough', 
            'symptom_breathing_difficulty', 'symptom_headache', 
            'symptom_dizziness', 'symptom_vomiting',
            'diabetes', 'hypertension', 'heart_disease', 'asthma', 
            'pregnant', 'smoker'
        ]
        
        self.pipeline = None
        self.label_encoder = None

    def build_pipeline(self):
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])

        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
            ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ])

        self.pipeline = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, self.numerical_features),
                ('cat', categorical_transformer, self.categorical_features),
                ('bool', 'passthrough', self.boolean_features)
            ]
        )
        # Target label encoder
        self.label_encoder = LabelEncoder()

    def fit(self, X, y=None):
        if self.pipeline is None:
            self.build_pipeline()
        
        self.pipeline.fit(X)
        if y is not None:
            self.label_encoder.fit(y)
        return self

    def transform(self, X):
        return self.pipeline.transform(X)

    def fit_transform(self, X, y=None):
        self.fit(X, y)
        X_transformed = self.transform(X)
        y_transformed = None
        if y is not None:
            y_transformed = self.label_encoder.transform(y)
            return X_transformed, y_transformed
        return X_transformed

    def save(self, filepath):
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(filepath):
        with open(filepath, 'rb') as f:
            return pickle.load(f)

    def inverse_transform_label(self, y):
        return self.label_encoder.inverse_transform(y)
