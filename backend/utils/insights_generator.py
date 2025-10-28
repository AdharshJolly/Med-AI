"""
AI Insights Generator for MedAI-Pro
Generate personalized health insights, risk assessments, and recommendations
"""

from typing import Dict, List
from datetime import datetime, timedelta
import json


class InsightsGenerator:
    """Generate AI-powered health insights"""
    
    def __init__(self):
        self.severity_weights = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }
    
    def generate_dashboard_insights(
        self,
        user_profile,
        recent_diagnoses: List
    ) -> Dict:
        """Generate insights for dashboard"""
        
        # Calculate health score
        health_score = self._calculate_health_score(user_profile, recent_diagnoses)
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(user_profile, recent_diagnoses)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(user_profile, recent_diagnoses)
        
        # Analyze trends
        trends = self._analyze_trends(recent_diagnoses)
        
        # Generate alerts
        alerts = self._generate_alerts(user_profile, recent_diagnoses)
        
        # Create summary
        summary = self._create_summary(health_score, risk_factors, trends)
        
        return {
            'summary': summary,
            'health_score': health_score,
            'risk_factors': risk_factors,
            'recommendations': recommendations,
            'trends': trends,
            'alerts': alerts
        }
    
    def generate_diagnosis_insights(
        self,
        diagnosis_data: Dict,
        user_profile
    ) -> Dict:
        """Generate insights for specific diagnosis"""
        
        condition = diagnosis_data.get('primary_diagnosis', 'Unknown')
        severity = diagnosis_data.get('severity', 'medium')
        
        return {
            'condition_overview': self._get_condition_overview(condition),
            'severity_assessment': self._assess_severity(severity, user_profile),
            'prognosis': self._generate_prognosis(condition, severity, user_profile),
            'treatment_options': self._get_treatment_options(condition),
            'lifestyle_modifications': self._get_lifestyle_modifications(condition),
            'warning_signs': self._get_warning_signs(condition),
            'when_to_seek_help': self._get_when_to_seek_help(severity),
            'medical_citations': self._get_medical_citations(condition)
        }
    
    def generate_history_insights(
        self,
        current_diagnosis,
        previous_diagnoses: List,
        user_profile
    ) -> Dict:
        """Generate insights comparing with history"""
        
        progression = self._analyze_progression(current_diagnosis, previous_diagnoses)
        changes = self._identify_condition_changes(current_diagnosis, previous_diagnoses)
        effectiveness = self._assess_treatment_effectiveness(previous_diagnoses)
        new_risks = self._identify_new_risk_factors(current_diagnosis, previous_diagnoses)
        
        return {
            'progression_analysis': progression,
            'condition_changes': changes,
            'treatment_effectiveness': effectiveness,
            'new_risk_factors': new_risks,
            'recommendations': self._generate_follow_up_recommendations(progression),
            'follow_up_advice': self._generate_follow_up_advice(current_diagnosis)
        }
    
    def calculate_health_trends(self, diagnoses: List) -> Dict:
        """Calculate health trends over time"""
        
        if not diagnoses:
            return {
                'severity_trend': 'stable',
                'confidence_trend': 'stable',
                'organ_systems_affected': [],
                'most_common_conditions': [],
                'timeline': []
            }
        
        # Analyze severity trend
        severities = [d.severity_level for d in diagnoses]
        severity_trend = self._calculate_trend(severities, self.severity_weights)
        
        # Analyze confidence trend
        confidences = [d.confidence_score for d in diagnoses]
        confidence_trend = 'improving' if confidences[-1] > confidences[0] else 'stable'
        
        # Count organ systems
        organ_systems = {}
        for d in diagnoses:
            organ_systems[d.diagnosis_type] = organ_systems.get(d.diagnosis_type, 0) + 1
        
        # Count conditions
        conditions = {}
        for d in diagnoses:
            conditions[d.primary_prediction] = conditions.get(d.primary_prediction, 0) + 1
        
        return {
            'severity_trend': severity_trend,
            'confidence_trend': confidence_trend,
            'organ_systems_affected': list(organ_systems.keys()),
            'most_common_conditions': sorted(conditions.items(), key=lambda x: x[1], reverse=True)[:5],
            'timeline': [
                {
                    'date': d.created_at.isoformat(),
                    'condition': d.primary_prediction,
                    'severity': d.severity_level
                }
                for d in diagnoses
            ]
        }
    
    def _calculate_health_score(self, user_profile, recent_diagnoses) -> int:
        """Calculate overall health score (0-100)"""
        score = 100
        
        # Deduct for age
        if user_profile.age:
            if user_profile.age > 60:
                score -= 10
            elif user_profile.age > 50:
                score -= 5
        
        # Deduct for BMI
        if user_profile.bmi:
            if user_profile.bmi < 18.5 or user_profile.bmi > 30:
                score -= 10
            elif user_profile.bmi > 25:
                score -= 5
        
        # Deduct for chronic conditions
        if user_profile.chronic_conditions:
            try:
                conditions = json.loads(user_profile.chronic_conditions)
                score -= len(conditions) * 5
            except:
                pass
        
        # Deduct for recent diagnoses
        if recent_diagnoses:
            for d in recent_diagnoses:
                score -= self.severity_weights.get(d.severity_level, 1) * 3
        
        return max(0, min(100, score))
    
    def _identify_risk_factors(self, user_profile, recent_diagnoses) -> List[str]:
        """Identify health risk factors"""
        risks = []
        
        if user_profile.age and user_profile.age > 60:
            risks.append("Advanced age (>60)")
        
        if user_profile.bmi:
            if user_profile.bmi >= 30:
                risks.append("Obesity (BMI ≥ 30)")
            elif user_profile.bmi < 18.5:
                risks.append("Underweight (BMI < 18.5)")
        
        if user_profile.chronic_conditions:
            try:
                conditions = json.loads(user_profile.chronic_conditions)
                if conditions:
                    risks.append(f"{len(conditions)} chronic condition(s)")
            except:
                pass
        
        if recent_diagnoses:
            high_severity = [d for d in recent_diagnoses if d.severity_level in ['high', 'critical']]
            if high_severity:
                risks.append(f"{len(high_severity)} high-severity diagnosis in last 30 days")
        
        return risks
    
    def _generate_recommendations(self, user_profile, recent_diagnoses) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        if user_profile.bmi and user_profile.bmi >= 25:
            recommendations.append("Consider weight management through diet and exercise")
        
        if user_profile.age and user_profile.age > 50:
            recommendations.append("Schedule regular health checkups (every 6 months)")
        
        if not recent_diagnoses:
            recommendations.append("Maintain healthy lifestyle with regular exercise")
        
        recommendations.append("Stay hydrated and maintain balanced diet")
        recommendations.append("Get adequate sleep (7-8 hours daily)")
        
        return recommendations
    
    def _analyze_trends(self, recent_diagnoses) -> str:
        """Analyze health trends"""
        if not recent_diagnoses:
            return "No recent diagnoses to analyze"
        
        if len(recent_diagnoses) == 1:
            return "Insufficient data for trend analysis"
        
        severities = [self.severity_weights.get(d.severity_level, 1) for d in recent_diagnoses]
        
        if severities[-1] > severities[0]:
            return "Worsening - severity increasing"
        elif severities[-1] < severities[0]:
            return "Improving - severity decreasing"
        else:
            return "Stable - no significant changes"
    
    def _generate_alerts(self, user_profile, recent_diagnoses) -> List[str]:
        """Generate health alerts"""
        alerts = []
        
        critical_diagnoses = [d for d in recent_diagnoses if d.severity_level == 'critical']
        if critical_diagnoses:
            alerts.append("⚠️ Critical condition detected - seek immediate medical attention")
        
        if user_profile.age and user_profile.age > 65 and not recent_diagnoses:
            alerts.append("ℹ️ Recommended: Schedule annual health checkup")
        
        return alerts
    
    def _create_summary(self, health_score, risk_factors, trends) -> str:
        """Create summary text"""
        if health_score >= 80:
            status = "excellent"
        elif health_score >= 60:
            status = "good"
        elif health_score >= 40:
            status = "fair"
        else:
            status = "needs attention"
        
        return f"Your health status is {status} with a score of {health_score}/100. {trends}."
    
    def _get_condition_overview(self, condition: str) -> str:
        """Get overview of medical condition"""
        return f"{condition} is a medical condition that requires proper diagnosis and treatment. Consult with a healthcare professional for accurate assessment."
    
    def _assess_severity(self, severity: str, user_profile) -> str:
        """Assess severity with user context"""
        assessments = {
            'low': "Mild condition - monitor symptoms",
            'medium': "Moderate condition - medical consultation recommended",
            'high': "Serious condition - seek medical attention soon",
            'critical': "Critical condition - seek immediate medical attention"
        }
        return assessments.get(severity, "Unknown severity")
    
    def _generate_prognosis(self, condition: str, severity: str, user_profile) -> str:
        """Generate prognosis"""
        if severity in ['low', 'medium']:
            return "With proper treatment and lifestyle modifications, prognosis is generally favorable."
        else:
            return "Requires immediate medical attention. Prognosis depends on timely treatment."
    
    def _get_treatment_options(self, condition: str) -> List[str]:
        """Get treatment options"""
        return [
            "Consult with a qualified healthcare provider",
            "Follow prescribed medication regimen",
            "Lifestyle modifications as recommended",
            "Regular follow-up appointments"
        ]
    
    def _get_lifestyle_modifications(self, condition: str) -> List[str]:
        """Get lifestyle modification recommendations"""
        return [
            "Maintain healthy diet",
            "Regular physical activity",
            "Adequate sleep and rest",
            "Stress management",
            "Avoid smoking and excessive alcohol"
        ]
    
    def _get_warning_signs(self, condition: str) -> List[str]:
        """Get warning signs to watch for"""
        return [
            "Worsening of symptoms",
            "New or unusual symptoms",
            "Severe pain or discomfort",
            "Difficulty breathing",
            "High fever"
        ]
    
    def _get_when_to_seek_help(self, severity: str) -> str:
        """When to seek medical help"""
        if severity == 'critical':
            return "Seek immediate emergency medical attention"
        elif severity == 'high':
            return "Consult a doctor within 24-48 hours"
        else:
            return "Schedule an appointment with your healthcare provider"
    
    def _get_medical_citations(self, condition: str) -> List[str]:
        """Get medical citations (placeholder)"""
        return [
            "Consult medical literature for detailed information",
            "Refer to trusted medical sources like Mayo Clinic, WebMD",
            "Discuss with your healthcare provider for personalized advice"
        ]
    
    def _analyze_progression(self, current, previous) -> str:
        """Analyze disease progression"""
        if not previous:
            return "First diagnosis - no historical data for comparison"
        return "Condition progression analysis based on historical data"
    
    def _identify_condition_changes(self, current, previous) -> List[str]:
        """Identify changes in condition"""
        return ["Monitor for any changes in symptoms or severity"]
    
    def _assess_treatment_effectiveness(self, previous) -> str:
        """Assess treatment effectiveness"""
        return "Continue following prescribed treatment plan"
    
    def _identify_new_risk_factors(self, current, previous) -> List[str]:
        """Identify new risk factors"""
        return []
    
    def _generate_follow_up_recommendations(self, progression) -> List[str]:
        """Generate follow-up recommendations"""
        return ["Schedule follow-up appointment", "Monitor symptoms closely"]
    
    def _generate_follow_up_advice(self, diagnosis) -> str:
        """Generate follow-up advice"""
        if diagnosis.follow_up_required:
            return f"Follow-up recommended in {diagnosis.follow_up_days} days"
        return "Continue monitoring and maintain healthy lifestyle"
    
    def _calculate_trend(self, values, weights) -> str:
        """Calculate trend from values"""
        if len(values) < 2:
            return 'stable'
        
        weighted_values = [weights.get(v, 1) for v in values]
        
        if weighted_values[-1] > weighted_values[0]:
            return 'worsening'
        elif weighted_values[-1] < weighted_values[0]:
            return 'improving'
        else:
            return 'stable'

