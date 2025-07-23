#!/usr/bin/env python3
"""
YBB Export API Test Suite
Comprehensive testing for YBB export functionality
"""
import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"

# Sample test data
SAMPLE_PARTICIPANTS = [
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
        "is_active": 1,
        "created_at": "2024-01-15 10:30:00",
        "updated_at": "2024-01-15 10:30:00"
    },
    {
        "id": 2,
        "form_id": "YBB2024_002",
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com",
        "phone": "+1234567891",
        "birthdate": "1993-08-22",
        "nationality": "Canadian",
        "state": "Ontario",
        "form_status": 2,
        "is_active": 1,
        "created_at": "2024-01-16 14:20:00",
        "updated_at": "2024-01-16 14:20:00"
    },
    {
        "id": 3,
        "form_id": "YBB2024_003",
        "first_name": "Carlos",
        "last_name": "Rodriguez",
        "email": "carlos.rodriguez@example.com",
        "phone": "+1234567892",
        "birthdate": "1997-12-03",
        "nationality": "Mexican",
        "state": "Jalisco",
        "form_status": 3,
        "is_active": 1,
        "created_at": "2024-01-17 09:15:00",
        "updated_at": "2024-01-17 09:15:00"
    }
]

SAMPLE_PAYMENTS = [
    {
        "id": 1,
        "participant_id": 1,
        "payment_method_id": 1,
        "amount": 1500.00,
        "usd_amount": 1500.00,
        "payment_date": "2024-01-20",
        "payment_status": 1,
        "reference_number": "PAY_001_2024",
        "notes": "Registration fee payment",
        "created_at": "2024-01-20 16:45:00",
        "updated_at": "2024-01-20 16:45:00"
    },
    {
        "id": 2,
        "participant_id": 2,
        "payment_method_id": 2,
        "amount": 1500.00,
        "usd_amount": 1500.00,
        "payment_date": "2024-01-21",
        "payment_status": 2,
        "reference_number": "PAY_002_2024",
        "notes": "Registration fee payment - pending verification",
        "created_at": "2024-01-21 11:30:00",
        "updated_at": "2024-01-21 11:30:00"
    }
]

SAMPLE_AMBASSADORS = [
    {
        "id": 1,
        "participant_id": 1,
        "ambassador_code": "AMB_001",
        "category": "university",
        "status": "active",
        "referral_count": 15,
        "commission_earned": 750.00,
        "is_active": 1,
        "created_at": "2024-01-25 12:00:00",
        "updated_at": "2024-01-25 12:00:00"
    }
]

def test_health_check():
    """Test basic health check"""
    print("\\n=== Testing Health Check ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_participants_export():
    """Test participants export"""
    print("\\n=== Testing Participants Export ===")
    
    # Test standard template
    payload = {
        "data": SAMPLE_PARTICIPANTS,
        "template": "standard",
        "format": "excel",
        "filename": "test_participants_standard.xlsx"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/ybb/export/participants", json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Export ID: {result['data']['export_id']}")
            print(f"File Name: {result['data']['file_name']}")
            print(f"Record Count: {result['data']['record_count']}")
            return result['data']['export_id']
        else:
            print(f"Error: {response.json()}")
            return None
            
    except Exception as e:
        print(f"Participants export failed: {e}")
        return None

def test_payments_export():
    """Test payments export"""
    print("\\n=== Testing Payments Export ===")
    
    payload = {
        "data": SAMPLE_PAYMENTS,
        "template": "detailed",
        "format": "excel",
        "filename": "test_payments_detailed.xlsx"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/ybb/export/payments", json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Export ID: {result['data']['export_id']}")
            print(f"File Name: {result['data']['file_name']}")
            print(f"Record Count: {result['data']['record_count']}")
            return result['data']['export_id']
        else:
            print(f"Error: {response.json()}")
            return None
            
    except Exception as e:
        print(f"Payments export failed: {e}")
        return None

def test_ambassadors_export():
    """Test ambassadors export"""
    print("\\n=== Testing Ambassadors Export ===")
    
    payload = {
        "data": SAMPLE_AMBASSADORS,
        "template": "standard",
        "format": "excel",
        "filename": "test_ambassadors_standard.xlsx"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/ybb/export/ambassadors", json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Export ID: {result['data']['export_id']}")
            print(f"File Name: {result['data']['file_name']}")
            print(f"Record Count: {result['data']['record_count']}")
            return result['data']['export_id']
        else:
            print(f"Error: {response.json()}")
            return None
            
    except Exception as e:
        print(f"Ambassadors export failed: {e}")
        return None

def test_large_dataset():
    """Test large dataset with chunking"""
    print("\\n=== Testing Large Dataset (6000 participants) ===")
    
    # Generate large dataset
    large_participants = []
    for i in range(6000):
        participant = {
            "id": i + 1,
            "form_id": f"YBB2024_{i+1:06d}",
            "first_name": f"First{i+1}",
            "last_name": f"Last{i+1}",
            "email": f"user{i+1}@example.com",
            "phone": f"+123456{i+1:04d}",
            "birthdate": "1995-01-01",
            "nationality": "American",
            "state": "California",
            "form_status": (i % 4) + 1,  # Status 1-4
            "is_active": 1,
            "created_at": "2024-01-15 10:30:00",
            "updated_at": "2024-01-15 10:30:00"
        }
        large_participants.append(participant)
    
    payload = {
        "data": large_participants,
        "template": "complete",
        "format": "excel",
        "filename": "test_large_participants.xlsx"
    }
    
    try:
        print(f"Sending {len(large_participants)} participants for export...")
        start_time = time.time()
        
        response = requests.post(f"{BASE_URL}/api/ybb/export/participants", json=payload)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Processing Time: {processing_time:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Export Strategy: {result.get('export_strategy', 'single_file')}")
            print(f"Export ID: {result['data']['export_id']}")
            
            if "total_files" in result["data"]:
                print(f"Total Files: {result['data']['total_files']}")
                print(f"ZIP File Size: {result['data']['archive']['zip_file_size']:,} bytes")
                print(f"Compression Ratio: {result['data']['archive']['compression_ratio']}")
            else:
                print(f"Single File Size: {result['data']['file_size']:,} bytes")
            
            return result['data']['export_id']
        else:
            print(f"Error: {response.json()}")
            return None
            
    except Exception as e:
        print(f"Large dataset export failed: {e}")
        return None

def test_export_status(export_id):
    """Test export status check"""
    print(f"\\n=== Testing Export Status for {export_id} ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/ybb/export/{export_id}/status")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Export Status: {result['status']}")
            print(f"Export Type: {result['export_type']}")
            print(f"Record Count: {result['record_count']}")
            print(f"Created At: {result['created_at']}")
            return True
        else:
            print(f"Error: {response.json()}")
            return False
            
    except Exception as e:
        print(f"Status check failed: {e}")
        return False

def test_download_export(export_id):
    """Test export download"""
    print(f"\\n=== Testing Export Download for {export_id} ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/ybb/export/{export_id}/download")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            content_length = len(response.content)
            print(f"Content Type: {content_type}")
            print(f"File Size: {content_length:,} bytes")
            
            # Save file for verification
            filename = f"downloaded_export_{export_id}.xlsx"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"File saved as: {filename}")
            return True
        else:
            print(f"Download failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Download failed: {e}")
        return False

def test_templates():
    """Test templates endpoint"""
    print("\\n=== Testing Templates Endpoint ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/ybb/templates")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Available templates:")
            for export_type, templates in result['data'].items():
                print(f"  {export_type}:")
                for template_name, template_info in templates.items():
                    print(f"    - {template_name}: {len(template_info['fields'])} fields")
            return True
        else:
            print(f"Error: {response.json()}")
            return False
            
    except Exception as e:
        print(f"Templates test failed: {e}")
        return False

def test_status_mappings():
    """Test status mappings endpoint"""
    print("\\n=== Testing Status Mappings Endpoint ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/ybb/status-mappings")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Available status mappings:")
            for mapping_type, mappings in result['data'].items():
                print(f"  {mapping_type}: {len(mappings)} options")
            return True
        else:
            print(f"Error: {response.json()}")
            return False
            
    except Exception as e:
        print(f"Status mappings test failed: {e}")
        return False

def run_comprehensive_test():
    """Run comprehensive test suite"""
    print("=" * 60)
    print("YBB Export API - Comprehensive Test Suite")
    print("=" * 60)
    
    test_results = {}
    
    # Test 1: Health Check
    test_results['health'] = test_health_check()
    
    if not test_results['health']:
        print("\\n❌ Server not responding. Please start the Flask service.")
        return
    
    # Test 2: Templates and Configuration
    test_results['templates'] = test_templates()
    test_results['status_mappings'] = test_status_mappings()
    
    # Test 3: Basic Exports
    export_ids = {}
    export_ids['participants'] = test_participants_export()
    export_ids['payments'] = test_payments_export()
    export_ids['ambassadors'] = test_ambassadors_export()
    
    # Test 4: Large Dataset
    export_ids['large_dataset'] = test_large_dataset()
    
    # Test 5: Status Checks
    for export_type, export_id in export_ids.items():
        if export_id:
            test_results[f'status_{export_type}'] = test_export_status(export_id)
    
    # Test 6: Downloads
    for export_type, export_id in export_ids.items():
        if export_id:
            test_results[f'download_{export_type}'] = test_download_export(export_id)
    
    # Test Summary
    print("\\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed_tests = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name.ljust(25)}: {status}")
    
    print(f"\\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\\n🎉 All tests passed! YBB Export API is working correctly.")
    else:
        print(f"\\n⚠️  {total_tests - passed_tests} test(s) failed. Please check the errors above.")

if __name__ == "__main__":
    run_comprehensive_test()
