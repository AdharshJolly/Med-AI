"""
MedAI-Pro Main FastAPI Application
Complete backend server with all API endpoints
"""

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, status, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from pydantic import BaseModel, EmailStr
from datetime import datetime
import uvicorn
import os
from pathlib import Path
from loguru import logger

# Import database (Clerk-based, no old JWT auth)
from database import get_db, init_db, UserProfile, Diagnosis, ChatSession, ChatMessage

# Import Clerk-based routes
from routes.profile import router as profile_router
from routes.diagnosis import router as diagnosis_router
from routes.insights import router as insights_router
from routes.chat import router as chat_router
from routes.maps import router as maps_router
from routes.contact import router as contact_router

# Import models
from models.cardiology_model import CardiologyModel
from models.dermatology_model import DermatologyModel
from models.respiratory_model import RespiratoryModel
from models.orthopedics_model import OrthopedicsModel
from models.gastro_model import GastroModel
from models.general_model import GeneralModel
from models.router_model import MedicalRouter

# Import utilities
from utils.preprocessor import MultiModalPreprocessor
from utils.translator import get_translator
from chatbot.nlp_engine import MedicalNLPEngine
from chatbot.sentiment_analyzer import SentimentAnalyzer
from chatbot.voice_handler import VoiceHandler
from maps.location_service import LocationService
from websocket_handler import websocket_endpoint, manager as ws_manager
from analytics import get_analytics_dashboard, get_model_analytics, track_diagnosis_event, track_chat_event
from model_versioning import version_manager

# Initialize FastAPI app
app = FastAPI(
    title="MedAI-Pro API",
    description="Production-ready multi-modal medical AI system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register new Clerk-based API routers
app.include_router(profile_router)
app.include_router(diagnosis_router)
app.include_router(insights_router)
app.include_router(chat_router)
app.include_router(maps_router)
app.include_router(contact_router)

# Initialize components
logger.info("🚀 Initializing MedAI-Pro components...")

# AI Models
cardiology_model = CardiologyModel()
dermatology_model = DermatologyModel()
respiratory_model = RespiratoryModel()
orthopedics_model = OrthopedicsModel()
gastro_model = GastroModel()
general_model = GeneralModel()
router = MedicalRouter()

# Utilities
preprocessor = MultiModalPreprocessor()
translator = get_translator()
nlp_engine = MedicalNLPEngine()
sentiment_analyzer = SentimentAnalyzer()
voice_handler = VoiceHandler()
location_service = LocationService()

# Create upload directories
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
(UPLOAD_DIR / "images").mkdir(exist_ok=True)
(UPLOAD_DIR / "ecg").mkdir(exist_ok=True)
(UPLOAD_DIR / "audio").mkdir(exist_ok=True)

logger.info("✅ All components initialized successfully")


# Pydantic models for requests
class DiagnosisRequest(BaseModel):
    symptoms: Optional[List[str]] = None
    description: Optional[str] = None
    specialty: Optional[str] = None
    language: str = "en"


class ChatMessageRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    language: str = "en"
    is_voice: bool = False


class LocationRequest(BaseModel):
    location: str
    facility_type: str = "hospital"
    radius: int = 5000


# ==================== AUTHENTICATION ====================
# Authentication is handled by Clerk via routes/profile.py
# All protected endpoints use require_clerk_auth dependency from utils/auth.py


# ==================== DIAGNOSIS ENDPOINTS ====================
# Diagnosis endpoints moved to routes/diagnosis.py with Clerk authentication
# Use POST /api/diagnosis/analyze for multi-modal diagnosis


# ==================== CHATBOT ENDPOINTS ====================
# Chat endpoints moved to routes/chat.py with Clerk authentication
# Use POST /api/chat/message for chatbot interactions


# ==================== LOCATION ENDPOINTS ====================
# Maps endpoints moved to routes/maps.py
# Use POST /api/maps/nearby for finding medical facilities


# ==================== UTILITY ENDPOINTS ====================

@app.get("/api/languages")
async def get_supported_languages():
    """Get supported languages"""
    return translator.get_supported_languages()


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "models_loaded": True
    }


# ==================== LEGACY ENDPOINTS (DEPRECATED) ====================
# These endpoints have been moved to Clerk-based routes:
# - Diagnosis history: GET /api/diagnosis/history/{user_id}
# - Chat history: GET /api/chat/history/{user_id}
# - All endpoints now use Clerk authentication via require_clerk_auth


# Old location and auth endpoints removed - now in routes/maps.py and routes/profile.py


# ==================== WEBSOCKET ENDPOINTS ====================

@app.websocket("/ws/chat/{user_id}/{session_id}")
async def chat_websocket(websocket: WebSocket, user_id: int, session_id: str):
    """
    WebSocket endpoint for real-time chat

    Args:
        websocket: WebSocket connection
        user_id: User ID
        session_id: Chat session ID
    """
    await websocket_endpoint(
        websocket,
        user_id,
        session_id,
        chatbot,
        voice_handler,
        translator
    )


@app.get("/ws/stats")
async def websocket_stats():
    """Get WebSocket connection statistics"""
    return {
        "active_users": ws_manager.get_active_users(),
        "total_connections": ws_manager.get_connection_count(),
        "connections_by_user": {
            user_id: ws_manager.get_connection_count(user_id)
            for user_id in ws_manager.get_active_users()
        }
    }


# ==================== ANALYTICS ENDPOINTS ====================
# Analytics endpoints can be added to routes/insights.py if needed
# Currently using public analytics without authentication


# ==================== STARTUP EVENT ====================

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    logger.info("✅ MedAI-Pro API is ready!")


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

