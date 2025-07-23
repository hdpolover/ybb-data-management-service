"""
Test the enhanced API with chunked processing for large datasets
"""
import requests
import json
import time
import uuid

BASE_URL = "http://localhost:5000"

def test_chunked_excel_export():
    """Test chunked Excel export with large dataset"""
    print("Testing chunked Excel export...")
    
    # Generate test data (simulating large dataset)
    test_data = []
    for i in range(5000):  # 5000 records
        test_data.append({
            "id": i,
            "name": f"User {i}",
            "email": f"user{i}@example.com",
            "department": ["IT", "HR", "Finance", "Marketing"][i % 4],
            "salary": 30000 + (i % 50000),
            "status": "active" if i % 2 == 0 else "inactive"
        })
    
    chunk_size = 1000
    chunks = [test_data[i:i + chunk_size] for i in range(0, len(test_data), chunk_size)]
    total_chunks = len(chunks)
    session_id = str(uuid.uuid4())
    
    print(f"Processing {len(test_data)} records in {total_chunks} chunks...")
    
    for index, chunk in enumerate(chunks):
        is_last_chunk = (index == total_chunks - 1)
        
        payload = {
            "session_id": session_id,
            "chunk_data": chunk,
            "chunk_index": index,
            "total_chunks": total_chunks,
            "filename": "chunked_test_export.xlsx",
            "sheet_name": "Large Dataset",
            "format_options": {
                "auto_width": True,
                "header_style": {
                    "bold": True,
                    "font_color": "FFFFFF",
                    "bg_color": "366092"
                }
            }
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/export/excel/chunked",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=300
            )
            
            if response.status_code == 200:
                if is_last_chunk:
                    # Save the Excel file
                    with open("chunked_test_export.xlsx", "wb") as f:
                        f.write(response.content)
                    print(f"✅ Chunked Excel export completed! File saved as chunked_test_export.xlsx")
                    return True
                else:
                    result = response.json()
                    print(f"✅ Chunk {index + 1}/{total_chunks} processed")
            else:
                print(f"❌ Chunk {index + 1} failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Chunk {index + 1} error: {e}")
            return False
    
    return False

def test_chunked_data_processing():
    """Test chunked data processing"""
    print("\nTesting chunked data processing...")
    
    # Generate test data
    test_data = []
    for i in range(3000):  # 3000 records
        test_data.append({
            "id": i,
            "name": f"Employee {i}",
            "department": ["IT", "HR", "Finance", "Marketing"][i % 4],
            "salary": 30000 + (i % 50000),
            "status": "active" if i % 3 != 0 else "inactive",
            "hire_date": f"2020-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}"
        })
    
    chunk_size = 500
    chunks = [test_data[i:i + chunk_size] for i in range(0, len(test_data), chunk_size)]
    total_chunks = len(chunks)
    session_id = str(uuid.uuid4())
    
    operations = [
        {"type": "filter", "column": "status", "value": "active"},
        {"type": "sort", "column": "salary", "order": "desc", "global": True}
    ]
    
    print(f"Processing {len(test_data)} records in {total_chunks} chunks with filtering...")
    
    for index, chunk in enumerate(chunks):
        is_last_chunk = (index == total_chunks - 1)
        
        payload = {
            "session_id": session_id,
            "chunk_data": chunk,
            "chunk_index": index,
            "total_chunks": total_chunks,
            "operations": operations
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/data/process/chunked",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=300
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if is_last_chunk:
                    print(f"✅ Chunked processing completed!")
                    print(f"   Original records: {len(test_data)}")
                    print(f"   Filtered records: {result['row_count']}")
                    print(f"   Top 5 results:")
                    for i, record in enumerate(result['data'][:5]):
                        print(f"     {i+1}. {record['name']} - ${record['salary']} ({record['department']})")
                    return True
                else:
                    print(f"✅ Chunk {index + 1}/{total_chunks} processed - {result['chunk_row_count']} rows")
            else:
                print(f"❌ Chunk {index + 1} failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Chunk {index + 1} error: {e}")
            return False
    
    return False

def test_performance_comparison():
    """Compare regular vs chunked processing performance"""
    print("\nTesting performance comparison...")
    
    # Small dataset for regular processing
    small_data = []
    for i in range(1000):
        small_data.append({
            "id": i,
            "name": f"User {i}",
            "value": i * 10
        })
    
    # Test regular processing
    start_time = time.time()
    try:
        response = requests.post(
            f"{BASE_URL}/api/export/excel",
            json={
                "data": small_data,
                "filename": "regular_test.xlsx"
            },
            timeout=60
        )
        regular_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ Regular export (1,000 records): {regular_time:.2f} seconds")
        else:
            print(f"❌ Regular export failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Regular export error: {e}")
    
    # Test chunked processing with same data
    start_time = time.time()
    session_id = str(uuid.uuid4())
    
    payload = {
        "session_id": session_id,
        "chunk_data": small_data,
        "chunk_index": 0,
        "total_chunks": 1,
        "filename": "chunked_small_test.xlsx"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/export/excel/chunked",
            json=payload,
            timeout=60
        )
        chunked_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ Chunked export (1,000 records): {chunked_time:.2f} seconds")
            print(f"   Overhead: {chunked_time - regular_time:.2f} seconds")
        else:
            print(f"❌ Chunked export failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Chunked export error: {e}")

if __name__ == "__main__":
    print("Enhanced YBB Data Management API Test Suite")
    print("Testing Large Dataset Processing")
    print("=" * 50)
    
    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ API is not running. Please start the Flask server first.")
            exit(1)
        print("✅ API is running")
    except:
        print("❌ Cannot connect to API. Please start the Flask server first.")
        exit(1)
    
    # Run tests
    tests = [
        ("Chunked Excel Export", test_chunked_excel_export),
        ("Chunked Data Processing", test_chunked_data_processing),
        ("Performance Comparison", test_performance_comparison)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'-' * 20}")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The API is ready for large dataset processing.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the output above for details.")
