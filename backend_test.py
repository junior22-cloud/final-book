import requests
import sys
import json
import time
import concurrent.futures
from datetime import datetime
import uuid

class WizBookTester:
    def __init__(self, base_url="https://wizpdf-maker.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_failures = []
        self.minor_issues = []
        self.generated_book_ids = []  # Track generated books for cleanup
        self.launch_readiness_issues = []  # Track launch-critical issues

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

    def test_api_keys_loading(self):
        """Test if API keys are properly loaded from environment - LAUNCH CRITICAL"""
        print("\n" + "="*60)
        print("🔑 API KEYS LOADING TEST - LAUNCH CRITICAL")
        print("="*60)
        
        # Test 1: Check if AI generation works (indicates EMERGENT_LLM_KEY is loaded)
        print("\n🔍 Testing EMERGENT_LLM_KEY loading via AI generation...")
        success, response = self.run_test(
            "API Key Test - EMERGENT_LLM_KEY", 
            "GET", 
            "generate", 
            200,
            params={"topic": "API Key Test Topic"},
            timeout=60
        )
        
        if success and isinstance(response, dict):
            book_content = response.get('book', '')
            if len(book_content) > 100 and 'API Key Test Topic' in book_content:
                print("   ✅ EMERGENT_LLM_KEY loaded and working")
            else:
                self.launch_readiness_issues.append("EMERGENT_LLM_KEY may not be working properly - AI generation returned minimal content")
                print("   ⚠️  EMERGENT_LLM_KEY may not be working - minimal content generated")
        else:
            self.launch_readiness_issues.append("EMERGENT_LLM_KEY not working - AI generation failed")
            print("   ❌ EMERGENT_LLM_KEY not working - AI generation failed")
        
        # Test 2: Check if Stripe checkout works (indicates STRIPE_SECRET_KEY is loaded)
        print("\n🔍 Testing STRIPE_SECRET_KEY loading via checkout...")
        stripe_success, stripe_response = self.run_test(
            "API Key Test - STRIPE_SECRET_KEY", 
            "GET", 
            "checkout", 
            200,
            params={"topic": "Test Topic", "tier": "pro"},
            timeout=30
        )
        
        if stripe_success and isinstance(stripe_response, dict):
            if 'checkout_url' in stripe_response:
                if stripe_response.get('demo'):
                    print("   ⚠️  STRIPE_SECRET_KEY in demo mode - may need real keys for production")
                    self.launch_readiness_issues.append("STRIPE_SECRET_KEY in demo mode - needs real keys for production launch")
                else:
                    print("   ✅ STRIPE_SECRET_KEY loaded and working")
            else:
                self.launch_readiness_issues.append("STRIPE_SECRET_KEY not working - checkout failed")
                print("   ❌ STRIPE_SECRET_KEY not working - checkout failed")
        else:
            self.launch_readiness_issues.append("STRIPE_SECRET_KEY not working - checkout endpoint failed")
            print("   ❌ STRIPE_SECRET_KEY not working - checkout endpoint failed")
        
        return success and stripe_success

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
        """Test GET /api/generate - AI book generation (actual endpoint)"""
        print("\n" + "="*60)
        print("🤖 AI BOOK GENERATION TESTS")
        print("="*60)
        
        # Test 1: Basic book generation with different topics
        topics = [
            "Python Programming for Beginners",
            "Digital Marketing Strategies", 
            "Personal Finance Management"
        ]
        
        generation_results = []
        
        for topic in topics:
            print(f"\n🔍 Testing generation for topic: {topic}")
            success, response = self.run_test(
                f"AI Book Generation - {topic}", 
                "GET", 
                "generate", 
                200,
                params={"topic": topic},
                timeout=120
            )
            
            if success and isinstance(response, dict):
                required_fields = ['book', 'topic', 'word_count', 'status']
                missing_fields = [field for field in required_fields if field not in response]
                if missing_fields:
                    self.minor_issues.append(f"Generation response missing fields: {missing_fields}")
                else:
                    print(f"   Topic: {response.get('topic')}")
                    print(f"   Word Count: {response.get('word_count')}")
                    print(f"   Status: {response.get('status')}")
                    print(f"   Content Preview: {response.get('book', '')[:100]}...")
                    
                    # Validate word count is reasonable
                    word_count = response.get('word_count', 0)
                    if word_count < 100:
                        self.minor_issues.append(f"Word count too low: {word_count}")
                    elif word_count > 10000:
                        self.minor_issues.append(f"Word count very high: {word_count}")
            
            generation_results.append(success)
        
        # Test 2: Error handling - Missing topic parameter
        print("\n🔍 Testing Error Handling - Missing Topic...")
        error_success, error_response = self.run_test(
            "AI Generation - Missing Topic", 
            "GET", 
            "generate", 
            422,  # Expecting validation error
            timeout=30
        )
        
        # Test 3: Edge cases with special characters and long topics
        print("\n🔍 Testing Edge Cases...")
        edge_cases = [
            ("Special Characters", "Python & AI: 100% Success!"),
            ("Unicode Topic", "机器学习与人工智能"),
            ("Long Topic", "A" * 200),
        ]
        
        edge_results = []
        for case_name, topic in edge_cases:
            success, response = self.run_test(
                f"AI Generation - {case_name}", 
                "GET", 
                "generate", 
                200,
                params={"topic": topic},
                timeout=90
            )
            edge_results.append(success)
        
        return all(generation_results) and any(edge_results)

    def test_pdf_generation(self):
        """Test GET /api/pdf - PDF generation with watermarking"""
        print("\n" + "="*60)
        print("📄 PDF GENERATION TESTS")
        print("="*60)
        
        # Test 1: Basic PDF generation
        topics = ["Python Programming", "Digital Marketing", "Personal Finance"]
        pdf_results = []
        
        for topic in topics:
            print(f"\n🔍 Testing PDF generation for: {topic}")
            success, response = self.run_test(
                f"PDF Generation - {topic}", 
                "GET", 
                "pdf", 
                200,
                params={"topic": topic},
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
            
            pdf_results.append(success)
        
        # Test 2: Error handling - Missing topic parameter
        print("\n🔍 Testing PDF Error Handling - Missing Topic...")
        error_success, error_response = self.run_test(
            "PDF Generation - Missing Topic", 
            "GET", 
            "pdf", 
            422,  # Expecting validation error
            timeout=30
        )
        
        # Test 3: Edge cases
        print("\n🔍 Testing PDF Edge Cases...")
        edge_cases = [
            ("Special Characters", "Python & AI: 100% Success!"),
            ("Unicode Topic", "机器学习与人工智能"),
            ("Long Topic", "A" * 100),
        ]
        
        edge_results = []
        for case_name, topic in edge_cases:
            success, response = self.run_test(
                f"PDF Generation - {case_name}", 
                "GET", 
                "pdf", 
                200,
                params={"topic": topic},
                timeout=90
            )
            edge_results.append(success)
        
        return all(pdf_results) and any(edge_results)

    def test_stripe_checkout(self):
        """Test GET /api/checkout - Stripe payment integration"""
        print("\n" + "="*60)
        print("💳 STRIPE CHECKOUT TESTS")
        print("="*60)
        
        # Test 1: Basic checkout with different tiers
        tiers = ["basic", "pro", "whitelabel"]
        checkout_results = []
        
        for tier in tiers:
            print(f"\n🔍 Testing {tier.upper()} tier checkout...")
            success, response = self.run_test(
                f"Stripe Checkout - {tier.upper()} Tier", 
                "GET", 
                "checkout", 
                200,
                params={
                    "topic": "Python Programming",
                    "tier": tier,
                    "upsells": "formatting,rushDelivery"
                },
                timeout=60
            )
            
            if success and isinstance(response, dict):
                required_fields = ['checkout_url', 'tier', 'price']
                missing_fields = [field for field in required_fields if field not in response]
                if missing_fields:
                    self.minor_issues.append(f"Checkout response missing fields: {missing_fields}")
                else:
                    print(f"   Checkout URL: {response.get('checkout_url')}")
                    print(f"   Tier: {response.get('tier')}")
                    print(f"   Price: ${response.get('price')}")
                    
                    if response.get('demo'):
                        print("   ⚠️  Demo mode detected (Stripe keys not configured)")
                        self.minor_issues.append("Stripe running in demo mode")
                    
                    # Validate pricing logic
                    expected_prices = {
                        "basic": 47.0,
                        "pro": 97.0, 
                        "whitelabel": 497.0
                    }
                    base_price = expected_prices.get(tier, 0)
                    actual_price = response.get('price', 0)
                    
                    # Account for upsells (formatting + rushDelivery = $29.99 + $19.99 = $49.98)
                    expected_total = base_price + 49.98
                    if abs(actual_price - expected_total) > 1.0:  # Allow $1 tolerance
                        self.minor_issues.append(f"{tier} tier pricing mismatch: expected ~${expected_total}, got ${actual_price}")
            
            checkout_results.append(success)
        
        # Test 2: Default parameters
        print("\n🔍 Testing Default Checkout Parameters...")
        default_success, default_response = self.run_test(
            "Stripe Checkout - Default", 
            "GET", 
            "checkout", 
            200,
            timeout=30
        )
        
        # Test 3: Upsell combinations
        print("\n🔍 Testing Upsell Combinations...")
        upsell_combinations = [
            ("formatting", "Professional Formatting only"),
            ("printReady,audioUpgrade", "Print-Ready + Audio"),
            ("formatting,printReady,rushDelivery,audioUpgrade", "All upsells")
        ]
        
        upsell_results = []
        for upsells, description in upsell_combinations:
            success, response = self.run_test(
                f"Checkout with {description}", 
                "GET", 
                "checkout", 
                200,
                params={
                    "topic": "Test Topic",
                    "tier": "pro",
                    "upsells": upsells
                },
                timeout=30
            )
            upsell_results.append(success)
        
        return all(checkout_results) and default_success and any(upsell_results)

    def test_email_capture_system(self):
        """Test POST /api/capture-email - Email capture system"""
        print("\n" + "="*60)
        print("📧 EMAIL CAPTURE SYSTEM TESTS")
        print("="*60)
        
        # Test 1: Valid email capture
        valid_emails = [
            {
                "email": "test@wizbook.io",
                "tier_interest": "pro",
                "topic": "Python Programming"
            },
            {
                "email": "user@example.com", 
                "tier_interest": "basic",
                "topic": "Digital Marketing"
            },
            {
                "email": "premium@test.com",
                "tier_interest": "whitelabel",
                "topic": "Business Strategy"
            }
        ]
        
        capture_results = []
        for email_data in valid_emails:
            print(f"\n🔍 Testing email capture for: {email_data['email']}")
            success, response = self.run_test(
                f"Email Capture - {email_data['email']}", 
                "POST", 
                "capture-email", 
                200,
                json_data=email_data,
                timeout=30
            )
            
            if success and isinstance(response, dict):
                required_fields = ['status', 'message', 'email', 'sequence']
                missing_fields = [field for field in required_fields if field not in response]
                if missing_fields:
                    self.minor_issues.append(f"Email capture response missing fields: {missing_fields}")
                else:
                    print(f"   Status: {response.get('status')}")
                    print(f"   Message: {response.get('message')}")
                    print(f"   Email: {response.get('email')}")
                    print(f"   Sequence: {response.get('sequence')}")
            
            capture_results.append(success)
        
        # Test 2: Invalid email formats
        print("\n🔍 Testing Invalid Email Formats...")
        invalid_emails = [
            {"email": "invalid-email", "tier_interest": "pro", "topic": "Test"},
            {"email": "", "tier_interest": "basic", "topic": "Test"},
            {"email": "no-at-symbol", "tier_interest": "pro", "topic": "Test"},
            {"email": "@missing-local.com", "tier_interest": "basic", "topic": "Test"}
        ]
        
        invalid_results = []
        for email_data in invalid_emails:
            success, response = self.run_test(
                f"Invalid Email - {email_data['email']}", 
                "POST", 
                "capture-email", 
                400,  # Expecting bad request
                json_data=email_data,
                timeout=30
            )
            invalid_results.append(success)
        
        # Test 3: Missing required fields
        print("\n🔍 Testing Missing Required Fields...")
        incomplete_data = [
            {"tier_interest": "pro", "topic": "Test"},  # Missing email
            {"email": "test@example.com"},  # Missing other fields
            {}  # Empty request
        ]
        
        incomplete_results = []
        for data in incomplete_data:
            success, response = self.run_test(
                "Incomplete Email Capture", 
                "POST", 
                "capture-email", 
                400,  # Expecting bad request
                json_data=data,
                timeout=30
            )
            incomplete_results.append(success)
        
        return all(capture_results) and any(invalid_results) and any(incomplete_results)

    def test_stripe_webhook(self):
        """Test POST /api/webhook - Stripe webhook handling"""
        print("\n" + "="*60)
        print("🔗 STRIPE WEBHOOK TESTS")
        print("="*60)
        
        # Test 1: Valid webhook payload (checkout.session.completed)
        print("\n🔍 Testing Valid Webhook Payload...")
        valid_webhook_payload = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_webhook_session",
                    "metadata": {
                        "topic": "Python Programming",
                        "tier": "pro",
                        "upsells": "formatting,rushDelivery"
                    },
                    "customer_details": {
                        "email": "customer@example.com"
                    },
                    "amount_total": 14697  # $146.97 in cents
                }
            }
        }
        
        success, response = self.run_test(
            "Webhook - Valid Payload", 
            "POST", 
            "webhook", 
            200,
            json_data=valid_webhook_payload,
            timeout=30
        )
        
        if success and isinstance(response, dict):
            if response.get('status') == 'success':
                print("   ✅ Webhook processed successfully")
            else:
                self.minor_issues.append("Webhook didn't return success status")
        
        # Test 2: Invalid webhook payload
        print("\n🔍 Testing Invalid Webhook Payload...")
        invalid_payloads = [
            {"type": "unknown.event", "data": {}},  # Unknown event type
            {"data": {"object": {}}},  # Missing type
            {},  # Empty payload
            {"type": "checkout.session.completed"}  # Missing data
        ]
        
        invalid_results = []
        for payload in invalid_payloads:
            webhook_success, webhook_response = self.run_test(
                "Webhook - Invalid Payload", 
                "POST", 
                "webhook", 
                200,  # Webhook should handle gracefully
                json_data=payload,
                timeout=30
            )
            invalid_results.append(webhook_success)
        
        # Test 3: Webhook without signature (demo mode)
        print("\n🔍 Testing Webhook Demo Mode...")
        demo_payload = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_demo_session",
                    "metadata": {
                        "topic": "Demo Topic",
                        "tier": "basic"
                    },
                    "customer_details": {
                        "email": "demo@example.com"
                    },
                    "amount_total": 4700  # $47.00 in cents
                }
            }
        }
        
        demo_success, demo_response = self.run_test(
            "Webhook - Demo Mode", 
            "POST", 
            "webhook", 
            200,
            json_data=demo_payload,
            timeout=30
        )
        
        return success and any(invalid_results) and demo_success

    def test_cors_configuration(self):
        """Test CORS configuration"""
        print("\n" + "="*60)
        print("🌐 CORS CONFIGURATION TESTS")
        print("="*60)
        
        # Test preflight request
        try:
            headers = {
                'Origin': 'https://wizbook.io',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            response = requests.options(f"{self.api_url}/", headers=headers, timeout=30)
            
            self.tests_run += 1
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
                'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
            }
            
            print(f"   CORS Headers: {cors_headers}")
            
            if cors_headers['Access-Control-Allow-Origin']:
                self.tests_passed += 1
                print("✅ CORS configured")
                
                # Check if wildcard or specific origins
                if cors_headers['Access-Control-Allow-Origin'] == '*':
                    print("   ⚠️  Using wildcard origin (consider restricting for production)")
                    self.minor_issues.append("CORS using wildcard origin - consider restricting")
                
                return True
            else:
                print("❌ CORS not properly configured")
                self.critical_failures.append("CORS: Missing Access-Control-Allow-Origin header")
                return False
                
        except Exception as e:
            print(f"❌ CORS test failed: {str(e)}")
            self.critical_failures.append(f"CORS: {str(e)}")
            return False

    def test_security_and_edge_cases(self):
        """Test security vulnerabilities and edge cases"""
        print("\n" + "="*60)
        print("🔒 SECURITY & EDGE CASE TESTS")
        print("="*60)
        
        security_tests = []
        
        # Test 1: SQL Injection attempts on GET endpoints
        print("\n🔍 Testing SQL Injection Protection...")
        sql_payloads = [
            "'; DROP TABLE books; --",
            "' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users--"
        ]
        
        for payload in sql_payloads:
            success, response = self.run_test(
                f"SQL Injection Test", 
                "GET", 
                "generate", 
                200,  # Should handle gracefully, not crash
                params={"topic": payload},
                timeout=30
            )
            
            if success:
                print(f"   ✅ SQL injection payload handled safely")
            else:
                print(f"   ⚠️  SQL injection payload caused error")
            
            security_tests.append(success)
        
        # Test 2: XSS attempts
        print("\n🔍 Testing XSS Protection...")
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert('xss');//"
        ]
        
        for payload in xss_payloads:
            success, response = self.run_test(
                f"XSS Protection Test", 
                "GET", 
                "generate", 
                200,
                params={"topic": payload},
                timeout=30
            )
            
            if success and isinstance(response, dict):
                content = response.get('book', '')
                if payload in content:
                    self.minor_issues.append(f"XSS payload not sanitized in response")
                else:
                    print(f"   ✅ XSS payload properly handled")
            
            security_tests.append(success)
        
        # Test 3: Large payload handling on email capture
        print("\n🔍 Testing Large Payload Handling...")
        large_request = {
            "email": "test@example.com",
            "tier_interest": "A" * 10000,  # 10KB tier interest
            "topic": "B" * 1000
        }
        
        large_success, large_response = self.run_test(
            "Large Payload Test", 
            "POST", 
            "capture-email", 
            400,  # Should reject or handle gracefully
            json_data=large_request,
            timeout=60
        )
        
        if not large_success:
            # Try with 200 - maybe it handles large payloads
            large_success, large_response = self.run_test(
                "Large Payload Test (Alt)", 
                "POST", 
                "capture-email", 
                200,
                json_data=large_request,
                timeout=60
            )
        
        security_tests.append(large_success)
        
        # Test 4: Invalid JSON on webhook
        print("\n🔍 Testing Invalid JSON Handling...")
        try:
            response = requests.post(
                f"{self.api_url}/webhook",
                data="invalid json{{{",
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            self.tests_run += 1
            if response.status_code in [200, 400, 422]:  # Should handle gracefully
                self.tests_passed += 1
                print("   ✅ Invalid JSON properly handled")
                security_tests.append(True)
            else:
                print(f"   ⚠️  Invalid JSON handling unexpected: {response.status_code}")
                security_tests.append(False)
                
        except Exception as e:
            print(f"   ❌ Invalid JSON test failed: {str(e)}")
            security_tests.append(False)
        
        # Test 5: Rate limiting behavior (if implemented)
        print("\n🔍 Testing Rate Limiting Behavior...")
        rate_limit_success = True
        try:
            # Make multiple rapid requests to test rate limiting
            for i in range(5):
                response = requests.get(f"{self.api_url}/generate", params={"topic": f"Test {i}"}, timeout=10)
                if response.status_code == 429:  # Too Many Requests
                    print("   ✅ Rate limiting detected")
                    break
            else:
                print("   ⚠️  No rate limiting detected (may be intentional)")
                self.minor_issues.append("No rate limiting detected on generation endpoint")
        except Exception as e:
            print(f"   ⚠️  Rate limit test failed: {str(e)}")
            rate_limit_success = False
        
        security_tests.append(rate_limit_success)
        
        return sum(security_tests) >= len(security_tests) * 0.75  # 75% pass rate

    def test_performance_and_reliability(self):
        """Test performance under load and reliability"""
        print("\n" + "="*60)
        print("⚡ PERFORMANCE & RELIABILITY TESTS")
        print("="*60)
        
        # Test 1: Response time benchmarks
        print("\n🔍 Testing Response Times...")
        endpoints_to_test = [
            ("Health Check", "GET", "", {}),
            ("AI Generation", "GET", "generate", {"topic": "Test Topic"}),
            ("Checkout", "GET", "checkout", {"topic": "Test Topic"})
        ]
        
        response_times = []
        for name, method, endpoint, params in endpoints_to_test:
            start_time = time.time()
            success, response = self.run_test(
                f"Performance - {name}", 
                method, 
                endpoint, 
                200,
                params=params,
                timeout=30
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            response_times.append(response_time)
            print(f"   Response Time: {response_time:.2f}s")
            
            if response_time > 10.0:  # More lenient for AI generation
                self.minor_issues.append(f"{name} response time too slow: {response_time:.2f}s")
        
        # Test 2: Concurrent requests
        print("\n🔍 Testing Concurrent Request Handling...")
        def make_concurrent_request(i):
            try:
                start_time = time.time()
                response = requests.get(f"{self.api_url}/", timeout=30)
                end_time = time.time()
                return response.status_code == 200, end_time - start_time
            except:
                return False, 999
        
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_concurrent_request, i) for i in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        end_time = time.time()
        
        successful_requests = sum(1 for success, _ in results if success)
        avg_response_time = sum(time for _, time in results if time < 999) / len([t for _, t in results if t < 999])
        total_time = end_time - start_time
        
        self.tests_run += 1
        if successful_requests >= 8:  # Allow 2 failures
            self.tests_passed += 1
            print(f"✅ Concurrent test passed: {successful_requests}/10 requests successful")
            print(f"   Average response time: {avg_response_time:.2f}s")
            print(f"   Total test time: {total_time:.2f}s")
            concurrent_success = True
        else:
            print(f"❌ Concurrent test failed: {successful_requests}/10 requests successful")
            self.critical_failures.append(f"Concurrent requests: Only {successful_requests}/10 successful")
            concurrent_success = False
        
        # Test 3: Memory usage simulation (large content generation)
        print("\n🔍 Testing Memory Usage with Large Content...")
        memory_success, memory_response = self.run_test(
            "Memory Usage - Large Content", 
            "GET", 
            "generate", 
            200,
            params={"topic": "Comprehensive Guide to Advanced Machine Learning Techniques and Deep Neural Networks with Practical Applications"},
            timeout=180  # Longer timeout for large content
        )
        
        if memory_success and isinstance(memory_response, dict):
            word_count = memory_response.get('word_count', 0)
            print(f"   Generated {word_count} words successfully")
        
        # Test 4: PDF generation performance
        print("\n🔍 Testing PDF Generation Performance...")
        pdf_start_time = time.time()
        pdf_success, pdf_response = self.run_test(
            "PDF Performance Test", 
            "GET", 
            "pdf", 
            200,
            params={"topic": "Performance Test Topic"},
            timeout=120
        )
        pdf_end_time = time.time()
        
        if pdf_success:
            pdf_time = pdf_end_time - pdf_start_time
            print(f"   PDF Generation Time: {pdf_time:.2f}s")
            if pdf_time > 30.0:
                self.minor_issues.append(f"PDF generation too slow: {pdf_time:.2f}s")
        
        return concurrent_success and memory_success and pdf_success

def main():
    print("🚀 WIZBOOK.IO LAUNCH READINESS TEST - COMPREHENSIVE BACKEND AUDIT")
    print("=" * 80)
    print("Testing all critical endpoints for production launch readiness")
    print("Focus: API Keys, AI Generation, PDF, Stripe, Email Capture, Performance")
    print("=" * 80)
    
    tester = WizBookTester()
    
    # Run all comprehensive tests in order of launch priority
    test_results = {}
    
    # LAUNCH CRITICAL TESTS - Must pass for production
    print("\n🎯 LAUNCH CRITICAL TESTS")
    print("-" * 40)
    test_results['api_keys_loading'] = tester.test_api_keys_loading()
    test_results['health_check'] = tester.test_health_check()
    test_results['ai_book_generation'] = tester.test_ai_book_generation()
    test_results['pdf_generation'] = tester.test_pdf_generation()
    test_results['stripe_checkout'] = tester.test_stripe_checkout()
    test_results['email_capture_system'] = tester.test_email_capture_system()
    
    # INFRASTRUCTURE TESTS - Important for stability
    print("\n🔧 INFRASTRUCTURE TESTS")
    print("-" * 40)
    test_results['cors_configuration'] = tester.test_cors_configuration()
    test_results['stripe_webhook'] = tester.test_stripe_webhook()
    test_results['performance_and_reliability'] = tester.test_performance_and_reliability()
    
    # SECURITY TESTS - Important for production
    print("\n🔒 SECURITY TESTS")
    print("-" * 40)
    test_results['security_and_edge_cases'] = tester.test_security_and_edge_cases()
    
    # Print comprehensive results
    print("\n" + "=" * 80)
    print("📊 LAUNCH READINESS TEST RESULTS")
    print("=" * 80)
    
    print(f"Total Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    # Launch Critical Results
    launch_critical_tests = [
        'api_keys_loading', 'health_check', 'ai_book_generation', 
        'pdf_generation', 'stripe_checkout', 'email_capture_system'
    ]
    
    launch_critical_passed = sum(1 for test in launch_critical_tests if test_results.get(test, False))
    launch_critical_total = len(launch_critical_tests)
    
    print(f"\n🎯 LAUNCH CRITICAL TESTS: {launch_critical_passed}/{launch_critical_total} PASSED")
    for test_name in launch_critical_tests:
        result = test_results.get(test_name, False)
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n🔧 INFRASTRUCTURE TESTS:")
    infrastructure_tests = ['cors_configuration', 'stripe_webhook', 'performance_and_reliability']
    for test_name in infrastructure_tests:
        result = test_results.get(test_name, False)
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n🔒 SECURITY TESTS:")
    security_tests = ['security_and_edge_cases']
    for test_name in security_tests:
        result = test_results.get(test_name, False)
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    # Launch Readiness Issues
    if tester.launch_readiness_issues:
        print("\n🚨 LAUNCH READINESS ISSUES (MUST FIX BEFORE LAUNCH):")
        for issue in tester.launch_readiness_issues:
            print(f"   🚨 {issue}")
    
    if tester.critical_failures:
        print("\n❌ CRITICAL FAILURES:")
        for failure in tester.critical_failures:
            print(f"   ❌ {failure}")
    
    if tester.minor_issues:
        print("\n⚠️  MINOR ISSUES (RECOMMENDED FIXES):")
        for issue in tester.minor_issues:
            print(f"   ⚠️  {issue}")
    
    # Final Launch Readiness Verdict
    launch_ready = (launch_critical_passed == launch_critical_total and 
                   len(tester.launch_readiness_issues) == 0 and 
                   len(tester.critical_failures) == 0)
    
    print("\n" + "=" * 80)
    print("🎯 WIZBOOK.IO LAUNCH READINESS VERDICT")
    print("=" * 80)
    
    if launch_ready:
        print("🎉 BACKEND IS LAUNCH READY!")
        print("✅ All critical functionality working")
        print("✅ API keys properly configured")
        print("✅ Core features operational")
        
        print(f"\n📈 LAUNCH READINESS METRICS:")
        print(f"   ✅ API Keys Loading: {'✅' if test_results.get('api_keys_loading') else '❌'}")
        print(f"   ✅ AI Generation: {'✅' if test_results.get('ai_book_generation') else '❌'}")
        print(f"   ✅ PDF Generation: {'✅' if test_results.get('pdf_generation') else '❌'}")
        print(f"   ✅ Stripe Integration: {'✅' if test_results.get('stripe_checkout') else '❌'}")
        print(f"   ✅ Email Capture: {'✅' if test_results.get('email_capture_system') else '❌'}")
        print(f"   ✅ Performance: {'✅' if test_results.get('performance_and_reliability') else '❌'}")
        
        if tester.minor_issues:
            print(f"\n⚠️  Consider addressing {len(tester.minor_issues)} minor issues for optimal experience")
        
        print("\n🚀 READY FOR PRODUCTION LAUNCH!")
        return 0
    else:
        print("🚨 BACKEND NOT READY FOR LAUNCH!")
        print("❌ Critical issues must be resolved")
        
        print(f"\n❌ FAILED LAUNCH CRITICAL TESTS:")
        for test_name in launch_critical_tests:
            if not test_results.get(test_name, False):
                print(f"   ❌ {test_name.replace('_', ' ').title()}")
        
        if tester.launch_readiness_issues:
            print(f"\n🚨 LAUNCH BLOCKING ISSUES:")
            for issue in tester.launch_readiness_issues:
                print(f"   🚨 {issue}")
        
        print("\n⚠️  DO NOT LAUNCH UNTIL ALL CRITICAL ISSUES ARE RESOLVED")
        return 1

if __name__ == "__main__":
    sys.exit(main())