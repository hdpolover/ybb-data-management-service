"""
Simple Certificate Test
Basic test for certificate generation
"""
import requests
import json

def test_certificate_health():
    """Test certificate service health endpoint"""
    try:
        response = requests.get("http://127.0.0.1:5000/api/ybb/certificates/health", timeout=5)
        print(f"Health Status Code: {response.status_code}")
        print(f"Health Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health test failed: {e}")
        return False

def test_basic_server():
    """Test basic server health"""
    try:
        response = requests.get("http://127.0.0.1:5000/health", timeout=5)
        print(f"Basic Health Status: {response.status_code}")
        print(f"Basic Health Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Basic health test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Simple Certificate Test ===")
    
    # Test basic server
    print("\n1. Testing basic server health...")
    if test_basic_server():
        print("✅ Basic server is working")
    else:
        print("❌ Basic server is not working")
        exit(1)
    
    # Test certificate health
    print("\n2. Testing certificate service health...")
    if test_certificate_health():
        print("✅ Certificate service is working")
    else:
        print("❌ Certificate service is not working")
        exit(1)
    
    print("\n🎉 All basic tests passed!")
