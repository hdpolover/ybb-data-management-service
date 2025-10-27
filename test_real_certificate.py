"""
Test Certificate Generation with Real Template
Uses the actual YBB certificate template with name and certificate number only
"""
import requests
import json
import base64
from datetime import datetime
import os

BASE_URL = "http://127.0.0.1:5000"
CERTIFICATE_BASE = f"{BASE_URL}/api/ybb/certificates"

# Path to the real certificate template
TEMPLATE_PATH = "/Users/mit06/Desktop/personal-projects/ybb-data-management-service/KYS Certif Delegates all Kosongan .pdf"

def upload_template_to_test_server():
    """
    In production, you would upload this to cloud storage (S3, etc.)
    For testing, we'll use GitHub's raw content URL or a temporary hosting service
    """
    # Read the template file
    with open(TEMPLATE_PATH, 'rb') as f:
        template_data = f.read()
    
    # Save to static folder that Flask can serve
    static_dir = "static/templates"
    os.makedirs(static_dir, exist_ok=True)
    
    template_filename = "kys_certificate_template.pdf"
    test_template_path = os.path.join(static_dir, template_filename)
    
    with open(test_template_path, 'wb') as f:
        f.write(template_data)
    
    # Return a URL that the Flask app can access
    # For local testing, we'll use localhost
    return f"{BASE_URL}/static/templates/{template_filename}"

def generate_certificate_with_template(participant_name, cert_number):
    """
    Generate certificate with just name and certificate number
    """
    print(f"\n{'='*70}")
    print(f"  Generating Certificate")
    print(f"{'='*70}")
    print(f"Participant: {participant_name}")
    print(f"Certificate Number: {cert_number}")
    
    # Prepare certificate data with minimal fields
    # Note: We still need to provide the full structure for API compatibility
    certificate_data = {
        "participant": {
            "id": 1,
            "full_name": participant_name,
            "birthdate": "1995-01-01",
            "gender": "male",
            "nationality": "Indonesia",
            "nationality_code": "ID",
            "education_level": "bachelor",
            "major": "Business",
            "institution": "University",
            "occupation": "Student",
            "category": "fully_funded"
        },
        "program": {
            "id": 1,
            "name": "Youth Break the Boundaries 2025",
            "theme": "Leadership Development",
            "start_date": "2025-08-01",
            "end_date": "2025-08-15"
        },
        "award": {
            "id": 1,
            "title": "Certificate of Participation",
            "description": "Successfully completed the program",
            "award_type": "other",
            "order_number": 1
        },
        "certificate_template": {
            "id": 1,
            "template_url": upload_template_to_test_server(),
            "template_type": "pdf",
            "issue_date": datetime.now().strftime("%Y-%m-%d")
        },
        # ONLY 2 content blocks: Name and Certificate Number
        "content_blocks": [
            {
                "id": 1,
                "type": "placeholder",
                "value": "{{participant_name}}",
                "x": 421,  # Center X
                "y": 268,  # Name position (adjusted for landscape)
                "font_size": 24,
                "font_family": "Times New Roman",
                "font_weight": "bold",
                "text_align": "center",
                "color": "#000000"
            },
            {
                "id": 2,
                "type": "text",
                "value": cert_number,
                "x": 100,  # Left-aligned for certificate number
                "y": 89,   # Bottom position
                "font_size": 12,
                "font_family": "Arial",
                "font_weight": "normal",
                "text_align": "left",
                "color": "#000000"
            }
        ],
        "assignment_info": {
            "assigned_by": 1,
            "assigned_at": datetime.now().isoformat(),
            "notes": "Generated with real template"
        }
    }
    
    try:
        print(f"\n📤 Sending request to API...")
        response = requests.post(
            f"{CERTIFICATE_BASE}/generate",
            json=certificate_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                cert_data = result['data']
                print(f"\n✅ Certificate Generated Successfully!")
                print(f"   • Certificate ID: {cert_data.get('certificate_id')}")
                print(f"   • File Size: {cert_data.get('file_size')} bytes")
                print(f"   • Generated At: {cert_data.get('generated_at')}")
                
                # Save the certificate
                if cert_data.get('file_data'):
                    safe_name = participant_name.replace(' ', '_')
                    safe_cert_num = cert_number.replace('/', '-').replace(' ', '_')
                    output_filename = f"certificate_{safe_name}_{safe_cert_num}.pdf"
                    pdf_bytes = base64.b64decode(cert_data['file_data'])
                    
                    with open(output_filename, 'wb') as f:
                        f.write(pdf_bytes)
                    
                    print(f"\n💾 Certificate saved to: {output_filename}")
                    return output_filename
            else:
                error = result.get('error', {})
                print(f"\n❌ Generation Failed:")
                print(f"   • Code: {error.get('code')}")
                print(f"   • Message: {error.get('message')}")
                if error.get('details'):
                    print(f"   • Details: {json.dumps(error['details'], indent=6)}")
        else:
            print(f"\n❌ API Error: Status {response.status_code}")
            try:
                print(f"   Response: {response.json()}")
            except:
                print(f"   Response: {response.text}")
        
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()
    
    return None

def test_batch_generation():
    """
    Generate multiple certificates with the real template
    """
    print("\n" + "🎓 "*30)
    print("  REAL CERTIFICATE GENERATION TEST")
    print("🎓 "*30)
    
    # Test cases with different names and certificate numbers
    test_cases = [
        ("John Michael Anderson", "KYS/2025/001"),
        ("Sarah Elizabeth Thompson", "KYS/2025/002"),
        ("Ahmad Faisal Ibrahim", "KYS/2025/003"),
        ("Maria Sofia Rodriguez", "KYS/2025/004"),
        ("David Chen Wei", "KYS/2025/005"),
    ]
    
    generated_files = []
    
    for name, cert_num in test_cases:
        result = generate_certificate_with_template(name, cert_num)
        if result:
            generated_files.append(result)
    
    # Summary
    print(f"\n{'='*70}")
    print(f"  GENERATION SUMMARY")
    print(f"{'='*70}")
    print(f"Total Certificates Generated: {len(generated_files)}")
    print(f"\nGenerated Files:")
    for idx, filename in enumerate(generated_files, 1):
        file_size = os.path.getsize(filename) if os.path.exists(filename) else 0
        print(f"  {idx}. {filename} ({file_size:,} bytes)")
    
    if len(generated_files) == len(test_cases):
        print(f"\n🎉 All {len(test_cases)} certificates generated successfully!")
    else:
        print(f"\n⚠️  Only {len(generated_files)}/{len(test_cases)} certificates generated")

def test_single_certificate():
    """
    Generate a single certificate for quick testing
    """
    print("\n" + "🎓 "*30)
    print("  SINGLE CERTIFICATE GENERATION TEST")
    print("🎓 "*30)
    
    name = "Test Participant Name"
    cert_number = "KYS/2025/TEST"
    
    result = generate_certificate_with_template(name, cert_number)
    
    if result:
        print(f"\n✅ Test completed successfully!")
        print(f"   Open the file to verify: {result}")
    else:
        print(f"\n❌ Test failed!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "batch":
        # Generate multiple certificates
        test_batch_generation()
    else:
        # Generate single certificate (default)
        test_single_certificate()
    
    print("\n" + "="*70 + "\n")
