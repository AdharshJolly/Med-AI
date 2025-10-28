"""
Integration Tests for MedAI-Pro API
Tests all API endpoints
"""

import unittest
import sys
from pathlib import Path
import requests
import json
import time

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = "test@medai.com"
TEST_USER_PASSWORD = "testpassword123"


class TestAuthEndpoints(unittest.TestCase):
    """Test Authentication Endpoints"""
    
    def test_01_register(self):
        """Test user registration"""
        response = requests.post(
            f"{API_BASE_URL}/api/auth/register",
            data={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "name": "Test User"
            }
        )
        
        # Should succeed or return 400 if user exists
        self.assertIn(response.status_code, [200, 400])
    
    def test_02_login(self):
        """Test user login"""
        response = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            data={
                "username": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('access_token', data)
        self.assertIn('token_type', data)
        
        # Save token for other tests
        global AUTH_TOKEN
        AUTH_TOKEN = data['access_token']
    
    def test_03_get_current_user(self):
        """Test get current user"""
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.get(
            f"{API_BASE_URL}/api/auth/me",
            headers=headers
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['email'], TEST_USER_EMAIL)


class TestDiagnosisEndpoints(unittest.TestCase):
    """Test Diagnosis Endpoints"""
    
    @classmethod
    def setUpClass(cls):
        cls.headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    def test_route_symptoms(self):
        """Test symptom routing"""
        response = requests.post(
            f"{API_BASE_URL}/api/diagnose/route",
            headers=self.headers,
            data={
                "symptoms": "chest pain, shortness of breath"
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('organ', data)
        self.assertIn('confidence', data)
    
    def test_symptom_diagnosis(self):
        """Test symptom-based diagnosis"""
        response = requests.post(
            f"{API_BASE_URL}/api/diagnose/symptoms",
            headers=self.headers,
            data={
                "symptoms": "fever, cough, fatigue"
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('diagnosis', data)
        self.assertIn('confidence', data)
    
    def test_get_diagnosis_history(self):
        """Test getting diagnosis history"""
        response = requests.get(
            f"{API_BASE_URL}/api/diagnose/history",
            headers=self.headers,
            params={"skip": 0, "limit": 10}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('diagnoses', data)
        self.assertIn('total', data)


class TestChatEndpoints(unittest.TestCase):
    """Test Chat Endpoints"""
    
    @classmethod
    def setUpClass(cls):
        cls.headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    def test_send_message(self):
        """Test sending chat message"""
        response = requests.post(
            f"{API_BASE_URL}/api/chat/message",
            headers=self.headers,
            data={
                "message": "What are the symptoms of pneumonia?",
                "language": "en"
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('response', data)
        self.assertIn('intent', data)


class TestLocationEndpoints(unittest.TestCase):
    """Test Location Endpoints"""
    
    def test_find_facilities(self):
        """Test finding nearby facilities"""
        response = requests.post(
            f"{API_BASE_URL}/api/location/find-facilities",
            data={
                "location": "New York, NY",
                "facility_type": "hospital",
                "radius": 5000
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('facilities', data)


class TestSystemEndpoints(unittest.TestCase):
    """Test System Endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = requests.get(f"{API_BASE_URL}/api/health")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
    
    def test_get_languages(self):
        """Test get supported languages"""
        response = requests.get(f"{API_BASE_URL}/api/languages")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('languages', data)
        self.assertGreaterEqual(len(data['languages']), 12)


class TestLoadTesting(unittest.TestCase):
    """Load Testing"""
    
    def test_concurrent_requests(self):
        """Test handling concurrent requests"""
        import concurrent.futures
        
        def make_request():
            response = requests.get(f"{API_BASE_URL}/api/health")
            return response.status_code == 200
        
        # Send 50 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        success_rate = sum(results) / len(results)
        self.assertGreaterEqual(success_rate, 0.95)  # 95% success rate
    
    def test_response_time(self):
        """Test API response time"""
        start_time = time.time()
        response = requests.get(f"{API_BASE_URL}/api/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Response should be under 1 second
        self.assertLess(response_time, 1.0)


def run_all_tests():
    """Run all API tests"""
    print("=" * 70)
    print("MedAI-Pro API Integration Tests".center(70))
    print("=" * 70)
    print()
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ API is not running or not healthy")
            print("Please start the API with: docker-compose up -d")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API")
        print(f"Please ensure API is running at {API_BASE_URL}")
        return False
    
    print("✅ API is running and healthy")
    print()
    
    # Run tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes in order
    suite.addTests(loader.loadTestsFromTestCase(TestAuthEndpoints))
    suite.addTests(loader.loadTestsFromTestCase(TestDiagnosisEndpoints))
    suite.addTests(loader.loadTestsFromTestCase(TestChatEndpoints))
    suite.addTests(loader.loadTestsFromTestCase(TestLocationEndpoints))
    suite.addTests(loader.loadTestsFromTestCase(TestSystemEndpoints))
    suite.addTests(loader.loadTestsFromTestCase(TestLoadTesting))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("=" * 70)
    print("Test Summary".center(70))
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)

