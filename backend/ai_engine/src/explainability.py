import shap
import xgboost as xgb
import os
import joblib
import pandas as pd
import numpy as np

MODEL_DIR = os.path.join(os.path.dirname(__file__), '../models')

class TriageExplainer:
    def __init__(self):
        self.risk_model = None
        self.explainer = None
        self.feature_names = None
    
    def load_explainer(self):
        if self.risk_model is None:
            model_path = os.path.join(MODEL_DIR, 'risk_model.joblib')
            feature_path = os.path.join(MODEL_DIR, 'feature_names.joblib')
            
            if os.path.exists(model_path):
                self.risk_model = joblib.load(model_path)
                
                # Check XGBoost version compatibility
                # TreeExplainer works best with booster object
                if hasattr(self.risk_model, 'get_booster'):
                    self.explainer = shap.TreeExplainer(self.risk_model)
                else: 
                     # Fallback for generic models if possible
                    self.explainer = shap.Explainer(self.risk_model)
            
            if os.path.exists(feature_path):
                self.feature_names = joblib.load(feature_path)

    def explain_prediction(self, X_transformed, top_k=5):
        if self.explainer is None:
            self.load_explainer()
            if self.explainer is None:
                return {}

        try:
            shap_values = self.explainer.shap_values(X_transformed)
        except Exception as e:
            print(f"SHAP calculation error: {e}")
            return {}
        
        explanations = {}
        
        # Handle SHAP return types (list for multiclass, array for binary)
        mean_abs_shap = None
        
        if isinstance(shap_values, list):
            # Multiclass: shap_values is a list of arrays, one for each class
            # We want important features across all classes
            # Shape of each element: (n_samples, n_features) -> (1, n_features) here
            # Sum abs values across classes
            combined = np.sum([np.abs(c) for c in shap_values], axis=0)
            mean_abs_shap = combined[0] 
        else:
            # Binary: shape (n_samples, n_features) -> (1, n_features)
            mean_abs_shap = np.abs(shap_values[0])

        # Get top K features
        if self.feature_names and len(self.feature_names) == len(mean_abs_shap):
            indices = np.argsort(mean_abs_shap)[::-1][:top_k]
            
            top_features = []
            for idx in indices:
                top_features.append({
                    'feature': self.feature_names[idx],
                    'importance': float(mean_abs_shap[idx])
                })
            
            explanations['top_features'] = top_features
            
        return explanations

