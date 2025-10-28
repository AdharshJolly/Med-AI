"""
User Profile Processor for MedAI-Pro
Extract features from user profile for ML models and generate personalized insights
"""

from typing import Dict, List
import json
import numpy as np


class UserProfileProcessor:
    """Process user profile data for ML models"""
    
    def __init__(self):
        self.age_risk_thresholds = {
            'low': (0, 40),
            'medium': (40, 60),
            'high': (60, 100)
        }
        
        self.bmi_categories = {
            'underweight': (0, 18.5),
            'normal': (18.5, 25),
            'overweight': (25, 30),
            'obese': (30, 100)
        }
    
    def extract_features(self, user_profile) -> Dict:
        """Extract features from user profile for ML model"""
        
        features = {
            'age': user_profile.age or 0,
            'gender': 1 if user_profile.gender == 'male' else 0,
            'bmi': user_profile.bmi or 0,
            'has_chronic_conditions': 0,
            'chronic_condition_count': 0,
            'medication_count': 0,
            'has_allergies': 0,
            'allergy_count': 0,
            'age_risk_category': self._get_age_risk_category(user_profile.age),
            'bmi_category': self._get_bmi_category(user_profile.bmi),
        }
        
        # Parse chronic conditions
        if user_profile.chronic_conditions:
            try:
                conditions = json.loads(user_profile.chronic_conditions)
                features['has_chronic_conditions'] = 1 if conditions else 0
                features['chronic_condition_count'] = len(conditions)
            except:
                pass
        
        # Parse medications
        if user_profile.present_medications:
            medications = user_profile.present_medications.split(',')
            features['medication_count'] = len([m for m in medications if m.strip()])
        
        # Parse allergies
        if user_profile.allergies:
            allergies = user_profile.allergies.split(',')
            features['has_allergies'] = 1 if allergies else 0
            features['allergy_count'] = len([a for a in allergies if a.strip()])
        
        return features
    
    def calculate_risk_factors(
        self,
        user_profile,
        diagnosis: str
    ) -> List[str]:
        """Calculate personalized risk factors"""
        
        risk_factors = []
        
        # Age-based risks
        if user_profile.age:
            if user_profile.age > 65:
                risk_factors.append("Advanced age (>65) - increased health risks")
            elif user_profile.age > 50:
                risk_factors.append("Age >50 - regular monitoring recommended")
        
        # BMI-based risks
        if user_profile.bmi:
            bmi_cat = self._get_bmi_category(user_profile.bmi)
            if bmi_cat == 'obese':
                risk_factors.append("Obesity - increased risk for multiple conditions")
            elif bmi_cat == 'overweight':
                risk_factors.append("Overweight - weight management recommended")
            elif bmi_cat == 'underweight':
                risk_factors.append("Underweight - nutritional assessment recommended")
        
        # Chronic conditions
        if user_profile.chronic_conditions:
            try:
                conditions = json.loads(user_profile.chronic_conditions)
                if conditions:
                    risk_factors.append(f"Existing chronic conditions: {', '.join(conditions)}")
            except:
                pass
        
        # Medications
        if user_profile.present_medications:
            meds = user_profile.present_medications.split(',')
            med_count = len([m for m in meds if m.strip()])
            if med_count >= 3:
                risk_factors.append(f"Multiple medications ({med_count}) - monitor for interactions")
        
        # Allergies
        if user_profile.allergies:
            allergies = user_profile.allergies.split(',')
            allergy_list = [a.strip() for a in allergies if a.strip()]
            if allergy_list:
                risk_factors.append(f"Known allergies: {', '.join(allergy_list)}")
        
        # Family history
        if user_profile.family_history:
            risk_factors.append("Family history of medical conditions - genetic predisposition")
        
        return risk_factors
    
    def check_medication_interactions(
        self,
        current_medications: str,
        suggested_medications: List[str]
    ) -> List[str]:
        """Check for potential medication interactions"""
        
        warnings = []
        
        if not current_medications:
            return warnings
        
        current_meds = [m.strip().lower() for m in current_medications.split(',') if m.strip()]
        suggested_meds = [m.lower() for m in suggested_medications]
        
        # Simple interaction checking (placeholder - would use drug interaction database in production)
        common_interactions = {
            'aspirin': ['warfarin', 'ibuprofen'],
            'warfarin': ['aspirin', 'vitamin k'],
            'metformin': ['alcohol'],
        }
        
        for current_med in current_meds:
            for suggested_med in suggested_meds:
                if current_med in common_interactions:
                    if suggested_med in common_interactions[current_med]:
                        warnings.append(
                            f"⚠️ Potential interaction: {current_med} and {suggested_med}"
                        )
        
        if not warnings:
            warnings.append("✓ No known interactions detected")
        
        return warnings
    
    def generate_personalized_advice(
        self,
        user_profile,
        prediction: Dict,
        risk_factors: List[str]
    ) -> str:
        """Generate personalized treatment advice"""
        
        advice_parts = []
        
        # Base recommendation
        advice_parts.append(
            f"Based on your profile and diagnosis of {prediction.get('primary_diagnosis', 'condition')}, "
            "here are personalized recommendations:"
        )
        
        # Age-specific advice
        if user_profile.age:
            if user_profile.age > 60:
                advice_parts.append(
                    "Given your age, regular monitoring and follow-up appointments are crucial."
                )
            elif user_profile.age < 18:
                advice_parts.append(
                    "Pediatric consultation recommended for age-appropriate treatment."
                )
        
        # BMI-specific advice
        if user_profile.bmi:
            bmi_cat = self._get_bmi_category(user_profile.bmi)
            if bmi_cat in ['overweight', 'obese']:
                advice_parts.append(
                    "Weight management through diet and exercise may improve outcomes."
                )
            elif bmi_cat == 'underweight':
                advice_parts.append(
                    "Nutritional support may be beneficial for recovery."
                )
        
        # Chronic condition considerations
        if user_profile.chronic_conditions:
            advice_parts.append(
                "Your existing chronic conditions require integrated care approach. "
                "Ensure all healthcare providers are aware of your complete medical history."
            )
        
        # Medication advice
        if user_profile.present_medications:
            advice_parts.append(
                "Continue your current medications as prescribed. "
                "Inform your doctor about any new medications before starting."
            )
        
        # General advice
        advice_parts.append(
            "Maintain healthy lifestyle with balanced diet, regular exercise, "
            "adequate sleep, and stress management."
        )
        
        return " ".join(advice_parts)
    
    def adjust_severity(
        self,
        base_severity: str,
        age: int,
        chronic_conditions: str,
        bmi: float
    ) -> str:
        """Adjust severity based on user profile"""
        
        severity_levels = ['low', 'medium', 'high', 'critical']
        current_index = severity_levels.index(base_severity) if base_severity in severity_levels else 1
        
        # Increase severity for high-risk factors
        if age and age > 70:
            current_index = min(current_index + 1, len(severity_levels) - 1)
        
        if chronic_conditions:
            try:
                conditions = json.loads(chronic_conditions)
                if len(conditions) >= 2:
                    current_index = min(current_index + 1, len(severity_levels) - 1)
            except:
                pass
        
        if bmi:
            if bmi >= 35 or bmi < 16:  # Severe obesity or severe underweight
                current_index = min(current_index + 1, len(severity_levels) - 1)
        
        return severity_levels[current_index]
    
    def _get_age_risk_category(self, age: int) -> int:
        """Get age risk category (0=low, 1=medium, 2=high)"""
        if not age:
            return 0
        
        for category, (min_age, max_age) in self.age_risk_thresholds.items():
            if min_age <= age < max_age:
                return ['low', 'medium', 'high'].index(category)
        
        return 0
    
    def _get_bmi_category(self, bmi: float) -> str:
        """Get BMI category"""
        if not bmi:
            return 'unknown'
        
        for category, (min_bmi, max_bmi) in self.bmi_categories.items():
            if min_bmi <= bmi < max_bmi:
                return category
        
        return 'unknown'
    
    def parse_medications(self, medication_string: str) -> List[str]:
        """Parse medication string into list"""
        if not medication_string:
            return []
        
        return [m.strip() for m in medication_string.split(',') if m.strip()]
    
    def parse_chronic_conditions(self, chronic_conditions: str) -> List[str]:
        """Parse chronic conditions JSON"""
        if not chronic_conditions:
            return []
        
        try:
            return json.loads(chronic_conditions)
        except:
            return []

