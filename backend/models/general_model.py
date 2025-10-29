"""
General Medical AI Model for MedAI-Pro
Multi-condition diagnosis using ensemble Random Forest + XGBoost
Target Accuracy: 85-90%
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer
import xgboost as xgb
from typing import Dict, List, Optional
from pathlib import Path
from loguru import logger
import joblib


class GeneralModel:
    """General medical diagnosis model using ensemble approach"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.rf_model = None
        self.xgb_model = None
        self.symptom_encoder = MultiLabelBinarizer()
        self.disease_encoder = LabelEncoder()
        
        # Common diseases
        self.diseases = [
            'Common Cold', 'Flu', 'Migraine', 'Hypertension', 'Diabetes',
            'Asthma', 'Bronchitis', 'Sinusitis', 'Allergic Rhinitis',
            'Urinary Tract Infection', 'Gastroenteritis', 'Anemia',
            'Arthritis', 'Thyroid Disorder', 'Anxiety', 'Depression'
        ]
        
        # Common symptoms
        self.all_symptoms = [
            'fever', 'cough', 'fatigue', 'headache', 'body_ache', 'sore_throat',
            'runny_nose', 'shortness_of_breath', 'chest_pain', 'nausea',
            'vomiting', 'diarrhea', 'abdominal_pain', 'dizziness', 'weakness',
            'joint_pain', 'muscle_pain', 'rash', 'sweating', 'chills',
            'loss_of_appetite', 'weight_loss', 'frequent_urination', 'thirst',
            'blurred_vision', 'numbness', 'tingling', 'anxiety', 'mood_changes'
        ]
        
        self.severity_map = {
            'Common Cold': 'low', 'Flu': 'medium', 'Migraine': 'medium',
            'Hypertension': 'high', 'Diabetes': 'high', 'Asthma': 'high',
            'Bronchitis': 'medium', 'Sinusitis': 'low', 'Allergic Rhinitis': 'low',
            'Urinary Tract Infection': 'medium', 'Gastroenteritis': 'medium',
            'Anemia': 'medium', 'Arthritis': 'medium', 'Thyroid Disorder': 'medium',
            'Anxiety': 'medium', 'Depression': 'medium'
        }
        
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
            logger.info(f"✅ General model loaded from {model_path}")
    
    def train(self, data_path: str):
        """Train the general medical model"""
        logger.info("🚀 Starting general model training...")
        
        # Load disease-symptom dataset
        df = pd.read_csv(data_path)
        
        # Prepare data
        X = []
        y = []
        
        for _, row in df.iterrows():
            disease = row['Disease']
            symptoms = [s.strip().lower().replace(' ', '_') for s in row['Symptom'].split(',')]
            
            X.append(symptoms)
            y.append(disease)
        
        # Encode symptoms
        X_encoded = self.symptom_encoder.fit_transform(X)
        
        # Encode diseases
        y_encoded = self.disease_encoder.fit_transform(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_encoded, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        # Train Random Forest
        logger.info("Training Random Forest...")
        self.rf_model = RandomForestClassifier(
            n_estimators=200,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        self.rf_model.fit(X_train, y_train)
        
        # Train XGBoost
        logger.info("Training XGBoost...")
        self.xgb_model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=10,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric='mlogloss'
        )
        self.xgb_model.fit(X_train, y_train)
        
        # Evaluate
        rf_acc = self.rf_model.score(X_test, y_test)
        xgb_acc = self.xgb_model.score(X_test, y_test)
        
        logger.info(f"Random Forest Accuracy: {rf_acc*100:.2f}%")
        logger.info(f"XGBoost Accuracy: {xgb_acc*100:.2f}%")
        
        # Save models
        self.save_model('models/general_ensemble')
        
        return max(rf_acc, xgb_acc) * 100
    
    def predict(self, symptoms: List[str]) -> Dict:
        """Make prediction based on symptoms"""
        # Normalize symptoms
        normalized_symptoms = [s.strip().lower().replace(' ', '_') for s in symptoms]
        
        # Encode symptoms
        symptom_vector = self.symptom_encoder.transform([normalized_symptoms])
        
        # Get predictions from both models
        rf_probs = self.rf_model.predict_proba(symptom_vector)[0]
        xgb_probs = self.xgb_model.predict_proba(symptom_vector)[0]
        
        # Ensemble: average probabilities
        ensemble_probs = (rf_probs + xgb_probs) / 2
        
        # Get top predictions
        top_indices = np.argsort(ensemble_probs)[::-1][:3]
        
        predicted_class = top_indices[0]
        confidence = ensemble_probs[predicted_class]
        
        disease_name = self.disease_encoder.inverse_transform([predicted_class])[0]
        
        result = {
            'primary_prediction': disease_name,
            'confidence_score': float(confidence),
            'severity_level': self.severity_map.get(disease_name, 'medium'),
            'all_predictions': {
                self.disease_encoder.inverse_transform([i])[0]: float(ensemble_probs[i])
                for i in top_indices
            },
            'recommendations': self._get_recommendations(disease_name),
            'suggested_specialists': self._get_specialists(disease_name)
        }
        
        return result
    
    def _get_recommendations(self, disease: str) -> List[str]:
        """Get medical recommendations"""
        recommendations_map = {
            'Common Cold': [
                "Rest and stay hydrated",
                "Over-the-counter cold medications",
                "Warm fluids and soups",
                "Usually resolves in 7-10 days"
            ],
            'Flu': [
                "Rest and isolation",
                "Antiviral medications if prescribed",
                "Stay hydrated",
                "Monitor for complications"
            ],
            'Migraine': [
                "Rest in dark, quiet room",
                "Pain relievers as prescribed",
                "Identify and avoid triggers",
                "Consult neurologist if frequent"
            ],
            'Hypertension': [
                "Regular blood pressure monitoring",
                "Low-sodium diet",
                "Regular exercise",
                "Medication compliance",
                "Stress management"
            ],
            'Diabetes': [
                "Regular blood sugar monitoring",
                "Balanced diet",
                "Regular exercise",
                "Medication compliance",
                "Annual eye and foot exams"
            ],
            'Asthma': [
                "Avoid triggers",
                "Use prescribed inhalers",
                "Have rescue inhaler available",
                "Regular pulmonologist visits"
            ]
        }
        
        return recommendations_map.get(disease, [
            "Consult a healthcare provider",
            "Follow prescribed treatment",
            "Monitor symptoms"
        ])
    
    def _get_specialists(self, disease: str) -> List[str]:
        """Get recommended specialists"""
        specialist_map = {
            'Migraine': ['Neurologist'],
            'Hypertension': ['Cardiologist', 'General Physician'],
            'Diabetes': ['Endocrinologist', 'Diabetologist'],
            'Asthma': ['Pulmonologist'],
            'Bronchitis': ['Pulmonologist'],
            'Arthritis': ['Rheumatologist'],
            'Thyroid Disorder': ['Endocrinologist'],
            'Anxiety': ['Psychiatrist', 'Psychologist'],
            'Depression': ['Psychiatrist', 'Psychologist'],
            'Urinary Tract Infection': ['Urologist', 'General Physician']
        }
        
        return specialist_map.get(disease, ['General Physician'])
    
    def save_model(self, path: str):
        """Save models"""
        Path(path).mkdir(parents=True, exist_ok=True)
        joblib.dump(self.rf_model, f"{path}/rf_model.pkl")
        joblib.dump(self.xgb_model, f"{path}/xgb_model.pkl")
        joblib.dump(self.symptom_encoder, f"{path}/symptom_encoder.pkl")
        joblib.dump(self.disease_encoder, f"{path}/disease_encoder.pkl")
        logger.info(f"Models saved to {path}")
    
    def load_model(self, path: str):
        """Load models"""
        self.rf_model = joblib.load(f"{path}/rf_model.pkl")
        self.xgb_model = joblib.load(f"{path}/xgb_model.pkl")
        self.symptom_encoder = joblib.load(f"{path}/symptom_encoder.pkl")
        self.disease_encoder = joblib.load(f"{path}/disease_encoder.pkl")



# Orchestrator-compatible training function
def train_model(data_path: str) -> dict:
    """Train GeneralModel and return accuracy in a dict."""
    model = GeneralModel()
    acc = model.train(data_path)
    return {"accuracy": acc}

if __name__ == "__main__":
    model = GeneralModel()
    logger.info("✅ General model module ready")

