"""
Enhanced Diagnosis Routes for MedAI-Pro with Clerk Authentication
Integrates user profile data into AI diagnosis for personalized results
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from pydantic import BaseModel
from datetime import datetime
import json
import os
from pathlib import Path

from ..database import get_db, Diagnosis, UserProfile
from ..utils.auth import require_clerk_auth
from ..models.router_model import MedicalRouter
from ..models.cardiology_model import CardiologyModel
from ..models.dermatology_model import DermatologyModel
from ..models.respiratory_model import RespiratoryModel
from ..models.orthopedics_model import OrthopedicsModel
from ..models.gastro_model import GastroModel
from ..models.general_model import GeneralModel
from ..utils.preprocessor import MultiModalPreprocessor
from ..utils.user_profile_processor import UserProfileProcessor

router = APIRouter(prefix="/api/diagnosis", tags=["diagnosis"])

# Initialize models
medical_router = MedicalRouter()
cardiology_model = CardiologyModel()
dermatology_model = DermatologyModel()
respiratory_model = RespiratoryModel()
orthopedics_model = OrthopedicsModel()
gastro_model = GastroModel()
general_model = GeneralModel()
preprocessor = MultiModalPreprocessor()
profile_processor = UserProfileProcessor()

# Upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


class DiagnosisRequest(BaseModel):
    user_id: str
    symptoms: Optional[str] = None
    input_type: str = "text"
    files: Optional[List[str]] = []


class DiagnosisResponse(BaseModel):
    diagnosis_id: int
    primary_diagnosis: str
    confidence: float
    severity: str
    organ_system: str
    treatment_recommendations: str
    medications: List[str]
    risk_factors: List[str]
    personalized_advice: str


@router.post("/analyze", response_model=DiagnosisResponse)
async def analyze_diagnosis(
    request: DiagnosisRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(require_clerk_auth)
):
    """
    Enhanced diagnosis with user profile integration
    Incorporates medical history, chronic conditions, medications, age, BMI, etc.
    """
    try:
        # Get user profile
        user_profile = db.query(UserProfile).filter(
            UserProfile.clerk_user_id == user_id
        ).first()
        
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Extract profile features for ML model
        profile_features = profile_processor.extract_features(user_profile)
        
        # Route to appropriate specialist model
        routing_result = medical_router.route(request.symptoms)
        organ_system = routing_result['specialty']
        
        # Select appropriate model
        model_map = {
            'cardiology': cardiology_model,
            'dermatology': dermatology_model,
            'respiratory': respiratory_model,
            'orthopedics': orthopedics_model,
            'gastroenterology': gastro_model,
            'general': general_model
        }
        
        specialist_model = model_map.get(organ_system, general_model)
        
        # Preprocess input with profile context
        processed_input = preprocessor.process_text(request.symptoms)
        
        # Get prediction with profile-aware context
        prediction = specialist_model.predict_with_profile(
            processed_input,
            profile_features
        )
        
        # Calculate personalized risk factors
        risk_factors = profile_processor.calculate_risk_factors(
            user_profile,
            prediction['primary_diagnosis']
        )
        
        # Check medication interactions
        medication_warnings = profile_processor.check_medication_interactions(
            user_profile.present_medications,
            prediction.get('suggested_medications', [])
        )
        
        # Generate personalized treatment recommendations
        personalized_advice = profile_processor.generate_personalized_advice(
            user_profile,
            prediction,
            risk_factors
        )
        
        # Adjust severity based on user profile
        adjusted_severity = profile_processor.adjust_severity(
            prediction['severity'],
            user_profile.age,
            user_profile.chronic_conditions,
            user_profile.bmi
        )
        
        # Save diagnosis to database
        diagnosis = Diagnosis(
            user_id=user_id,
            diagnosis_type=organ_system,
            input_type=request.input_type,
            symptoms=json.dumps(request.symptoms),
            model_used=specialist_model.__class__.__name__,
            primary_prediction=prediction['primary_diagnosis'],
            confidence_score=prediction['confidence'],
            all_predictions=json.dumps(prediction.get('all_predictions', [])),
            severity_level=adjusted_severity,
            recommendations=json.dumps(prediction.get('recommendations', [])),
            suggested_specialists=json.dumps(prediction.get('specialists', [])),
            medication_suggestions=json.dumps(prediction.get('suggested_medications', [])),
            lifestyle_advice=personalized_advice,
            follow_up_required=adjusted_severity in ['high', 'critical'],
            follow_up_days=7 if adjusted_severity == 'high' else 3 if adjusted_severity == 'critical' else None,
            processing_time=0.5,
            created_at=datetime.utcnow()
        )
        
        db.add(diagnosis)
        db.commit()
        db.refresh(diagnosis)
        
        return DiagnosisResponse(
            diagnosis_id=diagnosis.id,
            primary_diagnosis=prediction['primary_diagnosis'],
            confidence=prediction['confidence'],
            severity=adjusted_severity,
            organ_system=organ_system,
            treatment_recommendations=personalized_advice,
            medications=prediction.get('suggested_medications', []),
            risk_factors=risk_factors,
            personalized_advice=personalized_advice
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{user_id}")
async def get_diagnosis_history(
    user_id: str,
    db: Session = Depends(get_db),
    auth_user_id: str = Depends(require_clerk_auth)
):
    """Get diagnosis history for a user"""
    if user_id != auth_user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    diagnoses = db.query(Diagnosis).filter(
        Diagnosis.user_id == user_id
    ).order_by(Diagnosis.created_at.desc()).all()
    
    return {
        "diagnoses": [
            {
                "id": d.id,
                "primary_diagnosis": d.primary_prediction,
                "confidence": d.confidence_score,
                "severity": d.severity_level,
                "organ_system": d.diagnosis_type,
                "created_at": d.created_at.isoformat()
            }
            for d in diagnoses
        ]
    }


@router.get("/{diagnosis_id}")
async def get_diagnosis_by_id(
    diagnosis_id: int,
    db: Session = Depends(get_db),
    user_id: str = Depends(require_clerk_auth)
):
    """Get specific diagnosis by ID"""
    diagnosis = db.query(Diagnosis).filter(Diagnosis.id == diagnosis_id).first()
    
    if not diagnosis:
        raise HTTPException(status_code=404, detail="Diagnosis not found")
    
    if diagnosis.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    return {
        "id": diagnosis.id,
        "primary_diagnosis": diagnosis.primary_prediction,
        "confidence": diagnosis.confidence_score,
        "severity": diagnosis.severity_level,
        "organ_system": diagnosis.diagnosis_type,
        "recommendations": json.loads(diagnosis.recommendations) if diagnosis.recommendations else [],
        "medications": json.loads(diagnosis.medication_suggestions) if diagnosis.medication_suggestions else [],
        "lifestyle_advice": diagnosis.lifestyle_advice,
        "created_at": diagnosis.created_at.isoformat()
    }


@router.post("/upload")
async def upload_diagnosis_file(
    file: UploadFile = File(...),
    user_id: str = Depends(require_clerk_auth)
):
    """Upload medical file for diagnosis"""
    try:
        # Save file
        file_path = UPLOAD_DIR / f"{user_id}_{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        return {"url": str(file_path), "filename": file.filename}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

