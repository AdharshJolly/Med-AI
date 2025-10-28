@echo off
REM MedAI-Pro Setup Script for Windows

echo ========================================
echo    MedAI-Pro Setup Script (Windows)
echo ========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Docker is installed
    echo.
    set /p use_docker="Do you want to use Docker for setup? (y/n): "
    
    if /i "%use_docker%"=="y" (
        echo.
        echo [INFO] Setting up with Docker...
        echo.
        
        echo [INFO] Starting Docker containers...
        docker-compose up -d
        
        echo.
        echo [SUCCESS] Setup complete!
        echo.
        echo Access the application:
        echo   - Frontend: http://localhost:3000
        echo   - Backend API: http://localhost:8000
        echo   - API Docs: http://localhost:8000/docs
        echo.
        echo To download datasets, run:
        echo   docker-compose exec backend python utils/dataset_downloader.py
        echo.
        
        pause
        exit /b 0
    )
)

REM Manual setup
echo [INFO] Setting up manually...
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed. Please install Python 3.10+
    pause
    exit /b 1
)

echo [OK] Python is installed

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed. Please install Node.js 18+
    pause
    exit /b 1
)

echo [OK] Node.js is installed

REM Backend setup
echo.
echo [INFO] Setting up backend...
cd backend

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Download spaCy model
echo Downloading spaCy model...
python -m spacy download en_core_web_sm

REM Create directories
if not exist "uploads\images" mkdir uploads\images
if not exist "uploads\ecg" mkdir uploads\ecg
if not exist "uploads\audio" mkdir uploads\audio
if not exist "models\saved_models" mkdir models\saved_models

cd ..

REM Frontend setup
echo.
echo [INFO] Setting up frontend...
cd frontend

REM Install dependencies
echo Installing Node.js dependencies...
call npm install

cd ..

echo.
echo [SUCCESS] Setup complete!
echo.
echo To start the application:
echo.
echo Backend:
echo   cd backend
echo   venv\Scripts\activate.bat
echo   uvicorn app:app --reload
echo.
echo Frontend (in a new terminal):
echo   cd frontend
echo   npm start
echo.
echo Don't forget to:
echo   1. Set up PostgreSQL database
echo   2. Update .env files with your configuration
echo   3. Download datasets: python utils/dataset_downloader.py
echo   4. Train models before using the system
echo.

pause

