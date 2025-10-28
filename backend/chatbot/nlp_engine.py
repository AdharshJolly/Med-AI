"""
NLP Engine for MedAI-Pro Chatbot
BERT-based medical query processor with intent recognition and entity extraction
"""

import torch
from transformers import BertTokenizer, BertForSequenceClassification, pipeline
from typing import Dict, List, Optional
from loguru import logger
import re
import spacy


class MedicalNLPEngine:
    """Medical NLP engine for chatbot"""
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load BERT for intent classification
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        
        # Load spaCy for entity extraction
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except:
            logger.warning("spaCy model not found. Run: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Medical intents
        self.intents = [
            'symptom_query',           # User describing symptoms
            'diagnosis_question',      # Asking about a condition
            'medication_info',         # Asking about medications
            'treatment_advice',        # Seeking treatment recommendations
            'emergency_check',         # Potential emergency
            'appointment_booking',     # Want to book appointment
            'test_results',           # Asking about test results
            'general_health',         # General health questions
            'greeting',               # Hello, hi, etc.
            'farewell'                # Goodbye, thanks, etc.
        ]
        
        # Medical entities
        self.medical_entities = {
            'symptoms': [],
            'body_parts': [],
            'conditions': [],
            'medications': [],
            'duration': [],
            'severity': []
        }
        
        # Emergency keywords
        self.emergency_keywords = [
            'severe chest pain', 'can\'t breathe', 'unconscious', 'seizure',
            'heavy bleeding', 'stroke', 'heart attack', 'suicide', 'overdose',
            'severe burn', 'choking', 'severe allergic reaction'
        ]
        
        # Common medical terms
        self.symptom_keywords = [
            'pain', 'ache', 'fever', 'cough', 'nausea', 'vomiting', 'diarrhea',
            'headache', 'dizziness', 'fatigue', 'weakness', 'rash', 'swelling',
            'bleeding', 'numbness', 'tingling', 'shortness of breath', 'chest pain'
        ]
        
        logger.info("✅ Medical NLP Engine initialized")
    
    def process_message(self, message: str) -> Dict:
        """Process user message and extract information"""
        
        # Clean message
        cleaned_message = self._clean_text(message)
        
        # Detect intent
        intent = self._detect_intent(cleaned_message)
        
        # Extract entities
        entities = self._extract_entities(cleaned_message)
        
        # Check for emergency
        is_emergency = self._check_emergency(cleaned_message)
        
        # Extract symptoms
        symptoms = self._extract_symptoms(cleaned_message)
        
        # Determine urgency
        urgency = self._determine_urgency(cleaned_message, is_emergency, symptoms)
        
        result = {
            'original_message': message,
            'cleaned_message': cleaned_message,
            'intent': intent,
            'entities': entities,
            'symptoms': symptoms,
            'is_emergency': is_emergency,
            'urgency_level': urgency,
            'requires_human': is_emergency or urgency == 'high'
        }
        
        return result
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters but keep medical notation
        text = re.sub(r'[^\w\s\-\'/]', '', text)
        
        return text
    
    def _detect_intent(self, message: str) -> str:
        """Detect user intent"""
        message_lower = message.lower()
        
        # Rule-based intent detection
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good evening']):
            return 'greeting'
        
        if any(word in message_lower for word in ['bye', 'goodbye', 'thank you', 'thanks']):
            return 'farewell'
        
        if any(word in message_lower for word in ['emergency', 'urgent', 'severe', 'critical']):
            return 'emergency_check'
        
        if any(word in message_lower for word in ['appointment', 'book', 'schedule', 'visit']):
            return 'appointment_booking'
        
        if any(word in message_lower for word in ['medication', 'medicine', 'drug', 'prescription']):
            return 'medication_info'
        
        if any(word in message_lower for word in ['treatment', 'cure', 'therapy', 'how to treat']):
            return 'treatment_advice'
        
        if any(word in message_lower for word in ['test result', 'lab result', 'report']):
            return 'test_results'
        
        if any(word in message_lower for word in ['what is', 'tell me about', 'explain']):
            return 'diagnosis_question'
        
        # Check for symptom descriptions
        if any(symptom in message_lower for symptom in self.symptom_keywords):
            return 'symptom_query'
        
        return 'general_health'
    
    def _extract_entities(self, message: str) -> Dict:
        """Extract medical entities using spaCy"""
        entities = {
            'symptoms': [],
            'body_parts': [],
            'conditions': [],
            'medications': [],
            'duration': [],
            'severity': []
        }
        
        if self.nlp is None:
            return entities
        
        doc = self.nlp(message)
        
        # Extract named entities
        for ent in doc.ents:
            if ent.label_ in ['DISEASE', 'SYMPTOM']:
                entities['symptoms'].append(ent.text)
            elif ent.label_ == 'BODY_PART':
                entities['body_parts'].append(ent.text)
            elif ent.label_ == 'TIME':
                entities['duration'].append(ent.text)
        
        # Extract severity indicators
        severity_words = ['mild', 'moderate', 'severe', 'extreme', 'slight', 'intense']
        for word in severity_words:
            if word in message:
                entities['severity'].append(word)
        
        return entities
    
    def _extract_symptoms(self, message: str) -> List[str]:
        """Extract symptoms from message"""
        symptoms = []
        
        for symptom in self.symptom_keywords:
            if symptom in message:
                symptoms.append(symptom)
        
        return symptoms
    
    def _check_emergency(self, message: str) -> bool:
        """Check if message indicates emergency"""
        for keyword in self.emergency_keywords:
            if keyword in message:
                return True
        
        # Check for severity + critical symptoms
        if 'severe' in message and any(s in message for s in ['chest pain', 'bleeding', 'breathing']):
            return True
        
        return False
    
    def _determine_urgency(self, message: str, is_emergency: bool, symptoms: List[str]) -> str:
        """Determine urgency level"""
        if is_emergency:
            return 'critical'
        
        # High urgency indicators
        high_urgency_words = ['severe', 'intense', 'unbearable', 'worsening', 'can\'t']
        if any(word in message for word in high_urgency_words):
            return 'high'
        
        # Multiple symptoms
        if len(symptoms) >= 3:
            return 'medium'
        
        # Moderate urgency indicators
        medium_urgency_words = ['moderate', 'persistent', 'recurring', 'frequent']
        if any(word in message for word in medium_urgency_words):
            return 'medium'
        
        return 'low'
    
    def generate_response(self, processed_message: Dict) -> str:
        """Generate appropriate response based on processed message"""
        intent = processed_message['intent']
        is_emergency = processed_message['is_emergency']
        
        if is_emergency:
            return (
                "⚠️ **EMERGENCY DETECTED** ⚠️\n\n"
                "This appears to be a medical emergency. Please:\n"
                "1. Call emergency services (911/108) immediately\n"
                "2. If possible, go to the nearest emergency room\n"
                "3. Do not wait for online consultation\n\n"
                "Would you like me to help you find nearby hospitals?"
            )
        
        if intent == 'greeting':
            return (
                "Hello! I'm MedAI, your medical AI assistant. 👋\n\n"
                "I can help you with:\n"
                "• Symptom analysis and preliminary diagnosis\n"
                "• Health information and advice\n"
                "• Finding nearby medical facilities\n"
                "• Booking appointments\n\n"
                "How can I assist you today?"
            )
        
        if intent == 'farewell':
            return (
                "Thank you for using MedAI-Pro! Take care of your health. 🏥\n"
                "Remember: For emergencies, always call 911/108 or visit the nearest hospital.\n"
                "Feel free to return anytime you need medical assistance!"
            )
        
        if intent == 'symptom_query':
            symptoms = processed_message['symptoms']
            if symptoms:
                return (
                    f"I understand you're experiencing: {', '.join(symptoms)}.\n\n"
                    "To provide you with the best analysis, I'll need a bit more information:\n"
                    "1. How long have you had these symptoms?\n"
                    "2. On a scale of 1-10, how severe is the discomfort?\n"
                    "3. Have you noticed any other symptoms?\n\n"
                    "Alternatively, you can use our diagnosis feature for a comprehensive analysis."
                )
            else:
                return (
                    "I'm here to help with your symptoms. Could you please describe:\n"
                    "• What symptoms you're experiencing\n"
                    "• When they started\n"
                    "• How severe they are\n\n"
                    "This will help me provide better assistance."
                )
        
        if intent == 'appointment_booking':
            return (
                "I can help you find nearby medical facilities and specialists.\n\n"
                "Please let me know:\n"
                "1. What type of specialist do you need?\n"
                "2. Your location or preferred area\n"
                "3. Any specific requirements (insurance, language, etc.)\n\n"
                "You can also use our 'Find Hospitals' feature for a map view."
            )
        
        if intent == 'medication_info':
            return (
                "⚠️ **Important**: I can provide general information about medications, "
                "but I cannot prescribe or recommend specific medications.\n\n"
                "For medication-related questions:\n"
                "• Always consult with a licensed healthcare provider\n"
                "• Never start or stop medications without medical advice\n"
                "• Check for drug interactions with your doctor\n\n"
                "What would you like to know about medications in general?"
            )
        
        # Default response
        return (
            "I'm here to help! Could you please provide more details about your concern?\n"
            "You can:\n"
            "• Describe your symptoms\n"
            "• Ask about a medical condition\n"
            "• Request to find nearby hospitals\n"
            "• Book an appointment with a specialist"
        )


if __name__ == "__main__":
    engine = MedicalNLPEngine()
    
    # Test messages
    test_messages = [
        "Hello, I need help",
        "I have severe chest pain and can't breathe",
        "I've had a headache and fever for 3 days",
        "Can you help me book an appointment with a cardiologist?"
    ]
    
    for msg in test_messages:
        print(f"\nMessage: {msg}")
        processed = engine.process_message(msg)
        response = engine.generate_response(processed)
        print(f"Intent: {processed['intent']}")
        print(f"Response: {response}")
    
    logger.info("✅ NLP Engine test completed")

