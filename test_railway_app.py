#!/usr/bin/env python3
"""
Test Railway app_complete.py initialization
"""
import sys
import os
import traceback

# Add current directory to path
sys.path.insert(0, os.path.abspath('.'))

def test_app_complete_import():
    """Test importing app_complete.py"""
    print("Testing app_complete.py import...")
    
    try:
        # Set production environment like Railway
        os.environ['FLASK_ENV'] = 'production'
        os.environ['PORT'] = '5000'
        
        # Try importing the complete app
        import app_complete
        print("✅ app_complete.py imported successfully")
        
        # Test the Flask app
        app = app_complete.app
        print(f"✅ Flask app created: {type(app)}")
        
        # Test with client
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            print(f"✅ Health endpoint: {response.status_code} - {response.get_json()}")
            
            # Test export endpoint (should return 400 for missing data)
            response = client.post('/api/ybb/export/participants', 
                                 json={"test": "data"},
                                 headers={'Content-Type': 'application/json'})
            print(f"✅ Export endpoint: {response.status_code} - {response.get_json()}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ General error: {e}")
        traceback.print_exc()
        return False

def test_certificate_service_import():
    """Test certificate service import specifically"""
    print("\nTesting certificate service import...")
    
    try:
        from services.certificate_service import CertificateService
        service = CertificateService()
        print("✅ Certificate service imported and initialized successfully")
        return True
    except ImportError as e:
        print(f"❌ Certificate service import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Certificate service initialization error: {e}")
        return False

def main():
    """Main test function"""
    print("=== Testing Railway app_complete.py ===\n")
    
    # Test certificate service first (this is likely the issue)
    cert_success = test_certificate_service_import()
    
    # Test complete app import
    app_success = test_app_complete_import()
    
    print(f"\n=== Results ===")
    print(f"Certificate service: {'✅' if cert_success else '❌'}")
    print(f"Complete app: {'✅' if app_success else '❌'}")
    
    if not app_success:
        print("\nRECOMMENDED SOLUTION:")
        print("Update railway.toml to use app.py instead of app_complete.py:")
        print('startCommand = ". /opt/venv/bin/activate && python app.py"')
    
    return app_success

if __name__ == "__main__":
    main()
