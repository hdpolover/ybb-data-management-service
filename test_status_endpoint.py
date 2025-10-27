#!/usr/bin/env python3
"""
Quick test script for the YBB export status endpoint
"""

import requests
import json
import time

def test_status_endpoint():
    base_url = "http://127.0.0.1:5000/api/ybb"
    
    print("🧪 Testing YBB Export Status Endpoint")
    print("=" * 50)
    
    # First, test with an invalid export ID
    print("\n1. Testing invalid export ID...")
    try:
        response = requests.get(f"{base_url}/export/invalid-id/status", timeout=5)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 404:
            print("   ✅ Correctly returns 404 for invalid export ID")
        try:
            result = response.json()
            print(f"   Response: {json.dumps(result, indent=2)}")
        except:
            print(f"   Response (text): {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
        return False
    
    # Create a new export to test with
    print("\n2. Creating a new export...")
    export_data = {
        "export_type": "participants",
        "template": "basic",
        "filters": {"limit": 5}  # Small limit for quick testing
    }
    
    try:
        response = requests.post(f"{base_url}/export", 
                               json=export_data,
                               headers={'Content-Type': 'application/json'},
                               timeout=10)
        print(f"   Export Creation Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            export_id = result.get('data', {}).get('export_id')
            print(f"   ✅ Export created with ID: {export_id}")
            
            # Test the status endpoint
            print("\n3. Testing status endpoint with valid export ID...")
            time.sleep(1)  # Brief wait
            
            status_response = requests.get(f"{base_url}/export/{export_id}/status", timeout=5)
            print(f"   Status Check Code: {status_response.status_code}")
            
            if status_response.status_code == 200:
                status_result = status_response.json()
                print(f"   ✅ Status endpoint working!")
                print(f"   Export Status: {status_result.get('status', 'unknown')}")
                if 'record_count' in status_result:
                    print(f"   Record Count: {status_result['record_count']}")
                if 'export_type' in status_result:
                    print(f"   Export Type: {status_result['export_type']}")
                print(f"   Full Response: {json.dumps(status_result, indent=2)}")
                return True
            else:
                print(f"   ❌ Status check failed with code {status_response.status_code}")
                try:
                    error_result = status_response.json()
                    print(f"   Error: {json.dumps(error_result, indent=2)}")
                except:
                    print(f"   Error Response (text): {status_response.text}")
                return False
        else:
            print(f"   ❌ Export creation failed with code {response.status_code}")
            try:
                error_result = response.json()
                print(f"   Error: {json.dumps(error_result, indent=2)}")
            except:
                print(f"   Error Response (text): {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error during export: {e}")
        return False

if __name__ == "__main__":
    success = test_status_endpoint()
    if success:
        print("\n🎉 Status endpoint test completed successfully!")
    else:
        print("\n❌ Status endpoint test failed!")
        print("\nMake sure the Flask app is running with:")
        print("python app.py")