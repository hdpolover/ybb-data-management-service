"""
Test fallback certificate service
"""
from services.fallback_certificate_service import FallbackCertificateService
import json

def test_fallback_service():
    service = FallbackCertificateService()
    
    test_data = {
        "participant": {
            "id": 123,
            "full_name": "John Doe"
        },
        "program": {
            "id": 1,
            "name": "Youth Break the Boundaries 2025"
        },
        "award": {
            "id": 1,
            "title": "Certificate of Participation"
        },
        "certificate_template": {
            "id": 1,
            "issue_date": "2025-08-11"
        }
    }
    
    result = service.generate_certificate(test_data)
    
    if result['success']:
        print("✅ Fallback service works!")
        print(f"Certificate ID: {result['data']['certificate_id']}")
        print(f"Filename: {result['data']['file_name']}")
        print(f"File size: {result['data']['file_size']} bytes")
        print(f"Is fallback: {result['data']['is_fallback']}")
        
        # Decode and show first few lines
        import base64
        content = base64.b64decode(result['data']['file_data']).decode('utf-8')
        lines = content.split('\n')[:10]
        print("\nCertificate content preview:")
        for line in lines:
            print(line)
    else:
        print("❌ Fallback service failed:")
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_fallback_service()
