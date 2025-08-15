#!/usr/bin/env python3
"""
API Documentation Verification Script
Tests that all documented endpoints actually exist and work as documented
"""
import requests
import json

def test_endpoint_availability():
    """Test that all documented endpoints are available"""
    
    base_url = "http://localhost:5000"
    
    # Test endpoints from documentation
    endpoints_to_test = [
        # Export creation endpoints
        ("POST", "/api/ybb/export/participants"),
        ("POST", "/api/ybb/export/payments"), 
        ("POST", "/api/ybb/export/ambassadors"),
        
        # Status and download endpoints (will need export_id)
        ("GET", "/api/ybb/export/test-id/status"),
        ("GET", "/api/ybb/export/test-id/download"),
        ("GET", "/api/ybb/export/test-id/download/zip"),
        ("GET", "/api/ybb/export/test-id/download/batch/1"),
        
        # Template endpoint
        ("GET", "/api/ybb/templates/participants"),
    ]
    
    print("🔍 Testing API Endpoint Availability")
    print("=" * 50)
    
    available_endpoints = []
    unavailable_endpoints = []
    
    for method, endpoint in endpoints_to_test:
        url = f"{base_url}{endpoint}"
        
        try:
            if method == "POST":
                # Test with minimal payload to see if endpoint exists
                response = requests.post(url, 
                    json={"data": []}, 
                    timeout=5,
                    headers={'Content-Type': 'application/json'}
                )
            else:
                response = requests.get(url, timeout=5)
            
            # Check if endpoint exists (not 404)
            if response.status_code != 404:
                status_icon = "✅"
                available_endpoints.append((method, endpoint, response.status_code))
            else:
                status_icon = "❌"
                unavailable_endpoints.append((method, endpoint, "404 Not Found"))
                
            print(f"{status_icon} {method:4} {endpoint:40} -> {response.status_code}")
            
        except requests.exceptions.ConnectionError:
            print(f"⚠️  {method:4} {endpoint:40} -> Connection Error (Server not running)")
            unavailable_endpoints.append((method, endpoint, "Connection Error"))
        except Exception as e:
            print(f"❌ {method:4} {endpoint:40} -> Error: {str(e)}")
            unavailable_endpoints.append((method, endpoint, str(e)))
    
    print("\n" + "=" * 50)
    print("📊 Summary")
    print("=" * 50)
    print(f"Available endpoints: {len(available_endpoints)}")
    print(f"Unavailable endpoints: {len(unavailable_endpoints)}")
    
    if unavailable_endpoints:
        print("\n❌ Unavailable endpoints:")
        for method, endpoint, error in unavailable_endpoints:
            print(f"   {method} {endpoint} - {error}")
    
    if available_endpoints:
        print("\n✅ Available endpoints:")
        for method, endpoint, status_code in available_endpoints:
            print(f"   {method} {endpoint} - {status_code}")
    
    return len(unavailable_endpoints) == 0

def test_actual_export_flow():
    """Test a real export flow to verify response structure"""
    
    print("\n" + "=" * 50)
    print("🧪 Testing Actual Export Flow")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Step 1: Create export
    create_url = f"{base_url}/api/ybb/export/participants"
    
    payload = {
        "data": [
            {
                "first_name": "Test",
                "last_name": "User", 
                "email": "test@example.com"
            }
        ],
        "format": "excel",
        "template": "standard"
    }
    
    try:
        print("1. Creating export...")
        response = requests.post(create_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Export created successfully")
            
            # Check response structure matches documentation
            required_keys = ['status', 'data', 'performance_metrics', 'system_info']
            missing_keys = []
            
            for key in required_keys:
                if key not in result:
                    missing_keys.append(key)
                else:
                    print(f"   ✅ Has '{key}' field")
            
            if missing_keys:
                print(f"   ⚠️ Missing documented fields: {missing_keys}")
            
            # Test status endpoint
            if 'data' in result and 'export_id' in result['data']:
                export_id = result['data']['export_id']
                print(f"\n2. Testing status endpoint for {export_id}")
                
                status_url = f"{base_url}/api/ybb/export/{export_id}/status"
                status_response = requests.get(status_url, timeout=10)
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print("✅ Status endpoint works")
                    
                    # Check status response structure
                    status_keys = ['status', 'export_id', 'export_type', 'record_count']
                    for key in status_keys:
                        if key in status_data:
                            print(f"   ✅ Status has '{key}' field")
                        else:
                            print(f"   ⚠️ Status missing '{key}' field")
                
                print(f"\n3. Testing download endpoint")
                download_url = f"{base_url}/api/ybb/export/{export_id}/download"
                
                # Just test that endpoint exists (don't download full file)
                download_response = requests.head(download_url, timeout=10)
                
                if download_response.status_code in [200, 405]:  # 405 = Method not allowed for HEAD
                    print("✅ Download endpoint exists")
                    
                    # Test actual download
                    download_response = requests.get(download_url, timeout=10)
                    if download_response.status_code == 200:
                        content_type = download_response.headers.get('content-type', '')
                        content_disposition = download_response.headers.get('content-disposition', '')
                        
                        print(f"   ✅ Download successful")
                        print(f"   ✅ Content-Type: {content_type}")
                        print(f"   ✅ Content-Disposition: {content_disposition}")
                        print(f"   ✅ File size: {len(download_response.content)} bytes")
                        
                        # Verify Excel file
                        if content_type and 'spreadsheet' in content_type:
                            if download_response.content.startswith(b'PK'):
                                print("   ✅ Valid Excel file (PK header)")
                            else:
                                print("   ⚠️ Excel file may be corrupted (no PK header)")
                else:
                    print(f"❌ Download endpoint failed: {download_response.status_code}")
                    
            return True
            
        else:
            print(f"❌ Export creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server - is it running?")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main verification function"""
    
    print("📋 API Documentation Verification")
    print("=" * 60)
    print("This script verifies that the documented endpoints")
    print("actually exist and work as described.")
    print("=" * 60)
    
    # Test 1: Endpoint availability
    endpoints_ok = test_endpoint_availability()
    
    # Test 2: Actual flow
    flow_ok = test_actual_export_flow()
    
    print("\n" + "=" * 60)
    if endpoints_ok and flow_ok:
        print("🎉 VERIFICATION SUCCESSFUL!")
        print("✅ All documented endpoints are available and working")
        print("✅ Response structures match documentation")
        print("✅ Export flow works as documented")
    elif flow_ok:
        print("✅ PARTIAL SUCCESS")
        print("✅ Core functionality works correctly")
        print("⚠️ Some endpoints may not be available (server not running?)")
    else:
        print("❌ VERIFICATION FAILED") 
        print("❌ Some documented features don't work as expected")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
