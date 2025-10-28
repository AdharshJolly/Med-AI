"""
User Profile Routes for MedAI-Pro with Clerk Authentication
Handles user profile creation, retrieval, and updates
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import json

from ..database import get_db, UserProfile
from ..utils.auth import require_clerk_auth

router = APIRouter(prefix="/api/profile", tags=["profile"])


class ProfileCreate(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    age: int
    gender: str
    blood_group: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    previous_medical_records: Optional[str] = ""
    present_medications: Optional[str] = ""
    allergies: Optional[str] = ""
    family_history: Optional[str] = ""
    chronic_conditions: Optional[List[str]] = []
    terms_accepted: bool
    disclaimer_accepted: bool
    preferred_language: Optional[str] = "en"


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    previous_medical_records: Optional[str] = None
    present_medications: Optional[str] = None
    allergies: Optional[str] = None
    family_history: Optional[str] = None
    chronic_conditions: Optional[List[str]] = None
    preferred_language: Optional[str] = None


@router.post("/create")
async def create_profile(
    profile_data: ProfileCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(require_clerk_auth)
):
    """Create user profile after onboarding"""
    try:
        # Check if profile already exists
        existing_profile = db.query(UserProfile).filter(
            UserProfile.clerk_user_id == user_id
        ).first()

        if existing_profile:
            raise HTTPException(status_code=400, detail="Profile already exists")

        # Validate checkboxes
        if not profile_data.terms_accepted or not profile_data.disclaimer_accepted:
            raise HTTPException(
                status_code=400,
                detail="Both terms and disclaimer must be accepted"
            )

        # Calculate BMI
        bmi = None
        if profile_data.height and profile_data.weight:
            height_m = profile_data.height / 100
            bmi = profile_data.weight / (height_m ** 2)

        # Create profile
        profile = UserProfile(
            clerk_user_id=user_id,
            email=profile_data.email,
            full_name=profile_data.full_name,
            phone=profile_data.phone,
            age=profile_data.age,
            gender=profile_data.gender,
            blood_group=profile_data.blood_group,
            height=profile_data.height,
            weight=profile_data.weight,
            bmi=bmi,
            previous_medical_records=profile_data.previous_medical_records,
            present_medications=profile_data.present_medications,
            allergies=profile_data.allergies,
            family_history=profile_data.family_history,
            chronic_conditions=json.dumps(profile_data.chronic_conditions),
            terms_accepted=profile_data.terms_accepted,
            disclaimer_accepted=profile_data.disclaimer_accepted,
            preferred_language=profile_data.preferred_language,
            profile_completed=True,
            created_at=datetime.utcnow()
        )

        db.add(profile)
        db.commit()
        db.refresh(profile)

        return {
            "message": "Profile created successfully",
            "profile_id": profile.id,
            "user_id": user_id
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}")
async def get_profile(
    user_id: str,
    db: Session = Depends(get_db),
    auth_user_id: str = Depends(require_clerk_auth)
):
    """Get user profile"""
    # Verify user can only access their own profile
    if user_id != auth_user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    profile = db.query(UserProfile).filter(
        UserProfile.clerk_user_id == user_id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return {
        "profile": {
            "id": profile.id,
            "clerk_user_id": profile.clerk_user_id,
            "email": profile.email,
            "full_name": profile.full_name,
            "phone": profile.phone,
            "age": profile.age,
            "gender": profile.gender,
            "blood_group": profile.blood_group,
            "height": profile.height,
            "weight": profile.weight,
            "bmi": profile.bmi,
            "previous_medical_records": profile.previous_medical_records,
            "present_medications": profile.present_medications,
            "allergies": profile.allergies,
            "family_history": profile.family_history,
            "chronic_conditions": json.loads(profile.chronic_conditions) if profile.chronic_conditions else [],
            "preferred_language": profile.preferred_language,
            "profile_completed": profile.profile_completed,
            "created_at": profile.created_at.isoformat() if profile.created_at else None
        }
    }


@router.put("/{user_id}")
async def update_profile(
    user_id: str,
    profile_data: ProfileUpdate,
    db: Session = Depends(get_db),
    auth_user_id: str = Depends(require_clerk_auth)
):
    """Update user profile"""
    # Verify user can only update their own profile
    if user_id != auth_user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    profile = db.query(UserProfile).filter(
        UserProfile.clerk_user_id == user_id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    try:
        # Update fields
        update_data = profile_data.dict(exclude_unset=True)

        for field, value in update_data.items():
            if field == 'chronic_conditions':
                setattr(profile, field, json.dumps(value))
            else:
                setattr(profile, field, value)

        # Recalculate BMI if height or weight changed
        if 'height' in update_data or 'weight' in update_data:
            if profile.height and profile.weight:
                height_m = profile.height / 100
                profile.bmi = profile.weight / (height_m ** 2)

        profile.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(profile)

        return {
            "message": "Profile updated successfully",
            "profile_id": profile.id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/medical-summary")
async def get_medical_summary(
    user_id: str,
    db: Session = Depends(get_db),
    auth_user_id: str = Depends(require_clerk_auth)
):
    """Get medical summary for ML model"""
    if user_id != auth_user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    profile = db.query(UserProfile).filter(
        UserProfile.clerk_user_id == user_id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return {
        "summary": {
            "age": profile.age,
            "gender": profile.gender,
            "bmi": profile.bmi,
            "chronic_conditions": json.loads(profile.chronic_conditions) if profile.chronic_conditions else [],
            "medications": profile.present_medications.split(',') if profile.present_medications else [],
            "allergies": profile.allergies.split(',') if profile.allergies else [],
            "family_history": profile.family_history
        }
    }
