"""
Test the YBB Data Management API endpoints
"""
import requests
import json
import os

# API base URL
BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_excel_export():
    """Test Excel export endpoint"""
    print("\nTesting Excel export...")
    try:
        test_data = [
            {"name": "John Doe", "age": 30, "city": "New York", "salary": 50000},
            {"name": "Jane Smith", "age": 25, "city": "Los Angeles", "salary": 60000},
            {"name": "Bob Johnson", "age": 35, "city": "Chicago", "salary": 55000}
        ]
        
        payload = {
            "data": test_data,
            "filename": "test_export.xlsx",
            "sheet_name": "Employee Data",
            "format_options": {
                "auto_width": True,
                "header_style": {
                    "bold": True,
                    "font_color": "FFFFFF",
                    "bg_color": "366092"
                }
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/export/excel",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            # Save the Excel file
            with open("test_export.xlsx", "wb") as f:
                f.write(response.content)
            print("Excel export successful! File saved as test_export.xlsx")
            return True
        else:
            print(f"Excel export failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Excel export test failed: {e}")
        return False

def test_data_processing():
    """Test data processing endpoint"""
    print("\nTesting data processing...")
    try:
        test_data = [
            {"name": "John", "department": "IT", "salary": 50000, "status": "active"},
            {"name": "Jane", "department": "HR", "salary": 60000, "status": "active"},
            {"name": "Bob", "department": "IT", "salary": 55000, "status": "inactive"},
            {"name": "Alice", "department": "Finance", "salary": 65000, "status": "active"}
        ]
        
        payload = {
            "data": test_data,
            "operations": [
                {"type": "filter", "column": "status", "value": "active"},
                {"type": "sort", "column": "salary", "order": "desc"}
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/data/process",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Data processing successful!")
            print(f"Rows returned: {result['row_count']}")
            print(f"Processed data: {json.dumps(result['data'], indent=2)}")
            return True
        else:
            print(f"Data processing failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Data processing test failed: {e}")
        return False

def test_query_endpoint():
    """Test database query endpoint (will fail if DB not configured)"""
    print("\nTesting database query...")
    try:
        payload = {
            "query": "SELECT 1 as test_value, 'Hello World' as message",
            "format": "json"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/query",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Query successful!")
            print(f"Result: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"Query failed: {response.status_code} - {response.text}")
            print("(This is expected if database is not configured)")
            return False
            
    except Exception as e:
        print(f"Query test failed: {e}")
        return False

if __name__ == "__main__":
    print("YBB Data Management API Test Suite")
    print("=" * 40)
    
    # Run tests
    tests = [
        ("Health Check", test_health_check),
        ("Excel Export", test_excel_export),
        ("Data Processing", test_data_processing),
        ("Database Query", test_query_endpoint)
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 40)
    print("Test Results Summary:")
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
