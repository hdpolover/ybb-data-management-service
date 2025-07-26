import requests
import json

# Test the API with sample data
def test_api():
    base_url = "http://localhost:5000"
    
    print("🧪 Testing YBB API with comprehensive logging...")
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    response = requests.get(f"{base_url}/health")
    print(f"Response: {response.status_code}")
    print(f"Data: {response.json()}")
    
    # Test 2: Small participants export
    print("\n2. Testing participants export (small dataset)...")
    participants_data = {
        "data": [
            {
                "id": 1,
                "form_id": "YBB2024_001",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone": "+1234567890",
                "birthdate": "1995-05-15",
                "nationality": "American",
                "state": "California",
                "form_status": 1,
                "is_active": 1
            },
            {
                "id": 2,
                "form_id": "YBB2024_002",
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane.smith@example.com",
                "phone": "+1234567891",
                "birthdate": "1996-08-22",
                "nationality": "Canadian",
                "state": "Ontario",
                "form_status": 2,
                "is_active": 1
            },
            {
                "id": 3,
                "form_id": "YBB2024_003",
                "first_name": "Maria",
                "last_name": "Garcia",
                "email": "maria.garcia@example.com",
                "phone": "+1234567892",
                "birthdate": "1994-12-10",
                "nationality": "Mexican",
                "state": "Mexico City",
                "form_status": 3,
                "is_active": 1
            }
        ],
        "template": "standard",
        "format": "excel",
        "filename": "test_participants.xlsx"
    }
    
    response = requests.post(f"{base_url}/api/ybb/export/participants", json=participants_data)
    print(f"Response: {response.status_code}")
    result = response.json()
    print(f"Export result: {json.dumps(result, indent=2)}")
    
    # Test 3: Check export status
    if result.get("status") == "success" and "data" in result:
        export_id = result["data"]["export_id"]
        print(f"\n3. Checking export status for ID: {export_id}...")
        
        status_response = requests.get(f"{base_url}/api/ybb/export/{export_id}/status")
        print(f"Status response: {status_response.status_code}")
        print(f"Status data: {json.dumps(status_response.json(), indent=2)}")
    
    # Test 4: Test error case (no data)
    print("\n4. Testing error case (no data provided)...")
    error_response = requests.post(f"{base_url}/api/ybb/export/participants", json={})
    print(f"Error response: {error_response.status_code}")
    print(f"Error data: {json.dumps(error_response.json(), indent=2)}")
    
    # Test 5: Test templates endpoint
    print("\n5. Testing templates endpoint...")
    templates_response = requests.get(f"{base_url}/api/ybb/templates")
    print(f"Templates response: {templates_response.status_code}")
    templates_data = templates_response.json()
    print(f"Available templates: {list(templates_data.get('data', {}).keys())}")
    
    # Test 6: Test log viewer endpoints
    print("\n6. Testing log viewer endpoints...")
    logs_response = requests.get(f"{base_url}/api/logs/recent?lines=10")
    print(f"Logs response: {logs_response.status_code}")
    logs_data = logs_response.json()
    print(f"Recent logs count: {len(logs_data.get('data', {}).get('logs', []))}")
    
    print("\n✅ API testing completed! Check the logs for detailed tracking.")

if __name__ == "__main__":
    test_api()
