import requests
import sys
import json
import time
import concurrent.futures
from datetime import datetime
import uuid

class WizBookTester:
    def __init__(self, base_url="https://6c01608b-cf88-4ee1-bbbe-13267a9381af.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_failures = []
        self.minor_issues = []
        self.generated_book_ids = []  # Track generated books for cleanup

    def run_test(self, name, method, endpoint, expected_status, params=None, json_data=None, timeout=60, headers=None):
        """Run a single API test"""
        if endpoint.startswith('http'):
            url = endpoint
        elif endpoint == "":
            url = f"{self.api_url}/"  # Health check endpoint
        else:
            url = f"{self.api_url}/{endpoint}"
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            request_headers = headers or {}
            if method == 'GET':
                response = requests.get(url, params=params, timeout=timeout, headers=request_headers)
            elif method == 'POST':
                if json_data:
                    response = requests.post(url, json=json_data, timeout=timeout, headers=request_headers)
                else:
                    response = requests.post(url, json=params, timeout=timeout, headers=request_headers)
            elif method == 'OPTIONS':
                response = requests.options(url, timeout=timeout, headers=request_headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    if 'application/json' in response.headers.get('content-type', ''):
                        response_data = response.json()
                        print(f"   Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Non-dict response'}")
                        return True, response_data
                    elif 'application/pdf' in response.headers.get('content-type', ''):
                        print(f"   PDF Content-Length: {len(response.content)} bytes")
                        return True, response.content
                    else:
                        print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
                        print(f"   Content-Length: {len(response.content)} bytes")
                        return True, response.content
                except:
                    return True, response.text
            else:
                error_msg = f"Expected {expected_status}, got {response.status_code}"
                print(f"❌ Failed - {error_msg}")
                print(f"   Response: {response.text[:200]}...")
                self.critical_failures.append(f"{name}: {error_msg}")
                return False, {}

        except requests.exceptions.Timeout:
            error_msg = f"Request timed out after {timeout} seconds"
            print(f"❌ Failed - {error_msg}")
            self.critical_failures.append(f"{name}: {error_msg}")
            return False, {}
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"❌ Failed - {error_msg}")
            self.critical_failures.append(f"{name}: {error_msg}")
            return False, {}

    def test_health_check(self):
        """Test GET /api/ - Health check"""
        print("\n" + "="*60)
        print("🏥 HEALTH CHECK TESTS")
        print("="*60)
        
        success, response = self.run_test("Health Check", "GET", "", 200)
        if success and isinstance(response, dict):
            if 'message' in response and 'status' in response:
                print(f"   Message: {response.get('message')}")
                print(f"   Status: {response.get('status')}")
            else:
                self.minor_issues.append("Health check missing expected fields (message, status)")
        return success

    def test_ai_book_generation(self):
        """Test POST /api/generate-book - AI book generation with comprehensive testing"""
        print("\n" + "="*60)
        print("🤖 AI BOOK GENERATION TESTS")
        print("="*60)
        
        # Test 1: Basic book generation with all tiers
        tiers = ["basic", "pro", "premium"]
        tier_results = []
        
        for tier in tiers:
            print(f"\n🔍 Testing {tier.upper()} tier generation...")
            book_request = {
                "topic": "Python Programming for Beginners",
                "audience": "beginners",
                "style": "professional",
                "length": "medium",
                "tier": tier,
                "email": "test@wizbook.io"
            }
            
            success, response = self.run_test(
                f"AI Book Generation - {tier.upper()} Tier", 
                "POST", 
                "generate-book", 
                200,
                json_data=book_request,
                timeout=120
            )
            
            if success and isinstance(response, dict):
                required_fields = ['id', 'topic', 'audience', 'content', 'status', 'tier', 'word_count', 'created_at']
                missing_fields = [field for field in required_fields if field not in response]
                if missing_fields:
                    self.minor_issues.append(f"Generation response missing fields: {missing_fields}")
                else:
                    print(f"   Book ID: {response.get('id')}")
                    print(f"   Topic: {response.get('topic')}")
                    print(f"   Tier: {response.get('tier')}")
                    print(f"   Word Count: {response.get('word_count')}")
                    print(f"   Status: {response.get('status')}")
                    print(f"   Content Preview: {response.get('content', '')[:100]}...")
                    
                    # Store book ID for later tests
                    self.generated_book_ids.append(response.get('id'))
                    
                    # Validate word count expectations
                    word_count = response.get('word_count', 0)
                    expected_ranges = {
                        "basic": (3000, 10000),
                        "pro": (8000, 20000), 
                        "premium": (15000, 35000)
                    }
                    min_words, max_words = expected_ranges.get(tier, (0, 999999))
                    if not (min_words <= word_count <= max_words):
                        self.minor_issues.append(f"{tier} tier word count {word_count} outside expected range {min_words}-{max_words}")
            
            tier_results.append(success)
        
        # Test 2: Error handling - Invalid request
        print("\n🔍 Testing Error Handling - Invalid Request...")
        invalid_request = {
            "topic": "",  # Empty topic
            "audience": "beginners"
            # Missing required fields
        }
        
        error_success, error_response = self.run_test(
            "AI Generation - Invalid Request", 
            "POST", 
            "generate-book", 
            422,  # Expecting validation error
            json_data=invalid_request,
            timeout=30
        )
        
        # Test 3: Edge cases
        print("\n🔍 Testing Edge Cases...")
        edge_cases = [
            ("Long Topic", {"topic": "A" * 500, "audience": "professionals", "tier": "basic"}),
            ("Special Characters", {"topic": "Python & AI: 100% Success!", "audience": "beginners", "tier": "pro"}),
            ("Unicode Topic", {"topic": "机器学习与人工智能", "audience": "beginners", "tier": "basic"}),
        ]
        
        edge_results = []
        for case_name, request_data in edge_cases:
            success, response = self.run_test(
                f"AI Generation - {case_name}", 
                "POST", 
                "generate-book", 
                200,
                json_data=request_data,
                timeout=90
            )
            edge_results.append(success)
            if success and isinstance(response, dict):
                self.generated_book_ids.append(response.get('id'))
        
        return all(tier_results) and any(edge_results)

    def test_pdf_generation(self):
        """Test GET /api/pdf?topic=Python Programming - PDF generation with watermark"""
        print("\n" + "="*60)
        print("📄 PDF GENERATION TESTS")
        print("="*60)
        
        success, response = self.run_test(
            "PDF Generation - Python Programming", 
            "GET", 
            "pdf", 
            200,
            params={"topic": "Python Programming"},
            timeout=120
        )
        
        if success:
            if isinstance(response, bytes) and len(response) > 1000:
                print(f"   PDF Size: {len(response)} bytes")
                # Check if it's actually a PDF
                if response[:4] == b'%PDF':
                    print("   ✅ Valid PDF format detected")
                else:
                    self.minor_issues.append("PDF response doesn't start with PDF header")
            else:
                self.critical_failures.append("PDF Generation: Invalid or empty PDF response")
                success = False
        
        # Test error handling
        print("\n🔍 Testing PDF Error Handling - Missing Topic...")
        error_success, error_response = self.run_test(
            "PDF Generation - Missing Topic", 
            "GET", 
            "pdf", 
            422,
            timeout=30
        )
        
        if not error_success:
            error_success, error_response = self.run_test(
                "PDF Generation - Missing Topic (Alt)", 
                "GET", 
                "pdf", 
                400,
                timeout=30
            )
        
        return success

    def test_stripe_checkout(self):
        """Test GET /api/checkout?topic=Python Programming - Stripe payment flow"""
        print("\n" + "="*60)
        print("💳 STRIPE CHECKOUT TESTS")
        print("="*60)
        
        success, response = self.run_test(
            "Stripe Checkout - Python Programming", 
            "GET", 
            "checkout", 
            200,
            params={"topic": "Python Programming"},
            timeout=60
        )
        
        if success and isinstance(response, dict):
            required_fields = ['checkout_url', 'session_id']
            missing_fields = [field for field in required_fields if field not in response]
            if missing_fields:
                self.minor_issues.append(f"Checkout response missing fields: {missing_fields}")
            else:
                print(f"   Checkout URL: {response.get('checkout_url')}")
                print(f"   Session ID: {response.get('session_id')}")
                if response.get('demo'):
                    print("   ⚠️  Demo mode detected (Stripe keys not configured)")
                    self.minor_issues.append("Stripe running in demo mode")
        
        # Test default topic
        print("\n🔍 Testing Default Topic...")
        default_success, default_response = self.run_test(
            "Stripe Checkout - Default Topic", 
            "GET", 
            "checkout", 
            200,
            timeout=30
        )
        
        return success

    def test_cors_configuration(self):
        """Test CORS configuration"""
        print("\n" + "="*60)
        print("🌐 CORS CONFIGURATION TESTS")
        print("="*60)
        
        # Test preflight request
        try:
            response = requests.options(f"{self.api_url}/", headers={
                'Origin': 'https://wizbook.io',
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Content-Type'
            }, timeout=30)
            
            self.tests_run += 1
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            
            print(f"   CORS Headers: {cors_headers}")
            
            if cors_headers['Access-Control-Allow-Origin']:
                self.tests_passed += 1
                print("✅ CORS configured")
                return True
            else:
                print("❌ CORS not properly configured")
                self.critical_failures.append("CORS: Missing Access-Control-Allow-Origin header")
                return False
                
        except Exception as e:
            print(f"❌ CORS test failed: {str(e)}")
            self.critical_failures.append(f"CORS: {str(e)}")
            return False

    def test_static_file_serving(self):
        """Test static file serving - HTML frontend at root /"""
        print("\n" + "="*60)
        print("📁 STATIC FILE SERVING TESTS")
        print("="*60)
        
        success, response = self.run_test(
            "Static HTML Frontend", 
            "GET", 
            self.base_url,  # Root URL
            200,
            timeout=30
        )
        
        if success:
            if isinstance(response, (str, bytes)):
                content = response if isinstance(response, str) else response.decode('utf-8', errors='ignore')
                if 'WizBook.io' in content and 'html' in content.lower():
                    print("   ✅ HTML frontend detected")
                else:
                    self.minor_issues.append("Static serving: HTML content doesn't contain expected elements")
            else:
                self.critical_failures.append("Static serving: Invalid response type")
                success = False
        
        return success

    def test_environment_variables(self):
        """Test behavior with different environment variable configurations"""
        print("\n" + "="*60)
        print("🔧 ENVIRONMENT VARIABLE TESTS")
        print("="*60)
        
        # Test AI generation (should work with or without EMERGENT_LLM_KEY)
        print("🔍 Testing AI fallback mechanisms...")
        success, response = self.run_test(
            "AI Fallback Test", 
            "GET", 
            "generate", 
            200,
            params={"topic": "Test Topic"},
            timeout=90
        )
        
        if success:
            print("   ✅ AI generation working (fallback mechanisms functional)")
        
        # Test Stripe (should work in demo mode without keys)
        print("\n🔍 Testing Stripe demo mode...")
        stripe_success, stripe_response = self.run_test(
            "Stripe Demo Mode Test", 
            "GET", 
            "checkout", 
            200,
            params={"topic": "Test Topic"},
            timeout=30
        )
        
        if stripe_success and isinstance(stripe_response, dict):
            if stripe_response.get('demo'):
                print("   ✅ Stripe demo mode working")
            else:
                print("   ✅ Stripe live mode working")
        
        return success and stripe_success

    def test_load_testing(self):
        """Test multiple concurrent requests"""
        print("\n" + "="*60)
        print("⚡ LOAD TESTING")
        print("="*60)
        
        def make_request(i):
            try:
                response = requests.get(f"{self.api_url}/", timeout=30)
                return response.status_code == 200
            except:
                return False
        
        print("🔍 Testing 5 concurrent health check requests...")
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, i) for i in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        success_count = sum(results)
        
        self.tests_run += 1
        if success_count >= 4:  # Allow 1 failure
            self.tests_passed += 1
            print(f"✅ Load test passed: {success_count}/5 requests successful")
            print(f"   Total time: {end_time - start_time:.2f} seconds")
            return True
        else:
            print(f"❌ Load test failed: {success_count}/5 requests successful")
            self.critical_failures.append(f"Load test: Only {success_count}/5 requests successful")
            return False

    def test_edge_cases(self):
        """Test edge cases and error conditions"""
        print("\n" + "="*60)
        print("🧪 EDGE CASE TESTS")
        print("="*60)
        
        edge_cases = [
            ("Very Long Topic", "generate", {"topic": "A" * 1000}),
            ("Special Characters Topic", "generate", {"topic": "Python & AI: Machine Learning with 100% Success!"}),
            ("Empty Topic", "generate", {"topic": ""}),
            ("Unicode Topic", "generate", {"topic": "机器学习与人工智能"}),
        ]
        
        passed_edge_cases = 0
        for name, endpoint, params in edge_cases:
            print(f"\n🔍 Testing {name}...")
            try:
                response = requests.get(f"{self.api_url}/{endpoint}", params=params, timeout=60)
                self.tests_run += 1
                
                if response.status_code in [200, 400, 422]:  # Accept success or proper error
                    passed_edge_cases += 1
                    self.tests_passed += 1
                    print(f"   ✅ Handled properly (Status: {response.status_code})")
                else:
                    print(f"   ❌ Unexpected status: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Exception: {str(e)}")
                self.tests_run += 1
        
        return passed_edge_cases >= len(edge_cases) * 0.75  # 75% success rate

def main():
    print("🚀 COMPREHENSIVE PRE-LAUNCH BUG AUDIT for WizBook.io")
    print("=" * 80)
    print("Testing all critical endpoints and functionality before production deployment")
    print("=" * 80)
    
    tester = WizBookTester()
    
    # Run all comprehensive tests
    test_results = {}
    
    test_results['health_check'] = tester.test_health_check()
    test_results['ai_generation'] = tester.test_ai_generation()
    test_results['pdf_generation'] = tester.test_pdf_generation()
    test_results['stripe_checkout'] = tester.test_stripe_checkout()
    test_results['cors_config'] = tester.test_cors_configuration()
    test_results['static_serving'] = tester.test_static_file_serving()
    test_results['env_variables'] = tester.test_environment_variables()
    test_results['load_testing'] = tester.test_load_testing()
    test_results['edge_cases'] = tester.test_edge_cases()
    
    # Print comprehensive results
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 80)
    
    print(f"Total Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    print("\n🎯 TEST CATEGORY RESULTS:")
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    if tester.critical_failures:
        print("\n🚨 CRITICAL FAILURES (MUST FIX BEFORE LAUNCH):")
        for failure in tester.critical_failures:
            print(f"   ❌ {failure}")
    
    if tester.minor_issues:
        print("\n⚠️  MINOR ISSUES (RECOMMENDED FIXES):")
        for issue in tester.minor_issues:
            print(f"   ⚠️  {issue}")
    
    # Final verdict
    critical_tests_passed = all([
        test_results['health_check'],
        test_results['ai_generation'],
        test_results['pdf_generation'],
        test_results['cors_config'],
        test_results['static_serving']
    ])
    
    print("\n" + "=" * 80)
    if critical_tests_passed and not tester.critical_failures:
        print("🎉 READY FOR PRODUCTION LAUNCH!")
        print("All critical functionality is working properly.")
        if tester.minor_issues:
            print("Consider addressing minor issues for optimal user experience.")
        return 0
    else:
        print("🚨 NOT READY FOR LAUNCH!")
        print("Critical issues must be resolved before production deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())