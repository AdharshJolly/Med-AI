"""
Intelligent Router Model for MedAI-Pro
BERT-based routing system to direct inputs to appropriate specialty models
Target Accuracy: 90%+
"""

import torch
import torch.nn as nn
from transformers import BertTokenizer, BertModel, BertForSequenceClassification
from typing import Dict, List, Optional, Union
from loguru import logger
from pathlib import Path
import numpy as np


class MedicalRouter:
    """BERT-based intelligent router for medical specialties"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load BERT tokenizer and model
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.model = BertForSequenceClassification.from_pretrained(
            'bert-base-uncased',
            num_labels=6
        ).to(self.device)
        
        # Specialty classes
        self.specialties = [
            'cardiology',      # 0: Heart, ECG, cardiac
            'dermatology',     # 1: Skin, rash, lesion
            'respiratory',     # 2: Lungs, breathing, chest
            'orthopedics',     # 3: Bones, fracture, joints
            'gastroenterology',# 4: Stomach, GI, digestive
            'general'          # 5: General symptoms
        ]
        
        # Keyword mappings for rule-based fallback
        self.specialty_keywords = {
            'cardiology': [
                'heart', 'cardiac', 'ecg', 'ekg', 'chest pain', 'palpitation',
                'arrhythmia', 'myocardial', 'angina', 'cardiovascular', 'pulse'
            ],
            'dermatology': [
                'skin', 'rash', 'lesion', 'mole', 'acne', 'eczema', 'psoriasis',
                'melanoma', 'dermatitis', 'itching', 'hives', 'pigmentation'
            ],
            'respiratory': [
                'lung', 'breathing', 'cough', 'pneumonia', 'asthma', 'bronchitis',
                'chest xray', 'shortness of breath', 'wheezing', 'respiratory'
            ],
            'orthopedics': [
                'bone', 'fracture', 'joint', 'arthritis', 'sprain', 'xray',
                'musculoskeletal', 'limb', 'spine', 'orthopedic', 'trauma'
            ],
            'gastroenterology': [
                'stomach', 'abdominal', 'digestive', 'intestine', 'bowel',
                'nausea', 'vomiting', 'diarrhea', 'constipation', 'gastric',
                'liver', 'pancreas', 'gi', 'gastrointestinal'
            ]
        }
        
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
            logger.info(f"✅ Router model loaded from {model_path}")
        else:
            logger.warning("⚠️ Using pre-trained BERT. Fine-tune for better routing.")
    
    def route_by_keywords(self, text: str) -> str:
        """Rule-based routing using keyword matching"""
        text_lower = text.lower()
        
        specialty_scores = {specialty: 0 for specialty in self.specialties[:-1]}
        
        for specialty, keywords in self.specialty_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    specialty_scores[specialty] += 1
        
        # Get specialty with highest score
        max_score = max(specialty_scores.values())
        
        if max_score > 0:
            for specialty, score in specialty_scores.items():
                if score == max_score:
                    return specialty
        
        return 'general'  # Default to general
    
    def route_by_input_type(self, input_data: Dict) -> str:
        """Route based on input type"""
        if 'ecg_data' in input_data or 'ecg_file' in input_data:
            return 'cardiology'
        
        if 'image' in input_data or 'image_file' in input_data:
            # Need to determine image type
            if 'description' in input_data:
                desc = input_data['description'].lower()
                if any(kw in desc for kw in ['skin', 'rash', 'lesion', 'mole']):
                    return 'dermatology'
                elif any(kw in desc for kw in ['chest', 'lung', 'xray']):
                    return 'respiratory'
                elif any(kw in desc for kw in ['bone', 'fracture', 'joint']):
                    return 'orthopedics'
        
        if 'symptoms' in input_data:
            symptoms_text = ' '.join(input_data['symptoms']) if isinstance(input_data['symptoms'], list) else input_data['symptoms']
            return self.route_by_keywords(symptoms_text)
        
        if 'text' in input_data or 'description' in input_data:
            text = input_data.get('text', input_data.get('description', ''))
            return self.route_by_keywords(text)
        
        return 'general'
    
    def route_by_bert(self, text: str) -> str:
        """BERT-based intelligent routing"""
        # Tokenize input
        inputs = self.tokenizer(
            text,
            return_tensors='pt',
            truncation=True,
            padding=True,
            max_length=512
        ).to(self.device)
        
        # Get prediction
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=1)
            predicted_class = torch.argmax(probabilities, dim=1).item()
        
        return self.specialties[predicted_class]
    
    def route(self, input_data: Union[str, Dict]) -> Dict:
        """
        Main routing function
        Returns specialty and confidence
        """
        # Convert string to dict
        if isinstance(input_data, str):
            input_data = {'text': input_data}
        
        # Try input type routing first
        specialty_by_type = self.route_by_input_type(input_data)
        
        # Get text for BERT routing
        text = self._extract_text(input_data)
        
        if text:
            # Use BERT for text-based routing
            try:
                specialty_by_bert = self.route_by_bert(text)
            except Exception as e:
                logger.warning(f"BERT routing failed: {e}")
                specialty_by_bert = self.route_by_keywords(text)
            
            # Use keyword-based as fallback
            specialty_by_keywords = self.route_by_keywords(text)
            
            # Voting mechanism
            votes = [specialty_by_type, specialty_by_bert, specialty_by_keywords]
            specialty = max(set(votes), key=votes.count)
            
            # Calculate confidence based on agreement
            confidence = votes.count(specialty) / len(votes)
        else:
            specialty = specialty_by_type
            confidence = 0.8
        
        result = {
            'specialty': specialty,
            'confidence': confidence,
            'routing_method': 'ensemble',
            'alternative_specialties': self._get_alternatives(specialty)
        }
        
        logger.info(f"Routed to {specialty} with confidence {confidence:.2f}")
        
        return result
    
    def _extract_text(self, input_data: Dict) -> str:
        """Extract text from various input formats"""
        text_parts = []
        
        if 'text' in input_data:
            text_parts.append(input_data['text'])
        
        if 'description' in input_data:
            text_parts.append(input_data['description'])
        
        if 'symptoms' in input_data:
            if isinstance(input_data['symptoms'], list):
                text_parts.extend(input_data['symptoms'])
            else:
                text_parts.append(str(input_data['symptoms']))
        
        if 'complaint' in input_data:
            text_parts.append(input_data['complaint'])
        
        return ' '.join(text_parts)
    
    def _get_alternatives(self, primary_specialty: str) -> List[str]:
        """Get alternative specialties"""
        alternatives_map = {
            'cardiology': ['respiratory', 'general'],
            'dermatology': ['general'],
            'respiratory': ['cardiology', 'general'],
            'orthopedics': ['general'],
            'gastroenterology': ['general'],
            'general': ['cardiology', 'respiratory', 'gastroenterology']
        }
        
        return alternatives_map.get(primary_specialty, ['general'])
    
    def train(self, training_data: List[Dict], epochs: int = 3):
        """Fine-tune BERT for medical routing"""
        logger.info("🚀 Fine-tuning BERT for medical routing...")
        
        from torch.utils.data import Dataset, DataLoader
        
        class RoutingDataset(Dataset):
            def __init__(self, data, tokenizer):
                self.data = data
                self.tokenizer = tokenizer
            
            def __len__(self):
                return len(self.data)
            
            def __getitem__(self, idx):
                item = self.data[idx]
                encoding = self.tokenizer(
                    item['text'],
                    truncation=True,
                    padding='max_length',
                    max_length=512,
                    return_tensors='pt'
                )
                return {
                    'input_ids': encoding['input_ids'].flatten(),
                    'attention_mask': encoding['attention_mask'].flatten(),
                    'labels': torch.tensor(item['label'])
                }
        
        dataset = RoutingDataset(training_data, self.tokenizer)
        dataloader = DataLoader(dataset, batch_size=16, shuffle=True)
        
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=2e-5)
        
        self.model.train()
        for epoch in range(epochs):
            total_loss = 0
            for batch in dataloader:
                optimizer.zero_grad()
                
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                loss = outputs.loss
                total_loss += loss.item()
                
                loss.backward()
                optimizer.step()
            
            avg_loss = total_loss / len(dataloader)
            logger.info(f"Epoch {epoch+1}/{epochs} - Loss: {avg_loss:.4f}")
        
        self.save_model('models/router_bert')
        logger.info("✅ Router model training completed")
    
    def save_model(self, path: str):
        """Save model"""
        Path(path).mkdir(parents=True, exist_ok=True)
        self.model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)
    
    def load_model(self, path: str):
        """Load model"""
        self.model = BertForSequenceClassification.from_pretrained(path).to(self.device)
        self.tokenizer = BertTokenizer.from_pretrained(path)



# Orchestrator-compatible training function
def train_model(data_path: str, epochs: int = 3) -> dict:
    """Train MedicalRouter and return accuracy in a dict."""
    import pandas as pd
    model = MedicalRouter()
    # Expecting data_path to be a CSV with 'text' and 'label' columns
    df = pd.read_csv(data_path)
    training_data = [
        {"text": row["text"], "label": int(row["label"])}
        for _, row in df.iterrows()
    ]
    model.train(training_data, epochs=epochs)
    # No direct accuracy, so return empty dict or implement validation if available
    return {"accuracy": None}

if __name__ == "__main__":
    router = MedicalRouter()
    # Test routing
    test_cases = [
        "I have chest pain and palpitations",
        "There's a rash on my arm",
        "I'm having difficulty breathing",
        "My ankle is swollen after a fall",
        "I have severe abdominal pain and nausea"
    ]
    for case in test_cases:
        result = router.route(case)
        print(f"Input: {case}")
        print(f"Routed to: {result['specialty']} (confidence: {result['confidence']:.2f})\n")
    logger.info("✅ Router model module ready")

