"""
Load Testing Script for MedAI-Pro API
Tests API performance under load
"""

import time
import requests
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"
NUM_USERS = 50
NUM_REQUESTS_PER_USER = 10
MAX_WORKERS = 20

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(text):
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{text.center(70)}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")


def print_success(text):
    print(f"{GREEN}✓{RESET} {text}")


def print_error(text):
    print(f"{RED}✗{RESET} {text}")


def print_info(text):
    print(f"{YELLOW}ℹ{RESET} {text}")


class LoadTester:
    """Load testing class"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results = []
    
    def test_endpoint(self, endpoint: str, method: str = 'GET', data: dict = None) -> Dict:
        """Test a single endpoint"""
        start_time = time.time()
        
        try:
            if method == 'GET':
                response = requests.get(f"{self.base_url}{endpoint}", timeout=30)
            elif method == 'POST':
                response = requests.post(f"{self.base_url}{endpoint}", data=data, timeout=30)
            
            end_time = time.time()
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response_time': end_time - start_time,
                'endpoint': endpoint
            }
        except Exception as e:
            end_time = time.time()
            return {
                'success': False,
                'status_code': 0,
                'response_time': end_time - start_time,
                'endpoint': endpoint,
                'error': str(e)
            }
    
    def run_user_simulation(self, user_id: int) -> List[Dict]:
        """Simulate a single user making multiple requests"""
        user_results = []
        
        # Health check
        result = self.test_endpoint('/api/health')
        user_results.append(result)
        
        # Get languages
        result = self.test_endpoint('/api/languages')
        user_results.append(result)
        
        # Symptom routing
        result = self.test_endpoint(
            '/api/diagnose/route',
            method='POST',
            data={'symptoms': 'chest pain, shortness of breath'}
        )
        user_results.append(result)
        
        return user_results
    
    def run_load_test(self, num_users: int, max_workers: int):
        """Run load test with multiple concurrent users"""
        print_header("Load Test Configuration")
        print_info(f"Number of simulated users: {num_users}")
        print_info(f"Max concurrent workers: {max_workers}")
        print_info(f"Target API: {self.base_url}")
        
        # Check if API is available
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            if response.status_code != 200:
                print_error("API is not healthy")
                return False
            print_success("API is healthy and ready")
        except Exception as e:
            print_error(f"Cannot connect to API: {e}")
            return False
        
        print_header("Running Load Test")
        start_time = time.time()
        
        # Run concurrent user simulations
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self.run_user_simulation, user_id)
                for user_id in range(num_users)
            ]
            
            completed = 0
            for future in as_completed(futures):
                try:
                    user_results = future.result()
                    self.results.extend(user_results)
                    completed += 1
                    
                    if completed % 10 == 0:
                        print_info(f"Completed: {completed}/{num_users} users")
                except Exception as e:
                    print_error(f"User simulation failed: {e}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        self.analyze_results(total_time)
        
        return True
    
    def analyze_results(self, total_time: float):
        """Analyze and display test results"""
        print_header("Load Test Results")
        
        if not self.results:
            print_error("No results to analyze")
            return
        
        # Calculate statistics
        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r['success'])
        failed_requests = total_requests - successful_requests
        
        response_times = [r['response_time'] for r in self.results]
        avg_response_time = statistics.mean(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        median_response_time = statistics.median(response_times)
        
        if len(response_times) > 1:
            stdev_response_time = statistics.stdev(response_times)
        else:
            stdev_response_time = 0
        
        # Calculate percentiles
        sorted_times = sorted(response_times)
        p95_index = int(len(sorted_times) * 0.95)
        p99_index = int(len(sorted_times) * 0.99)
        p95_response_time = sorted_times[p95_index] if p95_index < len(sorted_times) else max_response_time
        p99_response_time = sorted_times[p99_index] if p99_index < len(sorted_times) else max_response_time
        
        # Requests per second
        rps = total_requests / total_time if total_time > 0 else 0
        
        # Display results
        print(f"{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}Overall Statistics{RESET}")
        print(f"{BLUE}{'='*70}{RESET}")
        print(f"Total Requests:        {total_requests}")
        print(f"Successful Requests:   {GREEN}{successful_requests}{RESET}")
        print(f"Failed Requests:       {RED}{failed_requests}{RESET}")
        print(f"Success Rate:          {GREEN}{(successful_requests/total_requests)*100:.2f}%{RESET}")
        print(f"Total Time:            {total_time:.2f}s")
        print(f"Requests/Second:       {rps:.2f}")
        
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}Response Time Statistics{RESET}")
        print(f"{BLUE}{'='*70}{RESET}")
        print(f"Average:               {avg_response_time*1000:.2f}ms")
        print(f"Median:                {median_response_time*1000:.2f}ms")
        print(f"Min:                   {min_response_time*1000:.2f}ms")
        print(f"Max:                   {max_response_time*1000:.2f}ms")
        print(f"Std Dev:               {stdev_response_time*1000:.2f}ms")
        print(f"95th Percentile:       {p95_response_time*1000:.2f}ms")
        print(f"99th Percentile:       {p99_response_time*1000:.2f}ms")
        
        # Endpoint breakdown
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}Endpoint Breakdown{RESET}")
        print(f"{BLUE}{'='*70}{RESET}")
        
        endpoints = {}
        for result in self.results:
            endpoint = result['endpoint']
            if endpoint not in endpoints:
                endpoints[endpoint] = []
            endpoints[endpoint].append(result)
        
        for endpoint, results in endpoints.items():
            success_count = sum(1 for r in results if r['success'])
            avg_time = statistics.mean([r['response_time'] for r in results])
            print(f"\n{endpoint}")
            print(f"  Requests: {len(results)}")
            print(f"  Success:  {success_count}/{len(results)} ({(success_count/len(results))*100:.1f}%)")
            print(f"  Avg Time: {avg_time*1000:.2f}ms")
        
        # Performance assessment
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}Performance Assessment{RESET}")
        print(f"{BLUE}{'='*70}{RESET}")
        
        if successful_requests / total_requests >= 0.99:
            print_success("✓ Excellent reliability (≥99% success rate)")
        elif successful_requests / total_requests >= 0.95:
            print_info("⚠ Good reliability (≥95% success rate)")
        else:
            print_error("✗ Poor reliability (<95% success rate)")
        
        if avg_response_time < 0.5:
            print_success("✓ Excellent response time (<500ms)")
        elif avg_response_time < 1.0:
            print_info("⚠ Good response time (<1s)")
        else:
            print_error("✗ Slow response time (≥1s)")
        
        if rps >= 50:
            print_success(f"✓ High throughput ({rps:.1f} req/s)")
        elif rps >= 20:
            print_info(f"⚠ Moderate throughput ({rps:.1f} req/s)")
        else:
            print_error(f"✗ Low throughput ({rps:.1f} req/s)")
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"load_test_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'configuration': {
                    'num_users': NUM_USERS,
                    'max_workers': MAX_WORKERS,
                    'base_url': self.base_url
                },
                'summary': {
                    'total_requests': total_requests,
                    'successful_requests': successful_requests,
                    'failed_requests': failed_requests,
                    'success_rate': successful_requests / total_requests,
                    'total_time': total_time,
                    'requests_per_second': rps,
                    'avg_response_time': avg_response_time,
                    'median_response_time': median_response_time,
                    'min_response_time': min_response_time,
                    'max_response_time': max_response_time,
                    'p95_response_time': p95_response_time,
                    'p99_response_time': p99_response_time
                },
                'detailed_results': self.results
            }, f, indent=2)
        
        print(f"\n{BLUE}{'='*70}{RESET}")
        print_success(f"Results saved to: {results_file}")
        print(f"{BLUE}{'='*70}{RESET}\n")


def main():
    """Main function"""
    print_header("MedAI-Pro Load Testing")
    
    tester = LoadTester(API_BASE_URL)
    success = tester.run_load_test(NUM_USERS, MAX_WORKERS)
    
    return 0 if success else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())

