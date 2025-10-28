#!/bin/bash

# MedAI-Pro Setup Script
# This script sets up the complete MedAI-Pro system

echo "🏥 MedAI-Pro Setup Script"
echo "=========================="
echo ""

# Check if Docker is installed
if command -v docker &> /dev/null; then
    echo "✅ Docker is installed"
    
    # Ask user if they want to use Docker
    read -p "Do you want to use Docker for setup? (y/n): " use_docker
    
    if [ "$use_docker" = "y" ]; then
        echo ""
        echo "🐳 Setting up with Docker..."
        echo ""
        
        # Check if .env files exist
        if [ ! -f "backend/.env" ]; then
            echo "Creating backend/.env from template..."
            cp backend/.env backend/.env.backup 2>/dev/null || true
        fi
        
        if [ ! -f "frontend/.env" ]; then
            echo "Creating frontend/.env from template..."
            cp frontend/.env frontend/.env.backup 2>/dev/null || true
        fi
        
        echo ""
        echo "⚠️  Please update the following files with your API keys:"
        echo "   - backend/.env (GOOGLE_MAPS_API_KEY, SECRET_KEY)"
        echo "   - frontend/.env (REACT_APP_GOOGLE_MAPS_API_KEY)"
        echo ""
        read -p "Press Enter when you're ready to continue..."
        
        echo ""
        echo "🚀 Starting Docker containers..."
        docker-compose up -d
        
        echo ""
        echo "✅ Setup complete!"
        echo ""
        echo "📍 Access the application:"
        echo "   - Frontend: http://localhost:3000"
        echo "   - Backend API: http://localhost:8000"
        echo "   - API Docs: http://localhost:8000/docs"
        echo ""
        echo "📊 To download datasets, run:"
        echo "   docker-compose exec backend python utils/dataset_downloader.py"
        echo ""
        echo "🎯 To train models, run:"
        echo "   docker-compose exec backend python models/cardiology_model.py"
        echo "   (and similarly for other models)"
        echo ""
        
        exit 0
    fi
fi

# Manual setup
echo "📦 Setting up manually..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10+"
    exit 1
fi

echo "✅ Python is installed"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+"
    exit 1
fi

echo "✅ Node.js is installed"

# Backend setup
echo ""
echo "🔧 Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Download spaCy model
echo "Downloading spaCy model..."
python -m spacy download en_core_web_sm

# Create directories
mkdir -p uploads/images uploads/ecg uploads/audio models/saved_models

cd ..

# Frontend setup
echo ""
echo "🎨 Setting up frontend..."
cd frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "📍 To start the application:"
echo ""
echo "Backend:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  uvicorn app:app --reload"
echo ""
echo "Frontend (in a new terminal):"
echo "  cd frontend"
echo "  npm start"
echo ""
echo "⚠️  Don't forget to:"
echo "  1. Set up PostgreSQL database"
echo "  2. Update .env files with your configuration"
echo "  3. Download datasets: python utils/dataset_downloader.py"
echo "  4. Train models before using the system"
echo ""

