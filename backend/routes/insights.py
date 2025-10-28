"""
AI Insights Routes for MedAI-Pro
Generate personalized health insights, risk assessments, and recommendations
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
from pydantic import BaseModel
from datetime import datetime, timedelta
import json

from ..database import get_db, Diagnosis, UserProfile
from ..utils.auth import require_clerk_auth
from ..utils.insights_generator import InsightsGenerator

router = APIRouter(prefix="/api/insights", tags=["insights"])
insights_generator = InsightsGenerator()


class DashboardInsightsRequest(BaseModel):
    user_id: str


class DiagnosisInsightsRequest(BaseModel):
    diagnosis_data: Dict
    user_profile: Dict


@router.post("/dashboard")
async def get_dashboard_insights(
    request: DashboardInsightsRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(require_clerk_auth)
):
    """
    Generate AI insights for dashboard
    Includes health trends, risk assessment, and recommendations
    """
    try:
        # Get user profile
        user_profile = db.query(UserProfile).filter(
            UserProfile.clerk_user_id == user_id
        ).first()
        
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Get recent diagnoses (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_diagnoses = db.query(Diagnosis).filter(
            Diagnosis.user_id == user_id,
            Diagnosis.created_at >= thirty_days_ago
        ).all()
        
        # Generate insights
        insights = insights_generator.generate_dashboard_insights(
            user_profile,
            recent_diagnoses
        )
        
        return {
            "summary": insights['summary'],
            "health_score": insights['health_score'],
            "risk_factors": insights['risk_factors'],
            "recommendations": insights['recommendations'],
            "trends": insights['trends'],
            "alerts": insights['alerts']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/diagnosis")
async def get_diagnosis_insights(
    request: DiagnosisInsightsRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(require_clerk_auth)
):
    """
    Generate AI insights for specific diagnosis
    Includes medical knowledge, prognosis, and treatment options
    """
    try:
        # Get user profile
        user_profile = db.query(UserProfile).filter(
            UserProfile.clerk_user_id == user_id
        ).first()
        
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Generate diagnosis-specific insights
        insights = insights_generator.generate_diagnosis_insights(
            request.diagnosis_data,
            user_profile
        )
        
        return {
            "condition_overview": insights['condition_overview'],
            "severity_assessment": insights['severity_assessment'],
            "prognosis": insights['prognosis'],
            "treatment_options": insights['treatment_options'],
            "lifestyle_modifications": insights['lifestyle_modifications'],
            "warning_signs": insights['warning_signs'],
            "when_to_seek_help": insights['when_to_seek_help'],
            "medical_citations": insights['medical_citations']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/history/{diagnosis_id}")
async def get_history_insights(
    diagnosis_id: int,
    db: Session = Depends(get_db),
    user_id: str = Depends(require_clerk_auth)
):
    """
    Generate insights comparing diagnosis with history
    Shows progression, treatment effectiveness, and new risk factors
    """
    try:
        # Get the specific diagnosis
        diagnosis = db.query(Diagnosis).filter(Diagnosis.id == diagnosis_id).first()
        
        if not diagnosis:
            raise HTTPException(status_code=404, detail="Diagnosis not found")
        
        if diagnosis.user_id != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Get user profile
        user_profile = db.query(UserProfile).filter(
            UserProfile.clerk_user_id == user_id
        ).first()
        
        # Get all previous diagnoses
        all_diagnoses = db.query(Diagnosis).filter(
            Diagnosis.user_id == user_id,
            Diagnosis.created_at < diagnosis.created_at
        ).order_by(Diagnosis.created_at.desc()).all()
        
        # Generate historical comparison insights
        insights = insights_generator.generate_history_insights(
            diagnosis,
            all_diagnoses,
            user_profile
        )
        
        return {
            "progression_analysis": insights['progression_analysis'],
            "condition_changes": insights['condition_changes'],
            "treatment_effectiveness": insights['treatment_effectiveness'],
            "new_risk_factors": insights['new_risk_factors'],
            "recommendations": insights['recommendations'],
            "follow_up_advice": insights['follow_up_advice']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends/{user_id}")
async def get_health_trends(
    user_id: str,
    db: Session = Depends(get_db),
    auth_user_id: str = Depends(require_clerk_auth)
):
    """Get health trends over time"""
    if user_id != auth_user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    try:
        # Get all diagnoses
        diagnoses = db.query(Diagnosis).filter(
            Diagnosis.user_id == user_id
        ).order_by(Diagnosis.created_at.asc()).all()
        
        # Calculate trends
        trends = insights_generator.calculate_health_trends(diagnoses)
        
        return {
            "severity_trend": trends['severity_trend'],
            "confidence_trend": trends['confidence_trend'],
            "organ_systems_affected": trends['organ_systems_affected'],
            "most_common_conditions": trends['most_common_conditions'],
            "timeline": trends['timeline']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

