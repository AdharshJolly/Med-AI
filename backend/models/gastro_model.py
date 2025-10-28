"""
Gastroenterology AI Model for MedAI-Pro
GI symptoms classification using XGBoost and TabNet
Target Accuracy: 85-90%
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import xgboost as xgb
from pytorch_tabnet.tab_model import TabNetClassifier
from typing import Dict, List, Optional
from pathlib import Path
from loguru import logger
import joblib


class GastroModel:
    """Gastroenterology diagnosis model using ensemble of XGBoost and TabNet"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.xgb_model = None
        self.tabnet_model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        self.class_names = [
            'Normal',
            'GERD',
            'IBS',
            'Gastritis',
            'Peptic Ulcer',
            'Crohns Disease',
            'Ulcerative Colitis',
            'Celiac Disease',
            'Pancreatitis'
        ]
        
        self.severity_map = {
            'Normal': 'low',
            'GERD': 'medium',
            'IBS': 'medium',
            'Gastritis': 'medium',
            'Peptic Ulcer': 'high',
            'Crohns Disease': 'high',
            'Ulcerative Colitis': 'high',
            'Celiac Disease': 'medium',
            'Pancreatitis': 'critical'
        }
        
        self.feature_names = [
            'age', 'gender', 'abdominal_pain', 'nausea', 'vomiting',
            'diarrhea', 'constipation', 'bloating', 'heartburn',
            'weight_loss', 'blood_in_stool', 'fever'
        ]
        
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
            logger.info(f"✅ Gastro model loaded from {model_path}")
    
    def train(self, data_path: str, epochs: int = 100):
        """Train the gastroenterology model"""
        logger.info("🚀 Starting gastroenterology model training...")
        
        # Load data
        df = pd.read_csv(data_path)
        
        # Prepare features and labels
        X = df[self.feature_names].copy()
        
        # Encode gender
        X['gender'] = X['gender'].map({'M': 0, 'F': 1})
        
        # Encode labels
        y = self.label_encoder.fit_transform(df['diagnosis'])
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train XGBoost
        logger.info("Training XGBoost model...")
        self.xgb_model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            objective='multi:softmax',
            num_class=len(self.class_names),
            random_state=42,
            eval_metric='mlogloss'
        )
        
        self.xgb_model.fit(
            X_train_scaled, y_train,
            eval_set=[(X_test_scaled, y_test)],
            verbose=False
        )
        
        # Train TabNet
        logger.info("Training TabNet model...")
        self.tabnet_model = TabNetClassifier(
            n_d=64,
            n_a=64,
            n_steps=5,
            gamma=1.5,
            n_independent=2,
            n_shared=2,
            optimizer_fn=torch.optim.Adam,
            optimizer_params=dict(lr=2e-2),
            scheduler_params={"step_size": 50, "gamma": 0.9},
            scheduler_fn=torch.optim.lr_scheduler.StepLR,
            mask_type='entmax'
        )
        
        self.tabnet_model.fit(
            X_train_scaled, y_train,
            eval_set=[(X_test_scaled, y_test)],
            max_epochs=epochs,
            patience=20,
            batch_size=256,
            virtual_batch_size=128,
            eval_metric=['accuracy']
        )
        
        # Evaluate
        xgb_acc = self.xgb_model.score(X_test_scaled, y_test)
        tabnet_preds = self.tabnet_model.predict(X_test_scaled)
        tabnet_acc = (tabnet_preds == y_test).mean()
        
        logger.info(f"XGBoost Accuracy: {xgb_acc*100:.2f}%")
        logger.info(f"TabNet Accuracy: {tabnet_acc*100:.2f}%")
        
        # Save models
        self.save_model('models/gastro_ensemble')
        
        return max(xgb_acc, tabnet_acc) * 100
    
    def predict(self, symptoms: Dict) -> Dict:
        """Make prediction on GI symptoms"""
        # Prepare input
        input_data = pd.DataFrame([symptoms])
        
        # Ensure all features are present
        for feature in self.feature_names:
            if feature not in input_data.columns:
                input_data[feature] = 0
        
        # Encode gender
        if 'gender' in input_data.columns:
            input_data['gender'] = input_data['gender'].map({'M': 0, 'F': 1, 0: 0, 1: 1})
        
        # Select and order features
        input_data = input_data[self.feature_names]
        
        # Scale
        input_scaled = self.scaler.transform(input_data)
        
        # Get predictions from both models
        xgb_probs = self.xgb_model.predict_proba(input_scaled)[0]
        tabnet_probs = self.tabnet_model.predict_proba(input_scaled)[0]
        
        # Ensemble: average probabilities
        ensemble_probs = (xgb_probs + tabnet_probs) / 2
        
        predicted_class = np.argmax(ensemble_probs)
        confidence = ensemble_probs[predicted_class]
        
        result = {
            'primary_prediction': self.class_names[predicted_class],
            'confidence_score': float(confidence),
            'severity_level': self.severity_map[self.class_names[predicted_class]],
            'all_predictions': {
                self.class_names[i]: float(ensemble_probs[i])
                for i in range(len(self.class_names))
            },
            'recommendations': self._get_recommendations(predicted_class)
        }
        
        return result
    
    def _get_recommendations(self, class_idx: int) -> List[str]:
        """Get medical recommendations"""
        recommendations_map = {
            0: ["Maintain healthy diet", "Regular exercise", "Stay hydrated"],
            1: ["Avoid spicy and acidic foods", "Elevate head while sleeping", "Consult gastroenterologist"],
            2: ["Stress management", "Dietary modifications", "Probiotics may help"],
            3: ["Avoid NSAIDs", "Eat smaller meals", "Reduce alcohol consumption"],
            4: ["Urgent gastroenterologist consultation", "Endoscopy recommended", "Avoid NSAIDs"],
            5: ["Specialist consultation required", "Anti-inflammatory diet", "Regular monitoring"],
            6: ["Specialist consultation required", "Colonoscopy recommended", "Medication compliance"],
            7: ["Gluten-free diet essential", "Nutritionist consultation", "Regular follow-ups"],
            8: ["URGENT: Hospital admission may be required", "NPO (nothing by mouth)", "IV fluids needed"]
        }
        
        return recommendations_map.get(class_idx, ["Consult a gastroenterologist"])
    
    def save_model(self, path: str):
        """Save model"""
        Path(path).mkdir(parents=True, exist_ok=True)
        joblib.dump(self.xgb_model, f"{path}/xgb_model.pkl")
        self.tabnet_model.save_model(f"{path}/tabnet_model")
        joblib.dump(self.scaler, f"{path}/scaler.pkl")
        joblib.dump(self.label_encoder, f"{path}/label_encoder.pkl")
        logger.info(f"Models saved to {path}")
    
    def load_model(self, path: str):
        """Load model"""
        self.xgb_model = joblib.load(f"{path}/xgb_model.pkl")
        self.tabnet_model = TabNetClassifier()
        self.tabnet_model.load_model(f"{path}/tabnet_model.zip")
        self.scaler = joblib.load(f"{path}/scaler.pkl")
        self.label_encoder = joblib.load(f"{path}/label_encoder.pkl")


import torch

if __name__ == "__main__":
    model = GastroModel()
    logger.info("✅ Gastroenterology model module ready")

