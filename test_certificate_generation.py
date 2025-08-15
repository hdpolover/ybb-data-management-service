"""
Certificate Generation Test Script
Tests certificate generation functionality with sample data
"""
import requests
import json
import base64
from datetime import datetime, date
import os

# Configuration
API_BASE_URL = "http://127.0.0.1:5000/api/ybb/certificates"
TEST_OUTPUT_DIR = "test_certificates"

def create_test_data():
    """Create sample test data for certificate generation"""
    return {
        "participant": {
            "id": 12345,
            "account_id": "test123456789",
            "full_name": "John Doe",
            "birthdate": "1995-03-15",
            "gender": "male",
            "nationality": "Indonesia",
            "nationality_code": "ID",
            "education_level": "bachelor",
            "major": "Computer Science",
            "institution": "University of Technology Jakarta",
            "occupation": "Student",
            "category": "fully_funded",
            "picture_url": "https://example.com/photo.jpg",
            "instagram_account": "johndoe",
            "experiences": "Software development intern at Tech Corp, participated in hackathons",
            "achievements": "Dean's List 2023, Programming Competition Winner",
            "tshirt_size": "L",
            "registration_date": "2024-06-01T10:00:00Z"
        },
        "program": {
            "id": 5,
            "name": "Youth Break the Boundaries 2025",
            "theme": "Innovation and Leadership for Global Impact",
            "start_date": "2024-08-01",
            "end_date": "2024-08-15"
        },
        "award": {
            "id": 1,
            "title": "Certificate of Participation",
            "description": "Awarded for successful completion of the YBB 2025 program",
            "award_type": "other",
            "order_number": 1
        },
        "certificate_template": {
            "id": 2,
            "template_url": "https://www.w3.org/WAI/WCAG21/working-examples/pdf-table/table.pdf",  # Sample PDF for testing
            "template_type": "pdf",
            "issue_date": "2024-08-15",
            "published_at": "2024-08-15T12:00:00Z"
        },
        "content_blocks": [
            {
                "id": 1,
                "type": "text",
                "value": "CERTIFICATE OF ACHIEVEMENT",
                "x": 300,
                "y": 100,
                "font_size": 24,
                "font_family": "Arial",
                "font_weight": "bold",
                "text_align": "center",
                "color": "#1a365d"
            },
            {
                "id": 2,
                "type": "text",
                "value": "This is to certify that",
                "x": 300,
                "y": 180,
                "font_size": 16,
                "font_family": "Arial",
                "font_weight": "normal",
                "text_align": "center",
                "color": "#4a5568"
            },
            {
                "id": 3,
                "type": "placeholder",
                "value": "{{participant_name}}",
                "x": 300,
                "y": 220,
                "font_size": 28,
                "font_family": "Times New Roman",
                "font_weight": "bold",
                "text_align": "center",
                "color": "#2d3748"
            },
            {
                "id": 4,
                "type": "text",
                "value": "has successfully completed all requirements for the",
                "x": 300,
                "y": 280,
                "font_size": 14,
                "font_family": "Arial",
                "font_weight": "normal",
                "text_align": "center",
                "color": "#4a5568"
            },
            {
                "id": 5,
                "type": "placeholder",
                "value": "{{program_name}}",
                "x": 300,
                "y": 320,
                "font_size": 20,
                "font_family": "Times New Roman",
                "font_weight": "bold",
                "text_align": "center",
                "color": "#1a365d"
            },
            {
                "id": 6,
                "type": "placeholder",
                "value": "{{award_title}}",
                "x": 300,
                "y": 380,
                "font_size": 18,
                "font_family": "Arial",
                "font_weight": "normal",
                "text_align": "center",
                "color": "#e53e3e"
            },
            {
                "id": 7,
                "type": "text",
                "value": "Program Theme:",
                "x": 200,
                "y": 430,
                "font_size": 12,
                "font_family": "Arial",
                "font_weight": "normal",
                "text_align": "right",
                "color": "#718096"
            },
            {
                "id": 8,
                "type": "placeholder",
                "value": "{{program_theme}}",
                "x": 220,
                "y": 430,
                "font_size": 12,
                "font_family": "Arial",
                "font_weight": "bold",
                "text_align": "left",
                "color": "#2d3748"
            },
            {
                "id": 9,
                "type": "text",
                "value": "Issued on:",
                "x": 200,
                "y": 480,
                "font_size": 12,
                "font_family": "Arial",
                "font_weight": "normal",
                "text_align": "right",
                "color": "#718096"
            },
            {
                "id": 10,
                "type": "placeholder",
                "value": "{{date}}",
                "x": 220,
                "y": 480,
                "font_size": 12,
                "font_family": "Arial",
                "font_weight": "bold",
                "text_align": "left",
                "color": "#2d3748"
            }
        ],
        "assignment_info": {
            "assigned_by": 1,
            "assigned_at": "2024-08-15T10:00:00Z",
            "notes": "Completed all program requirements successfully"
        }
    }

def test_certificate_health():
    """Test certificate service health endpoint"""
    print("Testing certificate health endpoint...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        
        if response.status_code == 200:
            print("✅ Certificate health check passed")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"❌ Certificate health check failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Certificate health check failed with error: {e}")
        return False

def test_placeholders():
    """Test placeholders endpoint"""
    print("\nTesting placeholders endpoint...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/placeholders", timeout=10)
        
        if response.status_code == 200:
            print("✅ Placeholders endpoint works")
            data = response.json()
            if data.get('success'):
                placeholders = data.get('data', {})
                print(f"Available placeholder categories: {list(placeholders.keys())}")
                return True
            else:
                print(f"❌ Placeholders response indicates failure: {data}")
                return False
        else:
            print(f"❌ Placeholders endpoint failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Placeholders test failed with error: {e}")
        return False

def test_template_validation():
    """Test template validation endpoint"""
    print("\nTesting template validation...")
    
    test_template = {
        "template_url": "https://www.w3.org/WAI/WCAG21/working-examples/pdf-table/table.pdf",
        "template_type": "pdf"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/templates/validate",
            json=test_template,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Template validation passed")
            data = response.json()
            if data.get('success'):
                print(f"Template file size: {data['data'].get('file_size', 0)} bytes")
                return True
            else:
                print(f"❌ Template validation failed: {data}")
                return False
        else:
            print(f"❌ Template validation failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Template validation failed with error: {e}")
        return False

def test_content_blocks_validation():
    """Test content blocks validation"""
    print("\nTesting content blocks validation...")
    
    test_data = create_test_data()
    validation_data = {
        "content_blocks": test_data["content_blocks"],
        "template_dimensions": {"width": 595, "height": 842}
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/content-blocks/validate",
            json=validation_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Content blocks validation passed")
            data = response.json()
            if data.get('success'):
                validation_result = data.get('data', {})
                print(f"Valid blocks: {validation_result.get('valid_blocks', 0)}")
                print(f"Invalid blocks: {validation_result.get('invalid_blocks', 0)}")
                print(f"Warnings: {len(validation_result.get('warnings', []))}")
                return True
            else:
                print(f"❌ Content blocks validation failed: {data}")
                return False
        else:
            print(f"❌ Content blocks validation failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Content blocks validation failed with error: {e}")
        return False

def test_certificate_generation():
    """Test certificate generation"""
    print("\nTesting certificate generation...")
    
    test_data = create_test_data()
    
    try:
        print("Sending certificate generation request...")
        response = requests.post(
            f"{API_BASE_URL}/generate",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=60  # Longer timeout for generation
        )
        
        if response.status_code == 200:
            print("✅ Certificate generation succeeded")
            data = response.json()
            
            if data.get('success'):
                cert_data = data.get('data', {})
                print(f"Certificate ID: {cert_data.get('certificate_id')}")
                print(f"Filename: {cert_data.get('file_name')}")
                print(f"File size: {cert_data.get('file_size')} bytes")
                
                # Save the certificate file
                if save_certificate_file(cert_data):
                    print("✅ Certificate file saved successfully")
                    return True
                else:
                    print("❌ Failed to save certificate file")
                    return False
            else:
                print(f"❌ Certificate generation failed: {data}")
                return False
        else:
            print(f"❌ Certificate generation failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Certificate generation failed with error: {e}")
        return False

def save_certificate_file(cert_data):
    """Save the generated certificate file"""
    try:
        # Create output directory
        os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)
        
        # Get file data and decode
        file_data_b64 = cert_data.get('file_data')
        filename = cert_data.get('file_name', 'test_certificate.pdf')
        
        if not file_data_b64:
            print("No file data in response")
            return False
        
        # Decode base64 data
        file_data = base64.b64decode(file_data_b64)
        
        # Save to file
        output_path = os.path.join(TEST_OUTPUT_DIR, filename)
        with open(output_path, 'wb') as f:
            f.write(file_data)
        
        print(f"Certificate saved to: {output_path}")
        
        # Verify file was saved correctly
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"Saved file size: {file_size} bytes")
            
            # Basic PDF validation (check if it starts with PDF header)
            with open(output_path, 'rb') as f:
                header = f.read(4)
                if header == b'%PDF':
                    print("✅ File appears to be a valid PDF")
                    return True
                else:
                    print(f"❌ File does not appear to be a valid PDF (header: {header})")
                    return False
        else:
            print("❌ File was not saved properly")
            return False
            
    except Exception as e:
        print(f"❌ Failed to save certificate file: {e}")
        return False

def run_all_tests():
    """Run all certificate tests"""
    print("=== YBB Certificate Generation Service Tests ===\n")
    
    tests = [
        ("Certificate Health Check", test_certificate_health),
        ("Placeholders Endpoint", test_placeholders),
        ("Template Validation", test_template_validation),
        ("Content Blocks Validation", test_content_blocks_validation),
        ("Certificate Generation", test_certificate_generation)
    ]
    
    results = []
    
    for test_name, test_function in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        success = test_function()
        results.append((test_name, success))
        
        if success:
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Certificate generation is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get("http://127.0.0.1:5000/health", timeout=5)
        if response.status_code != 200:
            print("❌ YBB API server is not responding properly")
            print("Please start the Flask server first: python app.py")
            exit(1)
    except Exception:
        print("❌ Cannot connect to YBB API server at http://127.0.0.1:5000")
        print("Please start the Flask server first: python app.py")
        exit(1)
    
    # Run tests
    success = run_all_tests()
    
    if not success:
        exit(1)
