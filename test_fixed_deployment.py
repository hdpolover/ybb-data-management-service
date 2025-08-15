#!/usr/bin/env python3
"""
Test the fixed deployment configuration
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.abspath('.'))

def test_wsgi_import():
    """Test importing wsgi.py with production config"""
    print("Testing WSGI import with production configuration...")
    
    try:
        # Set production environment
        os.environ['FLASK_ENV'] = 'production'
        os.environ['PORT'] = '5000'
        
        # Import wsgi
        import wsgi
        app = wsgi.application
        
        print(f"SUCCESS: WSGI import successful")
        print(f"App type: {type(app)}")
        
        # Test with test client
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            print(f"Health check: {response.status_code}")
            
            # Test export endpoint with valid data
            test_data = {
                "data": [
                    {
                        "id": 1,
                        "full_name": "Test User",
                        "email": "test@example.com",
                        "nationality": "USA"
                    }
                ],
                "template": "standard",
                "format": "excel"
            }
            
            response = client.post('/api/ybb/export/participants', 
                                 json=test_data,
                                 headers={'Content-Type': 'application/json'})
            print(f"Export test: {response.status_code}")
            
            if response.status_code == 200:
                result = response.get_json()
                print(f"Export success: {result.get('status')}")
                print(f"Export ID: {result.get('data', {}).get('export_id', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: WSGI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=== Testing Fixed Railway Deployment ===\n")
    
    success = test_wsgi_import()
    
    print(f"\n=== Result ===")
    if success:
        print("SUCCESS: Fixed deployment configuration works!")
        print("\nNext steps:")
        print("1. Deploy the updated railway.toml and wsgi.py to Railway")
        print("2. The 500 error should be resolved")
        print("3. Test the production endpoint again")
    else:
        print("ERROR: Issues still exist that need to be resolved")
    
    return success

if __name__ == "__main__":
    main()
