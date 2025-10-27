"""
Complete Certificate Generation Test
Tests all certificate endpoints with realistic data
"""
import requests
import json
import base64
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"
CERTIFICATE_BASE = f"{BASE_URL}/api/ybb/certificates"

# Test certificate data with sample template URL
SAMPLE_CERTIFICATE_DATA = {
    "participant": {
        "id": 12345,
        "account_id": "ACC123",
        "full_name": "John Michael Doe",
        "birthdate": "1995-03-15",
        "gender": "male",
        "nationality": "Indonesia",
        "nationality_code": "ID",
        "education_level": "bachelor",
        "major": "Computer Science",
        "institution": "University of Technology Jakarta",
        "occupation": "Student",
        "category": "fully_funded",
        "picture_url": "https://example.com/profile.jpg",
        "instagram_account": "@johndoe",
        "experiences": "3 years in software development",
        "achievements": "Winner of National Hackathon 2024",
        "tshirt_size": "L"
    },
    "program": {
        "id": 5,
        "name": "Youth Break the Boundaries 2025",
        "theme": "Innovation and Leadership for Sustainable Development",
        "start_date": "2025-08-01",
        "end_date": "2025-08-15"
    },
    "award": {
        "id": 1,
        "title": "Certificate of Outstanding Achievement",
        "description": "Awarded for exceptional performance and leadership",
        "award_type": "winner",
        "order_number": 1
    },
    "certificate_template": {
        "id": 2,
        "template_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        "template_type": "pdf",
        "issue_date": "2025-08-15"
    },
    "content_blocks": [
        {
            "id": 1,
            "type": "text",
            "value": "CERTIFICATE OF ACHIEVEMENT",
            "x": 297,
            "y": 100,
            "font_size": 28,
            "font_family": "Arial",
            "font_weight": "bold",
            "text_align": "center",
            "color": "#1a365d"
        },
        {
            "id": 2,
            "type": "text",
            "value": "This is to certify that",
            "x": 297,
            "y": 180,
            "font_size": 14,
            "font_family": "Arial",
            "font_weight": "normal",
            "text_align": "center",
            "color": "#2d3748"
        },
        {
            "id": 3,
            "type": "placeholder",
            "value": "{{participant_name}}",
            "x": 297,
            "y": 220,
            "font_size": 32,
            "font_family": "Times New Roman",
            "font_weight": "bold",
            "text_align": "center",
            "color": "#000000"
        },
        {
            "id": 4,
            "type": "text",
            "value": "has successfully completed",
            "x": 297,
            "y": 280,
            "font_size": 14,
            "font_family": "Arial",
            "font_weight": "normal",
            "text_align": "center",
            "color": "#2d3748"
        },
        {
            "id": 5,
            "type": "placeholder",
            "value": "{{program_name}}",
            "x": 297,
            "y": 320,
            "font_size": 20,
            "font_family": "Arial",
            "font_weight": "bold",
            "text_align": "center",
            "color": "#1a365d"
        },
        {
            "id": 6,
            "type": "placeholder",
            "value": "{{program_theme}}",
            "x": 297,
            "y": 360,
            "font_size": 12,
            "font_family": "Arial",
            "font_weight": "normal",
            "text_align": "center",
            "color": "#4a5568"
        },
        {
            "id": 7,
            "type": "text",
            "value": "and is hereby awarded",
            "x": 297,
            "y": 410,
            "font_size": 14,
            "font_family": "Arial",
            "font_weight": "normal",
            "text_align": "center",
            "color": "#2d3748"
        },
        {
            "id": 8,
            "type": "placeholder",
            "value": "{{award_title}}",
            "x": 297,
            "y": 450,
            "font_size": 22,
            "font_family": "Times New Roman",
            "font_weight": "bold",
            "text_align": "center",
            "color": "#1a365d"
        },
        {
            "id": 9,
            "type": "text",
            "value": "Date:",
            "x": 100,
            "y": 550,
            "font_size": 12,
            "font_family": "Arial",
            "font_weight": "normal",
            "text_align": "left",
            "color": "#2d3748"
        },
        {
            "id": 10,
            "type": "placeholder",
            "value": "{{date}}",
            "x": 150,
            "y": 550,
            "font_size": 12,
            "font_family": "Arial",
            "font_weight": "bold",
            "text_align": "left",
            "color": "#000000"
        }
    ],
    "assignment_info": {
        "assigned_by": 1,
        "assigned_at": datetime.now().isoformat(),
        "notes": "Generated via automated testing"
    }
}

def print_header(title):
    """Print formatted test header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_result(test_name, success, details=""):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"\n{status} | {test_name}")
    if details:
        print(f"    {details}")

def test_basic_health():
    """Test basic server health"""
    print_header("Test 1: Basic Server Health")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        success = response.status_code == 200
        print_result("Basic Health Check", success, 
                    f"Status: {response.status_code}")
        if success:
            data = response.json()
            print(f"    Service: {data.get('service')}")
            print(f"    Status: {data.get('status')}")
        return success
    except Exception as e:
        print_result("Basic Health Check", False, str(e))
        return False

def test_certificate_health():
    """Test certificate service health"""
    print_header("Test 2: Certificate Service Health")
    try:
        response = requests.get(f"{CERTIFICATE_BASE}/health", timeout=5)
        success = response.status_code == 200
        data = response.json()
        
        print_result("Certificate Health Check", success,
                    f"Status: {data.get('status')}")
        
        if success:
            print(f"    Service: {data.get('service')}")
            print(f"    Main Service: {'Available' if data.get('main_service_available') else 'Unavailable'}")
            print(f"    Fallback: {'Available' if data.get('fallback_service_available') else 'Unavailable'}")
            
            if data.get('dependencies'):
                print(f"    Dependencies:")
                for dep, available in data['dependencies'].items():
                    status = "✓" if available else "✗"
                    print(f"      {status} {dep}")
            
            if data.get('missing_dependencies'):
                print(f"    Missing: {', '.join(data['missing_dependencies'])}")
        
        return success
    except Exception as e:
        print_result("Certificate Health Check", False, str(e))
        return False

def test_get_placeholders():
    """Test getting available placeholders"""
    print_header("Test 3: Get Available Placeholders")
    try:
        response = requests.get(f"{CERTIFICATE_BASE}/placeholders", timeout=5)
        success = response.status_code == 200
        data = response.json()
        
        print_result("Get Placeholders", success,
                    f"Categories: {len(data.get('data', {}))}")
        
        if success and data.get('success'):
            placeholders = data['data']
            total = sum(len(v) for v in placeholders.values())
            print(f"    Total Placeholders: {total}")
            
            for category, items in placeholders.items():
                print(f"\n    {category.upper()}: {len(items)} placeholders")
                for item in items[:3]:  # Show first 3
                    print(f"      • {item['placeholder']} - {item['description']}")
                if len(items) > 3:
                    print(f"      ... and {len(items) - 3} more")
        
        return success
    except Exception as e:
        print_result("Get Placeholders", False, str(e))
        return False

def test_validate_template():
    """Test template validation"""
    print_header("Test 4: Template Validation")
    try:
        payload = {
            "template_url": SAMPLE_CERTIFICATE_DATA["certificate_template"]["template_url"],
            "template_type": "pdf"
        }
        
        response = requests.post(f"{CERTIFICATE_BASE}/templates/validate",
                                json=payload, timeout=10)
        success = response.status_code == 200
        data = response.json()
        
        print_result("Template Validation", success,
                    f"Template accessible: {data.get('success')}")
        
        if success and data.get('success'):
            template_data = data.get('data', {})
            print(f"    URL: {template_data.get('template_url')}")
            print(f"    Type: {template_data.get('template_type')}")
            print(f"    Size: {template_data.get('file_size', 0)} bytes")
        elif not data.get('success'):
            print(f"    Error: {data.get('error', {}).get('message')}")
        
        return success
    except Exception as e:
        print_result("Template Validation", False, str(e))
        return False

def test_validate_content_blocks():
    """Test content blocks validation"""
    print_header("Test 5: Content Blocks Validation")
    try:
        payload = {
            "content_blocks": SAMPLE_CERTIFICATE_DATA["content_blocks"],
            "template_dimensions": {"width": 595, "height": 842}
        }
        
        response = requests.post(f"{CERTIFICATE_BASE}/content-blocks/validate",
                                json=payload, timeout=10)
        success = response.status_code == 200
        data = response.json()
        
        print_result("Content Blocks Validation", success,
                    f"Valid: {data.get('success')}")
        
        if success:
            block_data = data.get('data', {})
            print(f"    Total Blocks: {block_data.get('total_blocks')}")
            print(f"    Valid: {block_data.get('valid_blocks')}")
            print(f"    Invalid: {block_data.get('invalid_blocks')}")
            print(f"    Warnings: {len(block_data.get('warnings', []))}")
            print(f"    Errors: {len(block_data.get('errors', []))}")
            
            if block_data.get('warnings'):
                print(f"\n    Warnings:")
                for warning in block_data['warnings'][:3]:
                    print(f"      ⚠ {warning}")
            
            if block_data.get('errors'):
                print(f"\n    Errors:")
                for error in block_data['errors'][:3]:
                    print(f"      ✗ {error}")
        
        return success
    except Exception as e:
        print_result("Content Blocks Validation", False, str(e))
        return False

def test_generate_certificate():
    """Test full certificate generation"""
    print_header("Test 6: Certificate Generation (Full Test)")
    try:
        print(f"\n📝 Generating certificate for: {SAMPLE_CERTIFICATE_DATA['participant']['full_name']}")
        print(f"   Program: {SAMPLE_CERTIFICATE_DATA['program']['name']}")
        print(f"   Award: {SAMPLE_CERTIFICATE_DATA['award']['title']}")
        
        response = requests.post(f"{CERTIFICATE_BASE}/generate",
                                json=SAMPLE_CERTIFICATE_DATA,
                                timeout=30)
        
        success = response.status_code == 200
        data = response.json()
        
        print_result("Certificate Generation", success,
                    f"Generated: {data.get('success')}")
        
        if success and data.get('success'):
            cert_data = data.get('data', {})
            print(f"\n    Certificate Details:")
            print(f"    • ID: {cert_data.get('certificate_id')}")
            print(f"    • Participant: {cert_data.get('participant_id')}")
            print(f"    • Award: {cert_data.get('award_id')}")
            print(f"    • Filename: {cert_data.get('file_name')}")
            print(f"    • Size: {cert_data.get('file_size')} bytes")
            print(f"    • MIME: {cert_data.get('mime_type')}")
            print(f"    • Generated: {cert_data.get('generated_at')}")
            
            template_info = cert_data.get('template_used', {})
            print(f"\n    Template Used:")
            print(f"    • ID: {template_info.get('id')}")
            print(f"    • Type: {template_info.get('type')}")
            print(f"    • Version: {template_info.get('version')}")
            
            # Check if it's fallback
            if cert_data.get('is_fallback'):
                print(f"\n    ⚠️  Using fallback text-based certificate")
            
            # Save certificate to file
            if cert_data.get('file_data'):
                output_filename = f"test_certificate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                pdf_bytes = base64.b64decode(cert_data['file_data'])
                
                with open(output_filename, 'wb') as f:
                    f.write(pdf_bytes)
                
                print(f"\n    💾 Certificate saved to: {output_filename}")
                print(f"    📄 File size: {len(pdf_bytes)} bytes")
        else:
            error = data.get('error', {})
            print(f"\n    Error Code: {error.get('code')}")
            print(f"    Error Message: {error.get('message')}")
            if error.get('details'):
                print(f"    Details: {json.dumps(error['details'], indent=6)}")
        
        return success
    except Exception as e:
        print_result("Certificate Generation", False, str(e))
        return False

def run_all_tests():
    """Run all certificate tests"""
    print("\n" + "🧪 "*35)
    print("  CERTIFICATE GENERATION - COMPREHENSIVE TEST SUITE")
    print("🧪 "*35)
    
    results = {
        "Basic Health": test_basic_health(),
        "Certificate Health": test_certificate_health(),
        "Get Placeholders": test_get_placeholders(),
        "Template Validation": test_validate_template(),
        "Content Blocks Validation": test_validate_content_blocks(),
        "Certificate Generation": test_generate_certificate()
    }
    
    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} | {test_name}")
    
    print("\n" + "-"*70)
    print(f"  Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    print("="*70 + "\n")
    
    if passed == total:
        print("🎉 All tests passed! Certificate generation is fully operational.")
    elif passed >= total * 0.5:
        print("⚠️  Some tests failed. Check logs above for details.")
    else:
        print("❌ Multiple tests failed. Service may not be running or has issues.")
    
    return passed == total

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {e}")
