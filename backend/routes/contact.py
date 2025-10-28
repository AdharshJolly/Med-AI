"""
Contact Routes for MedAI-Pro
Handle contact form submissions
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime

from ..database import get_db, ContactSubmission
from ..utils.auth import optional_clerk_auth

router = APIRouter(prefix="/api/contact", tags=["contact"])


class ContactFormRequest(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str


@router.post("/submit")
async def submit_contact_form(
    request: ContactFormRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(optional_clerk_auth)
):
    """
    Submit contact form
    Can be used by both authenticated and unauthenticated users
    """
    try:
        # Create contact submission
        submission = ContactSubmission(
            name=request.name,
            email=request.email,
            subject=request.subject,
            message=request.message,
            user_id=user_id,  # Will be None if not authenticated
            created_at=datetime.utcnow()
        )
        
        db.add(submission)
        db.commit()
        db.refresh(submission)
        
        return {
            "message": "Contact form submitted successfully",
            "submission_id": submission.id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

