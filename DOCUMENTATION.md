# 📚 MedAI-Pro - Complete Documentation

**Version:** 1.0.0  
**Date:** 2025-10-28  
**Status:** Production Ready

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Installation & Setup](#installation--setup)
5. [Running the Application](#running-the-application)
6. [Testing](#testing)
7. [Deployment](#deployment)
8. [API Documentation](#api-documentation)
9. [Features](#features)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

**MedAI-Pro** is a comprehensive, production-ready medical AI application that provides:

- **Multi-modal Medical Diagnosis** - Text, image, audio, PDF, lab results, IoT sensor data
- **6 Organ-Specific AI Models** - Cardiology, Dermatology, Respiratory, Orthopedics, Gastroenterology, General Medicine
- **Intelligent Router Model** - BERT-based routing to appropriate specialist
- **AI Chatbot** - NLP-powered medical assistant with sentiment analysis
- **Google Maps Integration** - Find nearby hospitals, clinics, pharmacies
- **Multilingual Support** - 11 Indian languages + English
- **User Profile Management** - Medical history integration with ML models
- **AI Insights** - Health scores, risk assessment, personalized recommendations
- **Clerk Authentication** - Secure, modern authentication system
- **Dark Mode** - Full theme support
- **Responsive Design** - Mobile, tablet, desktop

---

## 🛠 Tech Stack

### **Frontend**
- **Framework:** React 18.2.0
- **Authentication:** Clerk (@clerk/clerk-react 4.30.0)
- **UI Library:** Material-UI (MUI) 5.14.x
- **Routing:** React Router DOM 6.20.0
- **HTTP Client:** Axios 1.6.2
- **State Management:** React Context API
- **Maps:** @react-google-maps/api 2.19.2
- **Charts:** Chart.js, Recharts
- **Forms:** Formik + Yup

### **Backend**
- **Framework:** FastAPI 0.104.1
- **Authentication:** Clerk Backend API (PyJWT 2.8.0)
- **Database:** PostgreSQL + SQLAlchemy
- **AI/ML:** PyTorch 2.1.1, TensorFlow 2.15.0, Transformers
- **Cloud Services:** Google Cloud (Maps, Speech-to-Text, Text-to-Speech)
- **Logging:** Loguru

### **AI Models**
- **Cardiology:** CNN for ECG arrhythmia classification (5 classes)
- **Dermatology:** CNN for skin lesion classification (7 classes)
- **Respiratory:** CNN for pneumonia detection (binary)
- **Orthopedics:** CNN for bone fracture detection (binary)
- **Gastroenterology:** Dense NN for GI conditions (6 classes)
- **General Medicine:** Ensemble for general conditions (5 classes)
- **Router:** BERT-based multi-modal routing (6 organs)

---

## 📁 Project Structure

```
medai-pro/
├── backend/                    # FastAPI backend
│   ├── app.py                 # Main application
│   ├── database.py            # Database models
│   ├── requirements.txt       # Python dependencies
│   ├── routes/                # API routes
│   │   ├── profile.py         # User profile CRUD
│   │   ├── diagnosis.py       # Diagnosis endpoints
│   │   ├── insights.py        # AI insights
│   │   ├── chat.py            # Chatbot
│   │   ├── maps.py            # Google Maps
│   │   └── contact.py         # Contact form
│   ├── utils/                 # Utilities
│   │   ├── auth.py            # Clerk authentication
│   │   ├── insights_generator.py
│   │   └── user_profile_processor.py
│   ├── models/                # AI models
│   │   ├── weights/           # Trained model weights
│   │   ├── cardiology_model.py
│   │   ├── dermatology_model.py
│   │   ├── respiratory_model.py
│   │   ├── orthopedics_model.py
│   │   ├── gastro_model.py
│   │   ├── general_model.py
│   │   └── router_model.py
│   ├── chatbot/               # NLP chatbot
│   │   ├── nlp_engine.py
│   │   ├── sentiment_analyzer.py
│   │   └── voice_handler.py
│   └── maps/                  # Maps integration
│       └── location_service.py
├── frontend/                   # React frontend
│   ├── package.json           # npm dependencies
│   ├── public/                # Static files
│   └── src/
│       ├── App.js             # Main app component
│       ├── index.js           # Entry point
│       ├── pages/             # Page components
│       │   ├── LandingPage.js
│       │   ├── HomePage.js
│       │   ├── Dashboard.js
│       │   ├── DiagnosisPage.js
│       │   ├── DiagnosisHistory.js
│       │   ├── MapsPage.js
│       │   ├── ProfilePage.js
│       │   ├── AboutPage.js
│       │   └── ContactPage.js
│       ├── components/        # Reusable components
│       │   ├── FloatingChatbot.js
│       │   ├── Footer.js
│       │   ├── Navbar.js
│       │   ├── ProtectedRoute.js
│       │   └── UserDetailsForm.js
│       ├── context/           # Context providers
│       │   ├── AuthContext.js
│       │   └── ThemeContext.js
│       ├── services/          # API services
│       │   └── api.js
│       └── styles/            # CSS files
│           ├── globals.css
│           └── components.css
├── data/                       # Datasets
│   ├── cardiology/
│   ├── dermatology/
│   ├── respiratory/
│   ├── orthopedics/
│   ├── gastro/
│   └── general/
├── reports/                    # Test reports
├── complete_test_suite.py     # Comprehensive testing
├── simple_download_datasets.py # Dataset downloader
├── simple_train_models.py     # Model trainer
└── DOCUMENTATION.md           # This file
```

---

## 🚀 Installation & Setup

### **Prerequisites**

- **Node.js** 16+ and npm
- **Python** 3.8+
- **PostgreSQL** 12+
- **Git**

### **1. Clone Repository**

```bash
git clone <repository-url>
cd medai-pro
```

### **2. Backend Setup**

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### **3. Frontend Setup**

```bash
cd frontend

# Install dependencies
npm install
```

### **4. Environment Variables**

**Backend `.env`** (create in `backend/` directory):

```env
# Database
DATABASE_URL=postgresql://medai:medai123@localhost:5432/medai_db

# Clerk Authentication
CLERK_SECRET_KEY=your_clerk_secret_key_here

# Google Cloud
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
GOOGLE_CLOUD_PROJECT_ID=your_project_id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# Optional
ENVIRONMENT=development
LOG_LEVEL=INFO
```

**Frontend `.env`** (create in `frontend/` directory):

```env
# Clerk Authentication
REACT_APP_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key

# API
REACT_APP_API_URL=http://localhost:8000

# Google Maps
REACT_APP_GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

### **5. Database Setup**

```bash
# Create PostgreSQL database
createdb medai_db

# Or using psql:
psql -U postgres
CREATE DATABASE medai_db;
CREATE USER medai WITH PASSWORD 'medai123';
GRANT ALL PRIVILEGES ON DATABASE medai_db TO medai;
\q

# Initialize database tables
cd backend
python -c "from database import init_db; init_db()"
```

### **6. Download Datasets**

```bash
# From project root
python simple_download_datasets.py
```

This will download:
- PTB-XL ECG dataset (Cardiology)
- HAM10000 skin lesion dataset (Dermatology)
- Chest X-ray dataset (Respiratory)
- MURA bone X-ray dataset (Orthopedics)
- Synthetic GI data (Gastroenterology)
- Synthetic general medicine data

### **7. Train AI Models**

```bash
# From project root
python simple_train_models.py
```

This will train all 7 models:
- Cardiology (ECG arrhythmia)
- Dermatology (skin lesions)
- Respiratory (pneumonia)
- Orthopedics (fractures)
- Gastroenterology (GI conditions)
- General Medicine (general conditions)
- Router (organ routing)

Models will be saved to `backend/models/weights/`

---

## 🏃 Running the Application

### **Start Backend Server**

```bash
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

### **Start Frontend Server**

```bash
cd frontend
npm start
```

Frontend will be available at: `http://localhost:3000`

### **Access Application**

1. Open browser to `http://localhost:3000`
2. Click "Get Started" to sign up with Clerk
3. Complete 3-step onboarding form
4. Check both mandatory disclaimer checkboxes
5. Start using the application!

---

## 🧪 Testing

### **Run Comprehensive Test Suite**

```bash
# From project root
python complete_test_suite.py
```

This will:
- Test all 7 AI models (accuracy, precision, recall, F1, AUC)
- Automatically fine-tune models below 85% accuracy
- Test all API endpoints
- Test integration workflows
- Generate HTML report in `reports/test_report.html`
- Generate confusion matrices and accuracy charts
- Save JSON results to `reports/test_results.json`

### **Test Options**

```bash
# Skip automatic fine-tuning
python complete_test_suite.py --skip-finetuning

# Test models only (skip API/integration)
python complete_test_suite.py --models-only

# Verbose logging
python complete_test_suite.py --verbose
```

### **View Test Reports**

```bash
# Open HTML report in browser
# Windows:
start reports/test_report.html
# macOS:
open reports/test_report.html
# Linux:
xdg-open reports/test_report.html
```

---

## 🚀 Deployment

### **Frontend Deployment (Vercel)**

**Yes, you can deploy frontend and backend separately!**

The frontend is a standard React app that can be deployed to Vercel:

```bash
cd frontend

# Install Vercel CLI
npm install -g vercel

# Deploy
vercel
```

**Important:** Update `REACT_APP_API_URL` in frontend `.env` to point to your deployed backend URL.

### **Backend Deployment Options**

1. **Heroku** - Easy deployment for FastAPI
2. **AWS EC2** - Full control
3. **Google Cloud Run** - Serverless containers
4. **DigitalOcean App Platform** - Simple deployment
5. **Railway** - Modern deployment platform

### **Vercel Configuration**

Create `vercel.json` in frontend directory:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "build",
  "devCommand": "npm start",
  "installCommand": "npm install"
}
```

---

## 📡 API Documentation

### **Authentication**

All protected endpoints require Clerk authentication token in header:

```
Authorization: Bearer <clerk_token>
```

### **Endpoints**

**Profile:**
- `POST /api/profile/create` - Create user profile
- `GET /api/profile/{user_id}` - Get user profile
- `PUT /api/profile/{user_id}` - Update user profile
- `GET /api/profile/{user_id}/medical-summary` - Get medical summary

**Diagnosis:**
- `POST /api/diagnosis/analyze` - Submit diagnosis (multi-modal)
- `GET /api/diagnosis/history/{user_id}` - Get diagnosis history
- `GET /api/diagnosis/{diagnosis_id}` - Get specific diagnosis
- `POST /api/diagnosis/upload` - Upload medical files

**Insights:**
- `POST /api/insights/dashboard` - Get dashboard insights
- `POST /api/insights/diagnosis` - Get diagnosis insights
- `POST /api/insights/history/{diagnosis_id}` - Get historical insights
- `GET /api/insights/trends/{user_id}` - Get health trends

**Chat:**
- `POST /api/chat/message` - Send chat message
- `GET /api/chat/history/{user_id}` - Get chat history
- `POST /api/chat/sentiment` - Analyze sentiment
- `POST /api/chat/translate` - Translate text
- `POST /api/chat/speech-to-text` - Convert speech to text
- `POST /api/chat/text-to-speech` - Convert text to speech

**Maps:**
- `POST /api/maps/nearby` - Find nearby facilities
- `POST /api/maps/search` - Search facilities
- `GET /api/maps/facility/{place_id}` - Get facility details

**Contact:**
- `POST /api/contact/submit` - Submit contact form

Full API documentation available at: `http://localhost:8000/docs`

---

## ✨ Features

### **1. Multi-modal Diagnosis**
- Text input (symptom description)
- Image upload (X-rays, skin photos)
- Audio recording (voice symptoms)
- PDF upload (medical reports)
- Lab results (CSV/JSON)
- IoT sensor data (ECG, vitals)

### **2. AI Models**
- 6 organ-specific specialist models
- BERT-based intelligent routing
- User profile integration
- Risk assessment
- Confidence scores

### **3. User Experience**
- 3-step onboarding
- 2 mandatory medical disclaimers
- Floating chatbot (60x60px button, 350x500px panel)
- Dark mode support
- Responsive design
- Medical disclaimer on all pages

### **4. Integrations**
- Clerk authentication
- Google Maps (nearby facilities)
- Google Cloud Speech-to-Text
- Google Cloud Text-to-Speech
- Multilingual translation (11 languages)

---

## 🐛 Troubleshooting

### **Backend won't start**
- Check PostgreSQL is running
- Verify DATABASE_URL in .env
- Check all dependencies installed: `pip install -r requirements.txt`

### **Frontend won't start**
- Check Node.js version: `node --version` (should be 16+)
- Clear node_modules: `rm -rf node_modules && npm install`
- Check package.json for errors

### **Models not found**
- Run dataset download: `python simple_download_datasets.py`
- Run model training: `python simple_train_models.py`
- Check `backend/models/weights/` directory exists

### **Clerk authentication errors**
- Verify CLERK_SECRET_KEY in backend .env
- Verify REACT_APP_CLERK_PUBLISHABLE_KEY in frontend .env
- Check Clerk dashboard for correct keys

### **Google Maps not working**
- Verify GOOGLE_MAPS_API_KEY in both .env files
- Enable required APIs in Google Cloud Console:
  - Maps JavaScript API
  - Places API
  - Geocoding API

---

## 📞 Support

For issues, questions, or contributions:
- Check this documentation first
- Review test reports in `reports/`
- Check API documentation at `/docs`
- Review console logs for errors

---

## 📄 License

Proprietary - MedAI-Pro Team

---

**Last Updated:** 2025-10-28  
**Version:** 1.0.0  
**Status:** ✅ Production Ready

