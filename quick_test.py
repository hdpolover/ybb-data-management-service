"""
Simple test script for data processing service
"""
import requests
import json
import os

BASE_URL = "http://localhost:5000"

def main():
    print("🔧 YBB Data Processing Service - Quick Test")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing service health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Service is running: {data['service']}")
        else:
            print(f"   ❌ Service health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Cannot connect to service: {e}")
        return
    
    # Test 2: Simple Excel export
    print("\n2. Testing Excel export...")
    test_data = [
        {"name": "John", "age": 30, "city": "New York"},
        {"name": "Jane", "age": 25, "city": "Los Angeles"},
        {"name": "Bob", "age": 35, "city": "Chicago"}
    ]
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/export/excel",
            json={"data": test_data, "filename": "test_simple.xlsx"},
            timeout=30
        )
        
        if response.status_code == 200:
            with open("test_simple.xlsx", "wb") as f:
                f.write(response.content)
            print("   ✅ Excel export successful - saved as test_simple.xlsx")
        else:
            print(f"   ❌ Excel export failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Excel export error: {e}")
    
    # Test 3: Data validation
    print("\n3. Testing data validation...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/data/validate",
            json={"data": test_data},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Data validation successful:")
            print(f"      Rows: {result['row_count']}, Columns: {result['column_count']}")
            print(f"      Columns: {', '.join(result['columns'])}")
        else:
            print(f"   ❌ Data validation failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Data validation error: {e}")
    
    # Test 4: Data processing
    print("\n4. Testing data processing...")
    try:
        operations = [
            {"type": "sort", "column": "age", "order": "desc"}
        ]
        
        response = requests.post(
            f"{BASE_URL}/api/data/process",
            json={"data": test_data, "operations": operations},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Data processing successful:")
            print(f"      Processed {result['row_count']} rows")
            print(f"      Sorted data: {result['data'][0]['name']} (age {result['data'][0]['age']})")
        else:
            print(f"   ❌ Data processing failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Data processing error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Service is ready for integration!")
    print("\nNext steps:")
    print("1. Use the PHP integration class in examples/simple_php_integration.php")
    print("2. Send JSON data from your PHP app to this service")
    print("3. Receive Excel files or processed data back")

if __name__ == "__main__":
    main()
