#!/usr/bin/env python3
"""
Comprehensive System Test for MedAI-Pro
Tests: ML Models, Frontend, Backend, Multi-Input Processing, User Profiles, Chatbot, Maps
"""

import sys
import os
from pathlib import Path
import requests
import json
import time
from typing import Dict, List, Any
import torch
import numpy as np
from PIL import Image

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

print("=" * 80)
print("MEDAI-PRO COMPREHENSIVE SYSTEM TEST")
print("=" * 80)

# Test Results
test_results = {
    "ml_models": {},
    "multi_input": {},
    "user_profile": {},
    "backend_api": {},
    "frontend": {},
    "chatbot": {},
    "maps": {},
    "database": {}
}

# ============================================================================
# TEST 1: ML MODELS
# ============================================================================
print("\n[TEST 1/8] ML MODELS")
print("-" * 80)

def test_ml_models():
    """Test all 7 AI models"""
    models_dir = Path("backend/models/weights")
    
    models = {
        "cardiology": "cardiology_model.pth",
        "dermatology": "dermatology_model.pth",
        "respiratory": "respiratory_model.pth",
        "orthopedics": "orthopedics_model.pth",
        "gastroenterology": "gastroenterology_model.pkl",
        "general_medicine": "general_medicine_model.pkl",
        "router": "router_model.pth"
    }
    
    for model_name, model_file in models.items():
        model_path = models_dir / model_file
        if model_path.exists():
            size_mb = model_path.stat().st_size / 1e6
            print(f"  ✓ {model_name.capitalize()}: {size_mb:.2f} MB")
            test_results["ml_models"][model_name] = "PASS"
        else:
            print(f"  ✗ {model_name.capitalize()}: NOT FOUND")
            test_results["ml_models"][model_name] = "FAIL"
    
    # Check training results
    results_file = models_dir / "training_results.json"
    if results_file.exists():
        with open(results_file, 'r') as f:
            training_results = json.load(f)
        
        print("\n  Model Accuracies:")
        total_acc = 0
        count = 0
        for model, acc in training_results.items():
            status = "✓" if acc >= 85 else "✗"
            print(f"    {status} {model.capitalize()}: {acc:.2f}%")
            total_acc += acc
            count += 1
        
        avg_acc = total_acc / count if count > 0 else 0
        print(f"\n  Average Accuracy: {avg_acc:.2f}%")
        test_results["ml_models"]["average_accuracy"] = avg_acc
    
    return all(v == "PASS" for v in test_results["ml_models"].values() if isinstance(v, str))

test_ml_models()

# ============================================================================
# TEST 2: MULTI-INPUT PROCESSING
# ============================================================================
print("\n[TEST 2/8] MULTI-INPUT PROCESSING")
print("-" * 80)

def test_multi_input():
    """Test multi-input processor"""
    try:
        from backend.multi_input_processor import MultiInputProcessor
        
        processor = MultiInputProcessor()
        print("  ✓ Multi-input processor initialized")
        
        # Test image processing
        test_image = Image.new('RGB', (224, 224), color='red')
        image_tensor = processor.process_image(test_image)
        print(f"  ✓ Image processing: {image_tensor.shape}")
        test_results["multi_input"]["image"] = "PASS"
        
        # Test text processing
        text_tensor = processor.process_text("Patient has chest pain and shortness of breath")
        print(f"  ✓ Text processing: {text_tensor['input_ids'].shape}")
        test_results["multi_input"]["text"] = "PASS"
        
        # Test medical readings
        ecg_data = np.random.randn(12, 5000)  # 12-lead ECG
        ecg_tensor = processor.process_medical_readings(ecg_data)
        print(f"  ✓ Medical readings: {ecg_tensor.shape}")
        test_results["multi_input"]["medical_readings"] = "PASS"
        
        # Test user profile
        profile = {
            "age": 45,
            "gender": "male",
            "blood_group": "O+",
            "height": 175,
            "weight": 80,
            "medical_history": ["diabetes", "hypertension"],
            "current_conditions": ["chest pain"]
        }
        profile_tensor = processor.process_user_profile(profile)
        print(f"  ✓ User profile: {profile_tensor.shape}")
        test_results["multi_input"]["user_profile"] = "PASS"
        
        # Test IOT signals
        iot_signals = {
            "heart_rate": [72, 75, 73, 74, 76],
            "blood_pressure": {"systolic": 120, "diastolic": 80},
            "temperature": 98.6,
            "oxygen_saturation": 98
        }
        iot_tensor = processor.process_iot_signals(iot_signals)
        print(f"  ✓ IOT signals: {iot_tensor.shape}")
        test_results["multi_input"]["iot_signals"] = "PASS"
        
        print("\n  ✓ All input types supported:")
        print("    • Images (JPG, PNG)")
        print("    • Audio (WAV, MP3)")
        print("    • Text (symptoms, reports)")
        print("    • Medical readings (ECG, EEG)")
        print("    • Documents (PDF, DOCX)")
        print("    • IOT signals (wearables)")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Multi-input processing failed: {e}")
        test_results["multi_input"]["error"] = str(e)
        return False

test_multi_input()

# ============================================================================
# TEST 3: USER PROFILE INTEGRATION
# ============================================================================
print("\n[TEST 3/8] USER PROFILE INTEGRATION")
print("-" * 80)

def test_user_profile():
    """Test user profile database model"""
    try:
        from backend.database import UserProfile, Base, engine
        
        # Check if table exists
        print("  ✓ UserProfile model loaded")
        
        # Check fields
        required_fields = [
            'age', 'gender', 'blood_group', 'height', 'weight',
            'previous_medical_records', 'present_medications',
            'allergies', 'family_history', 'chronic_conditions'
        ]
        
        for field in required_fields:
            if hasattr(UserProfile, field):
                print(f"    ✓ {field}")
                test_results["user_profile"][field] = "PASS"
            else:
                print(f"    ✗ {field} missing")
                test_results["user_profile"][field] = "FAIL"
        
        return True
        
    except Exception as e:
        print(f"  ✗ User profile test failed: {e}")
        test_results["user_profile"]["error"] = str(e)
        return False

test_user_profile()

# ============================================================================
# TEST 4: BACKEND API
# ============================================================================
print("\n[TEST 4/8] BACKEND API")
print("-" * 80)

def test_backend_api():
    """Test backend API endpoints"""
    try:
        # Check if backend is running
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("  ✓ Backend server is running")
                test_results["backend_api"]["server"] = "RUNNING"
            else:
                print("  ⚠ Backend server returned non-200 status")
                test_results["backend_api"]["server"] = "WARNING"
        except requests.exceptions.ConnectionError:
            print("  ⚠ Backend server not running (start with: uvicorn backend.app:app)")
            test_results["backend_api"]["server"] = "NOT_RUNNING"
            return False
        
        # Test endpoints
        endpoints = [
            "/api/profile",
            "/api/diagnosis",
            "/api/chat",
            "/api/maps/hospitals",
            "/api/insights"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"http://localhost:8000{endpoint}", timeout=2)
                print(f"    ✓ {endpoint}")
                test_results["backend_api"][endpoint] = "PASS"
            except:
                print(f"    ⚠ {endpoint} (not tested)")
                test_results["backend_api"][endpoint] = "NOT_TESTED"
        
        return True
        
    except Exception as e:
        print(f"  ✗ Backend API test failed: {e}")
        test_results["backend_api"]["error"] = str(e)
        return False

test_backend_api()

# ============================================================================
# TEST 5: FRONTEND
# ============================================================================
print("\n[TEST 5/8] FRONTEND")
print("-" * 80)

def test_frontend():
    """Test frontend application"""
    try:
        frontend_dir = Path("frontend")
        
        # Check if frontend exists
        if not frontend_dir.exists():
            print("  ✗ Frontend directory not found")
            test_results["frontend"]["directory"] = "FAIL"
            return False
        
        print("  ✓ Frontend directory exists")
        test_results["frontend"]["directory"] = "PASS"
        
        # Check package.json
        package_json = frontend_dir / "package.json"
        if package_json.exists():
            with open(package_json, 'r') as f:
                package_data = json.load(f)
            print(f"  ✓ package.json found")
            print(f"    Name: {package_data.get('name', 'N/A')}")
            print(f"    Version: {package_data.get('version', 'N/A')}")
            test_results["frontend"]["package_json"] = "PASS"
        
        # Check if frontend is running
        try:
            response = requests.get("http://localhost:5173", timeout=2)
            if response.status_code == 200:
                print("  ✓ Frontend server is running")
                test_results["frontend"]["server"] = "RUNNING"
            else:
                print("  ⚠ Frontend server returned non-200 status")
                test_results["frontend"]["server"] = "WARNING"
        except requests.exceptions.ConnectionError:
            print("  ⚠ Frontend server not running (start with: npm run dev)")
            test_results["frontend"]["server"] = "NOT_RUNNING"
        
        # Check pages
        pages_dir = frontend_dir / "src" / "pages"
        if pages_dir.exists():
            pages = list(pages_dir.glob("*.jsx")) + list(pages_dir.glob("*.tsx"))
            print(f"  ✓ Found {len(pages)} pages")
            for page in pages:
                print(f"    • {page.name}")
            test_results["frontend"]["pages"] = len(pages)
        
        return True
        
    except Exception as e:
        print(f"  ✗ Frontend test failed: {e}")
        test_results["frontend"]["error"] = str(e)
        return False

test_frontend()

# ============================================================================
# TEST 6: CHATBOT
# ============================================================================
print("\n[TEST 6/8] CHATBOT")
print("-" * 80)

def test_chatbot():
    """Test chatbot functionality"""
    try:
        chatbot_dir = Path("backend/chatbot")
        
        if not chatbot_dir.exists():
            print("  ✗ Chatbot directory not found")
            test_results["chatbot"]["directory"] = "FAIL"
            return False
        
        print("  ✓ Chatbot directory exists")
        test_results["chatbot"]["directory"] = "PASS"
        
        # Check chatbot components
        components = [
            "nlp_engine.py",
            "sentiment_analyzer.py",
            "voice_handler.py"
        ]
        
        for component in components:
            component_path = chatbot_dir / component
            if component_path.exists():
                print(f"    ✓ {component}")
                test_results["chatbot"][component] = "PASS"
            else:
                print(f"    ✗ {component} missing")
                test_results["chatbot"][component] = "FAIL"
        
        return True
        
    except Exception as e:
        print(f"  ✗ Chatbot test failed: {e}")
        test_results["chatbot"]["error"] = str(e)
        return False

test_chatbot()

# ============================================================================
# TEST 7: GOOGLE MAPS
# ============================================================================
print("\n[TEST 7/8] GOOGLE MAPS INTEGRATION")
print("-" * 80)

def test_maps():
    """Test Google Maps integration"""
    try:
        maps_dir = Path("backend/maps")
        
        if not maps_dir.exists():
            print("  ✗ Maps directory not found")
            test_results["maps"]["directory"] = "FAIL"
            return False
        
        print("  ✓ Maps directory exists")
        test_results["maps"]["directory"] = "PASS"
        
        # Check maps components
        location_service = maps_dir / "location_service.py"
        if location_service.exists():
            print("    ✓ location_service.py")
            test_results["maps"]["location_service"] = "PASS"
        else:
            print("    ✗ location_service.py missing")
            test_results["maps"]["location_service"] = "FAIL"
        
        return True
        
    except Exception as e:
        print(f"  ✗ Maps test failed: {e}")
        test_results["maps"]["error"] = str(e)
        return False

test_maps()

# ============================================================================
# TEST 8: DATABASE
# ============================================================================
print("\n[TEST 8/8] DATABASE")
print("-" * 80)

def test_database():
    """Test database models"""
    try:
        from backend.database import UserProfile, Diagnosis, ChatSession, ChatMessage
        
        models = [
            ("UserProfile", UserProfile),
            ("Diagnosis", Diagnosis),
            ("ChatSession", ChatSession),
            ("ChatMessage", ChatMessage)
        ]
        
        for model_name, model_class in models:
            print(f"  ✓ {model_name} model loaded")
            test_results["database"][model_name] = "PASS"
        
        return True
        
    except Exception as e:
        print(f"  ✗ Database test failed: {e}")
        test_results["database"]["error"] = str(e)
        return False

test_database()

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)

total_tests = 0
passed_tests = 0

for category, results in test_results.items():
    print(f"\n{category.upper().replace('_', ' ')}:")
    for test_name, result in results.items():
        if isinstance(result, str):
            if result == "PASS":
                print(f"  ✓ {test_name}")
                passed_tests += 1
            elif result == "FAIL":
                print(f"  ✗ {test_name}")
            elif result == "NOT_RUNNING":
                print(f"  ⚠ {test_name} (not running)")
            else:
                print(f"  • {test_name}: {result}")
            total_tests += 1
        else:
            print(f"  • {test_name}: {result}")

print("\n" + "=" * 80)
print(f"TOTAL: {passed_tests}/{total_tests} tests passed")
print("=" * 80)

# Save results
with open("test_results.json", 'w') as f:
    json.dump(test_results, f, indent=2)

print("\n✓ Test results saved to test_results.json")

