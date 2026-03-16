import requests
import sys
import json
from datetime import datetime

class JSONAnonymizerTester:
    def __init__(self, base_url="https://maskdata-json.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    json_response = response.json()
                    return success, json_response
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_api_root(self):
        """Test API root endpoint"""
        success, response = self.run_test(
            "API Root",
            "GET",
            "/api/",
            200
        )
        return success

    def test_basic_anonymization(self):
        """Test basic JSON anonymization"""
        test_data = {
            "nom": "Dupont",
            "prenom": "Jean",
            "email": "jean.dupont@gmail.com",
            "telephone": "06 12 34 56 78"
        }
        
        success, response = self.run_test(
            "Basic Anonymization",
            "POST",
            "/api/anonymize",
            200,
            data={"data": test_data}
        )
        
        if success:
            # Verify response structure
            if 'success' in response and response['success']:
                print(f"   → Detected {len(response.get('detected_fields', []))} sensitive fields")
                if response.get('detected_fields'):
                    for field in response['detected_fields'][:3]:  # Show first 3
                        print(f"   → Field '{field['path']}' ({field['type']}): {field['original']} → {field['anonymized']}")
                return True
            else:
                print(f"❌ API returned success=false")
                return False
        return False

    def test_complex_json_anonymization(self):
        """Test complex nested JSON anonymization"""
        complex_data = {
            "utilisateur": {
                "nom": "Martin", 
                "prenom": "Marie",
                "email": "marie.martin@orange.fr",
                "telephone": "07 98 76 54 32",
                "adresse": "15 rue de la Paix",
                "code_postal": "75001",
                "ville": "Paris"
            },
            "informations_bancaires": {
                "iban": "FR76 3000 6000 0112 3456 7890 189",
                "titulaire": "Marie Martin"
            },
            "securite_sociale": {
                "numero_secu": "2 85 12 75 108 123 45",
                "date_naissance": "15/12/1985"
            },
            "contacts": [
                {
                    "nom": "Dubois",
                    "prenom": "Pierre", 
                    "email": "pierre.dubois@free.fr",
                    "telephone": "06 11 22 33 44"
                }
            ]
        }
        
        success, response = self.run_test(
            "Complex JSON Anonymization",
            "POST", 
            "/api/anonymize",
            200,
            data={"data": complex_data}
        )
        
        if success:
            detected_fields = response.get('detected_fields', [])
            stats = response.get('stats', {})
            
            print(f"   → Detected {len(detected_fields)} sensitive fields")
            print(f"   → Stats: {stats}")
            
            # Verify we detected expected field types
            expected_types = ['nom', 'prenom', 'email', 'telephone', 'adresse', 'iban', 'secu']
            detected_types = [f['type'] for f in detected_fields]
            
            found_types = set(detected_types) & set(expected_types)
            print(f"   → Found expected types: {sorted(found_types)}")
            
            return len(found_types) >= 5  # At least 5 different types should be found
        
        return False

    def test_invalid_json(self):
        """Test API error handling with invalid JSON structure"""
        success, response = self.run_test(
            "Invalid JSON Handling",
            "POST",
            "/api/anonymize", 
            400,  # Should return 400 for bad request
            data={"invalid": "structure"}  # Missing 'data' key
        )
        return success

    def test_empty_data(self):
        """Test anonymization with empty data"""
        success, response = self.run_test(
            "Empty Data Anonymization",
            "POST",
            "/api/anonymize",
            200,
            data={"data": {}}
        )
        
        if success:
            # Should succeed but detect no fields
            detected_count = len(response.get('detected_fields', []))
            print(f"   → Detected {detected_count} fields (expected: 0)")
            return detected_count == 0
        
        return False

def main():
    # Setup
    print("🚀 Starting JSON Anonymizer API Tests")
    print("=" * 50)
    
    tester = JSONAnonymizerTester()

    # Run tests
    print("\n📋 TESTING API ENDPOINTS")
    tester.test_api_root()
    
    print("\n📋 TESTING ANONYMIZATION FUNCTIONALITY")
    tester.test_basic_anonymization()
    tester.test_complex_json_anonymization()
    tester.test_empty_data()
    
    print("\n📋 TESTING ERROR HANDLING")
    tester.test_invalid_json()

    # Print results
    print(f"\n📊 FINAL RESULTS")
    print("=" * 50)
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    success_rate = (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("✅ Backend tests PASSED")
        return 0
    else:
        print("❌ Backend tests FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())