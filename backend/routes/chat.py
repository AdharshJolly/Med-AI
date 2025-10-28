"""
Chat Routes for MedAI-Pro
AI chatbot with NLP, sentiment analysis, translation, and voice support
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import json
import io

from ..database import get_db, ChatSession, ChatMessage
from ..utils.auth import require_clerk_auth
from ..chatbot.nlp_engine import MedicalNLPEngine
from ..chatbot.sentiment_analyzer import SentimentAnalyzer
from ..chatbot.voice_handler import VoiceHandler
from ..utils.translator import get_translator

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Initialize components
nlp_engine = MedicalNLPEngine()
sentiment_analyzer = SentimentAnalyzer()
voice_handler = VoiceHandler()
translator = get_translator()


class ChatMessageRequest(BaseModel):
    message: str
    user_id: str
    session_id: Optional[str] = None


class SentimentRequest(BaseModel):
    message: str


class TranslateRequest(BaseModel):
    message: str
    target_language: str


class TextToSpeechRequest(BaseModel):
    text: str
    language: str = "en"


@router.post("/message")
async def send_chat_message(
    request: ChatMessageRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(require_clerk_auth)
):
    """
    Send a message to the AI chatbot
    Returns AI response with intent recognition and entity extraction
    """
    try:
        # Get or create chat session
        if request.session_id:
            session = db.query(ChatSession).filter(
                ChatSession.session_id == request.session_id
            ).first()
        else:
            # Create new session
            session = ChatSession(
                user_id=user_id,
                session_id=f"session_{user_id}_{datetime.utcnow().timestamp()}",
                started_at=datetime.utcnow(),
                is_active=True
            )
            db.add(session)
            db.commit()
            db.refresh(session)
        
        # Process message with NLP
        nlp_result = nlp_engine.process_message(request.message)
        
        # Analyze sentiment
        sentiment = sentiment_analyzer.analyze(request.message)
        
        # Generate AI response
        ai_response = nlp_engine.generate_response(
            request.message,
            nlp_result['intent'],
            nlp_result['entities']
        )
        
        # Save message to database
        chat_message = ChatMessage(
            session_id=session.id,
            message=request.message,
            response=ai_response,
            intent=nlp_result['intent'],
            entities=json.dumps(nlp_result['entities']),
            sentiment=sentiment['label'],
            sentiment_score=sentiment['score'],
            created_at=datetime.utcnow()
        )
        
        db.add(chat_message)
        db.commit()
        
        return {
            "session_id": session.session_id,
            "response": ai_response,
            "intent": nlp_result['intent'],
            "entities": nlp_result['entities'],
            "sentiment": sentiment
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{user_id}")
async def get_chat_history(
    user_id: str,
    limit: int = 50,
    db: Session = Depends(get_db),
    auth_user_id: str = Depends(require_clerk_auth)
):
    """Get chat history for a user"""
    if user_id != auth_user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    try:
        # Get user's chat sessions
        sessions = db.query(ChatSession).filter(
            ChatSession.user_id == user_id
        ).order_by(ChatSession.started_at.desc()).limit(10).all()
        
        history = []
        for session in sessions:
            messages = db.query(ChatMessage).filter(
                ChatMessage.session_id == session.id
            ).order_by(ChatMessage.created_at.asc()).all()
            
            history.append({
                "session_id": session.session_id,
                "started_at": session.started_at.isoformat(),
                "messages": [
                    {
                        "message": msg.message,
                        "response": msg.response,
                        "sentiment": msg.sentiment,
                        "created_at": msg.created_at.isoformat()
                    }
                    for msg in messages
                ]
            })
        
        return {"history": history}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sentiment")
async def analyze_sentiment(
    request: SentimentRequest,
    user_id: str = Depends(require_clerk_auth)
):
    """Analyze sentiment of a message"""
    try:
        sentiment = sentiment_analyzer.analyze(request.message)
        
        return {
            "label": sentiment['label'],
            "score": sentiment['score'],
            "confidence": sentiment['confidence']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate")
async def translate_message(
    request: TranslateRequest,
    user_id: str = Depends(require_clerk_auth)
):
    """Translate message to target language"""
    try:
        translated = translator.translate(
            request.message,
            dest=request.target_language
        )
        
        return {
            "original": request.message,
            "translated": translated.text,
            "source_language": translated.src,
            "target_language": request.target_language
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/speech-to-text")
async def speech_to_text(
    audio: UploadFile = File(...),
    user_id: str = Depends(require_clerk_auth)
):
    """Convert speech audio to text"""
    try:
        # Read audio file
        audio_data = await audio.read()
        
        # Convert to text
        text = voice_handler.speech_to_text(audio_data)
        
        return {
            "text": text,
            "filename": audio.filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/text-to-speech")
async def text_to_speech(
    request: TextToSpeechRequest,
    user_id: str = Depends(require_clerk_auth)
):
    """Convert text to speech audio"""
    try:
        # Generate speech
        audio_data = voice_handler.text_to_speech(
            request.text,
            language=request.language
        )
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=speech.mp3"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

