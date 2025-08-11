import requests
import sys
import json
from datetime import datetime

class AIBookGeneratorTester:
    def __init__(self, base_url="https://ed0e24b7-92dc-464b-85c3-5e282ec65ef5.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.generated_book_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=60):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if not endpoint.startswith('http') else endpoint
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Non-dict response'}")
                    return True, response_data
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timed out after {timeout} seconds")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        return self.run_test("Root API Endpoint", "GET", "", 200)

    def test_pricing_endpoint(self):
        """Test pricing tiers endpoint"""
        success, response = self.run_test("Pricing Endpoint", "GET", "pricing", 200)
        if success and isinstance(response, dict):
            tiers = response.get('tiers', [])
            print(f"   Found {len(tiers)} pricing tiers")
            for tier in tiers:
                print(f"   - {tier.get('name', 'Unknown')}: ${tier.get('price', 'N/A')}")
        return success

    def test_book_generation(self):
        """Test book generation endpoint"""
        book_data = {
            "topic": "Python Programming",
            "audience": "complete beginners", 
            "style": "casual",
            "length": "medium",
            "tier": "pro",
            "email": "test@example.com"
        }
        
        success, response = self.run_test(
            "Book Generation", 
            "POST", 
            "generate-book", 
            200, 
            data=book_data,
            timeout=120  # Longer timeout for AI generation
        )
        
        if success and isinstance(response, dict):
            self.generated_book_id = response.get('id')
            print(f"   Generated book ID: {self.generated_book_id}")
            print(f"   Word count: {response.get('word_count', 'N/A')}")
            print(f"   Status: {response.get('status', 'N/A')}")
            print(f"   Content preview: {response.get('content', '')[:100]}...")
        
        return success

    def test_get_book(self):
        """Test retrieving a generated book"""
        if not self.generated_book_id:
            print("❌ Skipping - No book ID available from generation test")
            return False
            
        return self.run_test(
            "Get Book by ID", 
            "GET", 
            f"book/{self.generated_book_id}", 
            200
        )

    def test_pdf_download(self):
        """Test PDF download endpoint"""
        if not self.generated_book_id:
            print("❌ Skipping - No book ID available from generation test")
            return False
            
        url = f"{self.api_url}/book/{self.generated_book_id}/pdf"
        print(f"\n🔍 Testing PDF Download...")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, timeout=60)
            self.tests_run += 1
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                
                if 'application/pdf' in content_type and content_length > 1000:
                    self.tests_passed += 1
                    print(f"✅ Passed - PDF generated successfully")
                    print(f"   Content-Type: {content_type}")
                    print(f"   Size: {content_length} bytes")
                    return True
                else:
                    print(f"❌ Failed - Invalid PDF response")
                    print(f"   Content-Type: {content_type}")
                    print(f"   Size: {content_length} bytes")
                    return False
            else:
                print(f"❌ Failed - Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return False
                
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False

    def test_list_books(self):
        """Test listing books endpoint"""
        return self.run_test("List Books", "GET", "books", 200)

def main():
    print("🚀 Starting AI Book Generator API Tests")
    print("=" * 50)
    
    tester = AIBookGeneratorTester()
    
    # Run all tests
    tests = [
        tester.test_root_endpoint,
        tester.test_pricing_endpoint,
        tester.test_book_generation,
        tester.test_get_book,
        tester.test_pdf_download,
        tester.test_list_books
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())