"""
XGBoost Medical Risk Prediction Engine
Predicts patient risk levels based on medical features
"""

import xgboost as xgb
import numpy as np
import pandas as pd
import pickle
import os
import logging

logger = logging.getLogger(__name__)


class XGBoostMedicalPredictor:
    """
    XGBoost-based risk prediction for medical patients
    Handles:
    - Risk score calculation (0-1)
    - Feature importance explanation
    - Risk stratification (Low, Medium, High, Critical)
    - Confidence scores
    """
    
    def __init__(self, model_path=None):
        """
        Initialize XGBoost predictor
        
        Args:
            model_path: Path to pre-trained model
        """
        self.model = None
        self.feature_names = None
        self.scaler = None
        
        # Define medical risk features
        self.feature_set = [
            'age', 'heart_rate', 'systolic_bp', 'diastolic_bp',
            'temperature', 'spo2', 'respiratory_rate', 'glucose',
            'creatinine', 'hemoglobin', 'platelet_count', 'white_blood_cells',
            'comorbidity_count', 'medication_count', 'previous_hospitalizations',
            'days_since_last_visit', 'abnormal_lab_count'
        ]
        
        self.risk_thresholds = {
            'low': 0.25,
            'medium': 0.50,
            'high': 0.75,
            'critical': 1.0
        }
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            self._init_default_model()

    def _init_default_model(self):
        """Initialize with default model parameters"""
        self.model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            objective='reg:squarederror',
            random_state=42
        )
        # Will use fallback prediction if not trained
        logger.info("XGBoost model initialized with default parameters")

    def load_model(self, model_path):
        """Load pre-trained model"""
        try:
            self.model = xgb.XGBRegressor()
            self.model.load_model(model_path)
            logger.info(f"Loaded XGBoost model from {model_path}")
        except Exception as e:
            logger.warning(f"Could not load model: {e}, using default")
            self._init_default_model()

    def prepare_features(self, patient_data):
        """
        Prepare patient data for prediction
        
        Args:
            patient_data: Dictionary of patient metrics
            
        Returns:
            Feature vector for prediction
        """
        features = []
        for feature in self.feature_set:
            value = patient_data.get(feature, 0)
            # Handle missing values
            if value is None:
                value = 0
            features.append(float(value))
        
        return np.array([features])

    def predict_risk(self, patient_data):
        """
        Predict patient risk score
        
        Args:
            patient_data: Patient metrics dictionary
            
        Returns:
            Dictionary with risk score and classification
        """
        try:
            # Prepare features
            X = self.prepare_features(patient_data)
            
            # Make prediction
            risk_score = self.model.predict(X)[0]
            risk_score = float(np.clip(risk_score, 0, 1))
            
            # Get feature importance for explanation
            feature_importance = self.get_feature_importance(X)
            
            # Classify risk level
            risk_level = self._classify_risk(risk_score)
            
            return {
                'risk_score': risk_score,
                'risk_level': risk_level,
                'risk_percentage': f"{risk_score*100:.1f}%",
                'top_risk_factors': feature_importance['top_factors'],
                'confidence': risk_score if risk_score > 0.5 else 1 - risk_score
            }
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            # Fallback: rule-based risk
            return self._fallback_risk(patient_data)

    def _classify_risk(self, score):
        """Classify risk level from score"""
        if score < self.risk_thresholds['low']:
            return 'LOW'
        elif score < self.risk_thresholds['medium']:
            return 'MEDIUM'
        elif score < self.risk_thresholds['high']:
            return 'HIGH'
        else:
            return 'CRITICAL'

    def get_feature_importance(self, X):
        """
        Get feature importance from model
        
        Args:
            X: Feature vector
            
        Returns:
            Feature importance analysis
        """
        try:
            # Get SHAP-like importance
            importances = self.model.feature_importances_
            
            # Get top factors
            top_indices = np.argsort(importances)[-5:][::-1]
            top_factors = []
            for idx in top_indices:
                if idx < len(self.feature_set):
                    top_factors.append({
                        'feature': self.feature_set[idx],
                        'importance': float(importances[idx])
                    })
            
            return {'top_factors': top_factors}
        except Exception as e:
            logger.warning(f"Could not compute feature importance: {e}")
            return {'top_factors': []}

    def _fallback_risk(self, patient_data):
        """
        Fallback rule-based risk calculation
        """
        score = 0.0
        factors = []
        
        # Rule-based scoring
        age = patient_data.get('age', 0)
        if age > 65:
            score += 0.15
            factors.append('advanced_age')
        
        hr = patient_data.get('heart_rate', 0)
        if hr > 100 or hr < 60:
            score += 0.15
            factors.append('abnormal_heart_rate')
        
        spo2 = patient_data.get('spo2', 100)
        if spo2 < 95:
            score += 0.20
            factors.append('low_oxygen_saturation')
        
        temp = patient_data.get('temperature', 37)
        if temp > 38 or temp < 36:
            score += 0.10
            factors.append('fever_or_hypothermia')
        
        comorbidities = patient_data.get('comorbidity_count', 0)
        if comorbidities > 2:
            score += 0.15
            factors.append('multiple_comorbidities')
        
        score = float(np.clip(score, 0, 1))
        
        return {
            'risk_score': score,
            'risk_level': self._classify_risk(score),
            'risk_percentage': f"{score*100:.1f}%",
            'top_risk_factors': [{'feature': f, 'importance': 0.2} for f in factors],
            'confidence': score if score > 0.5 else 1 - score,
            'method': 'fallback_rule_based'
        }

    def batch_predict(self, patient_list):
        """
        Predict risk for multiple patients
        
        Args:
            patient_list: List of patient data dictionaries
            
        Returns:
            List of predictions
        """
        results = []
        for patient in patient_list:
            results.append(self.predict_risk(patient))
        return results


# Singleton instance
_predictor = None


def get_predictor(model_path=None):
    """Get or create predictor instance"""
    global _predictor
    if _predictor is None:
        _predictor = XGBoostMedicalPredictor(model_path)
    return _predictor
