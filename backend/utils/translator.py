"""
Multi-Language Translation Service for MedAI-Pro
Supports 11 Indian languages + English using Google Translate API
"""

from typing import Dict, List, Optional
from deep_translator import GoogleTranslator
from loguru import logger
import json
from functools import lru_cache

# Supported languages configuration
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi (हिंदी)',
    'bn': 'Bengali (বাংলা)',
    'te': 'Telugu (తెలుగు)',
    'mr': 'Marathi (मराठी)',
    'ta': 'Tamil (தமிழ்)',
    'gu': 'Gujarati (ગુજરાતી)',
    'kn': 'Kannada (ಕನ್ನಡ)',
    'ml': 'Malayalam (മലയാളം)',
    'pa': 'Punjabi (ਪੰਜਾਬੀ)',
    'or': 'Odia (ଓଡ଼ିଆ)',
    'as': 'Assamese (অসমীয়া)'
}

# Medical terminology translations (for accuracy)
MEDICAL_TERMS = {
    'en': {
        'fever': 'fever',
        'cough': 'cough',
        'headache': 'headache',
        'pain': 'pain',
        'nausea': 'nausea',
        'vomiting': 'vomiting',
        'diarrhea': 'diarrhea',
        'fatigue': 'fatigue',
        'dizziness': 'dizziness',
        'chest_pain': 'chest pain',
        'shortness_of_breath': 'shortness of breath',
        'rash': 'rash',
        'swelling': 'swelling',
        'bleeding': 'bleeding',
        'weakness': 'weakness'
    },
    'hi': {
        'fever': 'बुखार',
        'cough': 'खांसी',
        'headache': 'सिरदर्द',
        'pain': 'दर्द',
        'nausea': 'मतली',
        'vomiting': 'उल्टी',
        'diarrhea': 'दस्त',
        'fatigue': 'थकान',
        'dizziness': 'चक्कर',
        'chest_pain': 'सीने में दर्द',
        'shortness_of_breath': 'सांस लेने में तकलीफ',
        'rash': 'चकत्ते',
        'swelling': 'सूजन',
        'bleeding': 'रक्तस्राव',
        'weakness': 'कमजोरी'
    },
    'bn': {
        'fever': 'জ্বর',
        'cough': 'কাশি',
        'headache': 'মাথাব্যথা',
        'pain': 'ব্যথা',
        'nausea': 'বমি বমি ভাব',
        'vomiting': 'বমি',
        'diarrhea': 'ডায়রিয়া',
        'fatigue': 'ক্লান্তি',
        'dizziness': 'মাথা ঘোরা',
        'chest_pain': 'বুকে ব্যথা',
        'shortness_of_breath': 'শ্বাসকষ্ট',
        'rash': 'ফুসকুড়ি',
        'swelling': 'ফোলা',
        'bleeding': 'রক্তপাত',
        'weakness': 'দুর্বলতা'
    },
    'te': {
        'fever': 'జ్వరం',
        'cough': 'దగ్గు',
        'headache': 'తలనొప్పి',
        'pain': 'నొప్పి',
        'nausea': 'వాంతులు',
        'vomiting': 'వాంతులు',
        'diarrhea': 'విరేచనాలు',
        'fatigue': 'అలసట',
        'dizziness': 'తల తిరగడం',
        'chest_pain': 'ఛాతీ నొప్పి',
        'shortness_of_breath': 'ఊపిరి ఆడకపోవడం',
        'rash': 'దద్దుర్లు',
        'swelling': 'వాపు',
        'bleeding': 'రక్తస్రావం',
        'weakness': 'బలహీనత'
    },
    'ta': {
        'fever': 'காய்ச்சல்',
        'cough': 'இருமல்',
        'headache': 'தலைவலி',
        'pain': 'வலி',
        'nausea': 'குமட்டல்',
        'vomiting': 'வாந்தி',
        'diarrhea': 'வயிற்றுப்போக்கு',
        'fatigue': 'சோர்வு',
        'dizziness': 'தலைசுற்றல்',
        'chest_pain': 'மார்பு வலி',
        'shortness_of_breath': 'மூச்சுத் திணறல்',
        'rash': 'தடிப்பு',
        'swelling': 'வீக்கம்',
        'bleeding': 'இரத்தப்போக்கு',
        'weakness': 'பலவீனம்'
    }
}


class MedicalTranslator:
    """Medical-aware translation service"""
    
    def __init__(self):
        self.translators = {}
        self._initialize_translators()
        logger.info(f"✅ Medical translator initialized for {len(SUPPORTED_LANGUAGES)} languages")
    
    def _initialize_translators(self):
        """Initialize translators for all language pairs"""
        for lang_code in SUPPORTED_LANGUAGES.keys():
            if lang_code != 'en':
                try:
                    self.translators[f'en-{lang_code}'] = GoogleTranslator(source='en', target=lang_code)
                    self.translators[f'{lang_code}-en'] = GoogleTranslator(source=lang_code, target='en')
                except Exception as e:
                    logger.warning(f"Failed to initialize translator for {lang_code}: {e}")
    
    @lru_cache(maxsize=1000)
    def translate(self, text: str, source_lang: str = 'en', target_lang: str = 'hi') -> str:
        """
        Translate text from source to target language
        Uses caching for frequently translated phrases
        """
        if not text or source_lang == target_lang:
            return text
        
        translator_key = f'{source_lang}-{target_lang}'
        
        try:
            if translator_key in self.translators:
                translated = self.translators[translator_key].translate(text)
                return translated
            else:
                # Fallback to creating new translator
                translator = GoogleTranslator(source=source_lang, target=target_lang)
                translated = translator.translate(text)
                return translated
        except Exception as e:
            logger.error(f"Translation error ({source_lang} -> {target_lang}): {e}")
            return text  # Return original text on error
    
    def translate_medical_term(self, term: str, target_lang: str = 'hi') -> str:
        """
        Translate medical terminology with high accuracy
        Uses predefined medical dictionary when available
        """
        # Check if term exists in medical dictionary
        term_key = term.lower().replace(' ', '_')
        
        if target_lang in MEDICAL_TERMS and term_key in MEDICAL_TERMS[target_lang]:
            return MEDICAL_TERMS[target_lang][term_key]
        
        # Fallback to general translation
        return self.translate(term, 'en', target_lang)
    
    def translate_symptoms(self, symptoms: List[str], target_lang: str = 'hi') -> List[str]:
        """Translate list of symptoms"""
        translated_symptoms = []
        for symptom in symptoms:
            translated = self.translate_medical_term(symptom, target_lang)
            translated_symptoms.append(translated)
        return translated_symptoms
    
    def translate_diagnosis_result(self, result: Dict, target_lang: str = 'hi') -> Dict:
        """
        Translate complete diagnosis result
        Preserves structure while translating text fields
        """
        translated_result = result.copy()
        
        # Translate main fields
        if 'primary_prediction' in result:
            translated_result['primary_prediction'] = self.translate(
                result['primary_prediction'], 'en', target_lang
            )
        
        if 'recommendations' in result and isinstance(result['recommendations'], list):
            translated_result['recommendations'] = [
                self.translate(rec, 'en', target_lang) for rec in result['recommendations']
            ]
        
        if 'lifestyle_advice' in result:
            translated_result['lifestyle_advice'] = self.translate(
                result['lifestyle_advice'], 'en', target_lang
            )
        
        if 'severity_level' in result:
            severity_translations = {
                'en': {'low': 'Low', 'medium': 'Medium', 'high': 'High', 'critical': 'Critical'},
                'hi': {'low': 'कम', 'medium': 'मध्यम', 'high': 'उच्च', 'critical': 'गंभीर'},
                'bn': {'low': 'কম', 'medium': 'মাঝারি', 'high': 'উচ্চ', 'critical': 'সংকটজনক'},
                'te': {'low': 'తక్కువ', 'medium': 'మధ్యస్థ', 'high': 'అధిక', 'critical': 'క్లిష్టమైన'},
                'ta': {'low': 'குறைவு', 'medium': 'நடுத்தர', 'high': 'அதிக', 'critical': 'முக்கியமான'}
            }
            
            severity = result['severity_level'].lower()
            if target_lang in severity_translations and severity in severity_translations[target_lang]:
                translated_result['severity_level'] = severity_translations[target_lang][severity]
        
        return translated_result
    
    def translate_chat_message(self, message: str, source_lang: str, target_lang: str = 'en') -> str:
        """Translate chat messages bidirectionally"""
        return self.translate(message, source_lang, target_lang)
    
    def detect_language(self, text: str) -> str:
        """
        Detect language of input text
        Returns language code
        """
        try:
            from langdetect import detect
            detected = detect(text)
            
            # Map to our supported languages
            if detected in SUPPORTED_LANGUAGES:
                return detected
            return 'en'  # Default to English
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return 'en'
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return SUPPORTED_LANGUAGES
    
    def translate_ui_elements(self, ui_dict: Dict[str, str], target_lang: str) -> Dict[str, str]:
        """
        Translate UI elements (buttons, labels, etc.)
        """
        translated_ui = {}
        for key, value in ui_dict.items():
            translated_ui[key] = self.translate(value, 'en', target_lang)
        return translated_ui


# UI translations for common elements
UI_TRANSLATIONS = {
    'en': {
        'welcome': 'Welcome to MedAI-Pro',
        'login': 'Login',
        'register': 'Register',
        'diagnose': 'Get Diagnosis',
        'chat': 'Chat with AI',
        'find_hospitals': 'Find Hospitals',
        'profile': 'Profile',
        'history': 'History',
        'logout': 'Logout',
        'submit': 'Submit',
        'cancel': 'Cancel',
        'save': 'Save',
        'upload_image': 'Upload Image',
        'enter_symptoms': 'Enter Symptoms',
        'view_results': 'View Results',
        'emergency': 'Emergency',
        'book_appointment': 'Book Appointment'
    },
    'hi': {
        'welcome': 'MedAI-Pro में आपका स्वागत है',
        'login': 'लॉगिन',
        'register': 'पंजीकरण',
        'diagnose': 'निदान प्राप्त करें',
        'chat': 'AI से चैट करें',
        'find_hospitals': 'अस्पताल खोजें',
        'profile': 'प्रोफ़ाइल',
        'history': 'इतिहास',
        'logout': 'लॉगआउट',
        'submit': 'जमा करें',
        'cancel': 'रद्द करें',
        'save': 'सहेजें',
        'upload_image': 'छवि अपलोड करें',
        'enter_symptoms': 'लक्षण दर्ज करें',
        'view_results': 'परिणाम देखें',
        'emergency': 'आपातकाल',
        'book_appointment': 'अपॉइंटमेंट बुक करें'
    }
}


# Singleton instance
_translator_instance = None

def get_translator() -> MedicalTranslator:
    """Get singleton translator instance"""
    global _translator_instance
    if _translator_instance is None:
        _translator_instance = MedicalTranslator()
    return _translator_instance


if __name__ == "__main__":
    # Test translator
    translator = get_translator()
    
    # Test basic translation
    text = "You have a fever and cough. Please consult a doctor."
    translated = translator.translate(text, 'en', 'hi')
    print(f"English: {text}")
    print(f"Hindi: {translated}")
    
    # Test medical terms
    symptoms = ['fever', 'cough', 'headache']
    translated_symptoms = translator.translate_symptoms(symptoms, 'hi')
    print(f"\nSymptoms in Hindi: {translated_symptoms}")
    
    logger.info("✅ Translator test completed")

