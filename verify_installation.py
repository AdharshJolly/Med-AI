#!/usr/bin/env python3
"""
MedAI-Pro Installation Verification Script
Checks that all components are properly installed and configured
"""

import os
import sys
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text.center(60)}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓{RESET} {text}")

def print_error(text):
    print(f"{RED}✗{RESET} {text}")

def print_warning(text):
    print(f"{YELLOW}⚠{RESET} {text}")

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print_success(f"{description}: {filepath}")
        return True
    else:
        print_error(f"{description} NOT FOUND: {filepath}")
        return False

def check_directory_exists(dirpath, description):
    """Check if a directory exists"""
    if os.path.isdir(dirpath):
        print_success(f"{description}: {dirpath}")
        return True
    else:
        print_error(f"{description} NOT FOUND: {dirpath}")
        return False

def count_lines(filepath):
    """Count lines in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return len(f.readlines())
    except:
        return 0

def main():
    print_header("MedAI-Pro Installation Verification")
    
    # Get project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    total_checks = 0
    passed_checks = 0
    
    # 1. Check Backend Structure
    print_header("1. Backend Structure")
    
    backend_files = [
        ("backend/__init__.py", "Backend package init"),
        ("backend/app.py", "Main FastAPI application"),
        ("backend/auth.py", "Authentication module"),
        ("backend/database.py", "Database models"),
        ("backend/requirements.txt", "Python dependencies"),
        ("backend/.env", "Environment variables"),
    ]
    
    for filepath, desc in backend_files:
        total_checks += 1
        if check_file_exists(filepath, desc):
            passed_checks += 1
            lines = count_lines(filepath)
            if lines > 0:
                print(f"  └─ {lines} lines")
    
    # 2. Check AI Models
    print_header("2. AI Models")
    
    model_files = [
        ("backend/models/__init__.py", "Models package init"),
        ("backend/models/cardiology_model.py", "Cardiology Model (ECG)"),
        ("backend/models/dermatology_model.py", "Dermatology Model (Skin)"),
        ("backend/models/respiratory_model.py", "Respiratory Model (Chest X-Ray)"),
        ("backend/models/orthopedics_model.py", "Orthopedics Model (Bone X-Ray)"),
        ("backend/models/gastro_model.py", "Gastroenterology Model (Tabular)"),
        ("backend/models/general_model.py", "General Medicine Model (Symptoms)"),
        ("backend/models/router_model.py", "Router Model (BERT)"),
    ]
    
    for filepath, desc in model_files:
        total_checks += 1
        if check_file_exists(filepath, desc):
            passed_checks += 1
            lines = count_lines(filepath)
            if lines > 0:
                print(f"  └─ {lines} lines")
    
    # 3. Check Utilities
    print_header("3. Utility Modules")
    
    util_files = [
        ("backend/utils/__init__.py", "Utils package init"),
        ("backend/utils/dataset_downloader.py", "Dataset Downloader"),
        ("backend/utils/preprocessor.py", "Multi-Modal Preprocessor"),
        ("backend/utils/translator.py", "Medical Translator"),
        ("backend/utils/accuracy_checker.py", "Model Accuracy Checker"),
    ]
    
    for filepath, desc in util_files:
        total_checks += 1
        if check_file_exists(filepath, desc):
            passed_checks += 1
            lines = count_lines(filepath)
            if lines > 0:
                print(f"  └─ {lines} lines")
    
    # 4. Check Chatbot
    print_header("4. AI Chatbot System")
    
    chatbot_files = [
        ("backend/chatbot/__init__.py", "Chatbot package init"),
        ("backend/chatbot/nlp_engine.py", "NLP Engine (BERT)"),
        ("backend/chatbot/sentiment_analyzer.py", "Sentiment Analyzer"),
        ("backend/chatbot/voice_handler.py", "Voice Handler (STT/TTS)"),
    ]
    
    for filepath, desc in chatbot_files:
        total_checks += 1
        if check_file_exists(filepath, desc):
            passed_checks += 1
            lines = count_lines(filepath)
            if lines > 0:
                print(f"  └─ {lines} lines")
    
    # 5. Check Maps Integration
    print_header("5. Google Maps Integration")
    
    maps_files = [
        ("backend/maps/__init__.py", "Maps package init"),
        ("backend/maps/location_service.py", "Location Service"),
    ]
    
    for filepath, desc in maps_files:
        total_checks += 1
        if check_file_exists(filepath, desc):
            passed_checks += 1
            lines = count_lines(filepath)
            if lines > 0:
                print(f"  └─ {lines} lines")
    
    # 6. Check Frontend Structure
    print_header("6. Frontend Structure")
    
    frontend_files = [
        ("frontend/package.json", "Node.js dependencies"),
        ("frontend/.env", "Frontend environment"),
        ("frontend/src/index.js", "React entry point"),
        ("frontend/src/App.js", "Main App component"),
    ]
    
    for filepath, desc in frontend_files:
        total_checks += 1
        if check_file_exists(filepath, desc):
            passed_checks += 1
    
    # 7. Check Frontend Components
    print_header("7. Frontend Components")
    
    component_files = [
        ("frontend/src/components/Header.js", "Header Component"),
        ("frontend/src/components/Sidebar.js", "Sidebar Component"),
        ("frontend/src/components/LoginForm.js", "Login Form"),
        ("frontend/src/components/RegisterForm.js", "Register Form"),
    ]
    
    for filepath, desc in component_files:
        total_checks += 1
        if check_file_exists(filepath, desc):
            passed_checks += 1
    
    # 8. Check Frontend Pages
    print_header("8. Frontend Pages")
    
    page_files = [
        ("frontend/src/pages/Dashboard.js", "Dashboard Page"),
        ("frontend/src/pages/Diagnose.js", "Diagnosis Page"),
        ("frontend/src/pages/Chat.js", "Chat Interface"),
        ("frontend/src/pages/Maps.js", "Maps/Hospital Finder"),
        ("frontend/src/pages/History.js", "Diagnosis History"),
        ("frontend/src/pages/Profile.js", "User Profile"),
    ]
    
    for filepath, desc in page_files:
        total_checks += 1
        if check_file_exists(filepath, desc):
            passed_checks += 1
    
    # 9. Check Frontend Services
    print_header("9. Frontend Services")
    
    service_files = [
        ("frontend/src/services/api.js", "API Client (Axios)"),
        ("frontend/src/services/auth.js", "Auth Service"),
        ("frontend/src/styles/App.css", "Global Styles"),
    ]
    
    for filepath, desc in service_files:
        total_checks += 1
        if check_file_exists(filepath, desc):
            passed_checks += 1
    
    # 10. Check Docker Configuration
    print_header("10. Docker Configuration")
    
    docker_files = [
        ("Dockerfile", "Backend Dockerfile"),
        ("docker-compose.yml", "Docker Compose"),
    ]
    
    for filepath, desc in docker_files:
        total_checks += 1
        if check_file_exists(filepath, desc):
            passed_checks += 1
    
    # 11. Check Setup Scripts
    print_header("11. Setup Scripts")
    
    setup_files = [
        ("setup.sh", "Linux/Mac Setup Script"),
        ("setup.bat", "Windows Setup Script"),
    ]
    
    for filepath, desc in setup_files:
        total_checks += 1
        if check_file_exists(filepath, desc):
            passed_checks += 1
    
    # 12. Check Documentation
    print_header("12. Documentation")
    
    doc_files = [
        ("README.md", "Main README"),
        ("PROJECT_SUMMARY.md", "Project Summary"),
        ("FILE_STRUCTURE.md", "File Structure"),
        ("QUICKSTART.md", "Quick Start Guide"),
        ("IMPLEMENTATION_STATUS.md", "Implementation Status"),
    ]
    
    for filepath, desc in doc_files:
        total_checks += 1
        if check_file_exists(filepath, desc):
            passed_checks += 1
            lines = count_lines(filepath)
            if lines > 0:
                print(f"  └─ {lines} lines")
    
    # Calculate total lines of code
    print_header("Code Statistics")
    
    total_lines = 0
    backend_lines = 0
    frontend_lines = 0
    
    # Count backend Python files
    for root, dirs, files in os.walk("backend"):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                lines = count_lines(filepath)
                backend_lines += lines
                total_lines += lines
    
    # Count frontend JS files
    for root, dirs, files in os.walk("frontend/src"):
        for file in files:
            if file.endswith((".js", ".jsx", ".css")):
                filepath = os.path.join(root, file)
                lines = count_lines(filepath)
                frontend_lines += lines
                total_lines += lines
    
    print(f"Backend Python Code: {backend_lines:,} lines")
    print(f"Frontend JS/CSS Code: {frontend_lines:,} lines")
    print(f"Total Code: {total_lines:,} lines")
    
    # Final Summary
    print_header("Verification Summary")
    
    percentage = (passed_checks / total_checks * 100) if total_checks > 0 else 0
    
    print(f"Total Checks: {total_checks}")
    print(f"Passed: {GREEN}{passed_checks}{RESET}")
    print(f"Failed: {RED}{total_checks - passed_checks}{RESET}")
    print(f"Success Rate: {GREEN}{percentage:.1f}%{RESET}")
    
    if percentage == 100:
        print(f"\n{GREEN}{'='*60}{RESET}")
        print(f"{GREEN}✓ ALL CHECKS PASSED! MedAI-Pro is ready to use!{RESET}")
        print(f"{GREEN}{'='*60}{RESET}\n")
        print(f"\n{BLUE}Next Steps:{RESET}")
        print(f"1. Configure API keys in backend/.env and frontend/.env")
        print(f"2. Run: docker-compose up -d")
        print(f"3. Access: http://localhost:3000")
        print(f"4. See QUICKSTART.md for detailed instructions\n")
        return 0
    elif percentage >= 90:
        print(f"\n{YELLOW}{'='*60}{RESET}")
        print(f"{YELLOW}⚠ MOSTLY COMPLETE - Minor issues detected{RESET}")
        print(f"{YELLOW}{'='*60}{RESET}\n")
        return 1
    else:
        print(f"\n{RED}{'='*60}{RESET}")
        print(f"{RED}✗ INSTALLATION INCOMPLETE - Please check errors above{RESET}")
        print(f"{RED}{'='*60}{RESET}\n")
        return 2

if __name__ == "__main__":
    sys.exit(main())

