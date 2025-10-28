"""
Database models and configuration for MedAI-Pro
SQLAlchemy ORM models for users, diagnoses, chat history, and medical records
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://medai:medai123@localhost:5432/medai_db")

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Old JWT-based User model removed - now using Clerk authentication with UserProfile

class UserProfile(Base):
    """User profile model with Clerk authentication"""
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    clerk_user_id = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(200))
    phone = Column(String(20))

    # Personal Information
    age = Column(Integer)
    gender = Column(String(20))
    blood_group = Column(String(10))
    height = Column(Float)  # in cm
    weight = Column(Float)  # in kg
    bmi = Column(Float)

    # Address
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100), default="India")
    pincode = Column(String(10))

    # Medical Information
    previous_medical_records = Column(Text)
    present_medications = Column(Text)
    allergies = Column(Text)
    family_history = Column(Text)
    chronic_conditions = Column(JSON)  # List of chronic conditions

    # Terms and Disclaimers
    terms_accepted = Column(Boolean, default=False)
    disclaimer_accepted = Column(Boolean, default=False)

    # Preferences
    preferred_language = Column(String(20), default="en")

    # Metadata
    is_active = Column(Boolean, default=True)
    profile_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)


class Diagnosis(Base):
    """Medical diagnosis records with AI predictions and recommendations"""
    __tablename__ = "diagnoses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), index=True, nullable=False)  # Clerk user ID
    diagnosis_type = Column(String(50), nullable=False)  # cardiology, dermatology, etc.
    input_type = Column(String(50))  # image, ecg, text, multi-modal
    symptoms = Column(JSON)  # List of symptoms
    image_path = Column(String(500))
    ecg_data_path = Column(String(500))
    text_input = Column(Text)

    # AI Model Results
    model_used = Column(String(100))
    primary_prediction = Column(String(200))
    confidence_score = Column(Float)
    all_predictions = Column(JSON)  # All predictions with probabilities
    severity_level = Column(String(20))  # low, medium, high, critical

    # Recommendations
    recommendations = Column(JSON)
    suggested_specialists = Column(JSON)
    medication_suggestions = Column(JSON)
    lifestyle_advice = Column(Text)
    follow_up_required = Column(Boolean, default=False)
    follow_up_days = Column(Integer)

    # Metadata
    processing_time = Column(Float)  # seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # No relationships - user_id is Clerk user ID (string)


class ChatSession(Base):
    """AI chatbot conversation sessions with sentiment tracking"""
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), index=True, nullable=False)  # Clerk user ID
    session_id = Column(String(100), unique=True, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    language = Column(String(20), default="en")

    # Relationships
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """Individual chat messages with sentiment analysis"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    message = Column(Text, nullable=False)  # User message
    response = Column(Text)  # Bot response
    intent = Column(String(100))  # Medical intent
    entities = Column(JSON)  # Extracted entities

    # Voice data
    is_voice = Column(Boolean, default=False)
    audio_path = Column(String(500))

    # Sentiment Analysis
    sentiment = Column(String(20))  # positive, negative, neutral, anxious, concerned
    sentiment_score = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")


# MedicalRecord model removed - medical records now stored in UserProfile model

class MedicalFacility(Base):
    """Nearby hospitals and medical facilities from Google Maps"""
    __tablename__ = "medical_facilities"
    
    id = Column(Integer, primary_key=True, index=True)
    google_place_id = Column(String(200), unique=True)
    name = Column(String(300), nullable=False)
    facility_type = Column(String(100))  # hospital, clinic, pharmacy, diagnostic_center
    specialties = Column(JSON)  # List of specialties available
    
    # Location
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    pincode = Column(String(10))
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Contact
    phone = Column(String(50))
    website = Column(String(500))
    email = Column(String(200))
    
    # Ratings & Reviews
    google_rating = Column(Float)
    total_reviews = Column(Integer)
    
    # Operational Info
    is_24x7 = Column(Boolean, default=False)
    has_emergency = Column(Boolean, default=False)
    has_icu = Column(Boolean, default=False)
    has_ambulance = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ModelMetrics(Base):
    """Track AI model performance metrics"""
    __tablename__ = "model_metrics"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50))
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    auc_roc = Column(Float)

    # Detailed metrics
    confusion_matrix = Column(JSON)
    class_metrics = Column(JSON)  # Per-class metrics

    # Dataset info
    dataset_name = Column(String(100))
    dataset_size = Column(Integer)
    validation_size = Column(Integer)

    # Training info
    training_date = Column(DateTime)
    training_duration = Column(Float)  # hours
    epochs = Column(Integer)
    batch_size = Column(Integer)
    learning_rate = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)


class ContactSubmission(Base):
    """Contact form submissions"""
    __tablename__ = "contact_submissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    email = Column(String(255), nullable=False)
    subject = Column(String(300), nullable=False)
    message = Column(Text, nullable=False)
    user_id = Column(String(255))  # Clerk user ID (optional - can be null for non-authenticated users)
    created_at = Column(DateTime, default=datetime.utcnow)


# Database initialization
def init_db():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    init_db()

