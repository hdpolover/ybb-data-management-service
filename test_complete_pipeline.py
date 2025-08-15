#!/usr/bin/env python3
"""
Complete Excel Generation Pipeline Test
Tests the entire process from service to file serving
"""
import os
import sys
import json
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime

# Add the directory containing our modules to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_local_service():
    """Test the YBB Export Service directly"""
    print("\n=== Testing YBB Export Service Directly ===")
    
    try:
        from services.ybb_export_service import YBBExportService
        
        # Create sample data
        data = [
            {
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'test@example.com',
                'phone_number': '123-456-7890',
                'passport_number': 'ABC123456',
                'country': 'Test Country',
                'birth_date': '1990-01-01',
                'registration_date': '2024-01-01'
            }
        ]
        
        # Test Excel creation
        service = YBBExportService()
        success, file_path_or_error = service.create_excel_file(data, 'test_participants')
        
        if success:
            print(f"✅ Excel file created successfully: {file_path_or_error}")
            
            # Test if file can be read
            try:
                df = pd.read_excel(file_path_or_error)
                print(f"✅ Excel file is readable with {len(df)} rows")
                print("✅ Columns:", list(df.columns))
                
                # Check file size
                file_size = Path(file_path_or_error).stat().st_size
                print(f"✅ File size: {file_size} bytes")
                
                return True, file_path_or_error
                
            except Exception as e:
                print(f"❌ Error reading created Excel file: {e}")
                return False, str(e)
        else:
            print(f"❌ Excel creation failed: {file_path_or_error}")
            return False, file_path_or_error
            
    except Exception as e:
        print(f"❌ Service test error: {e}")
        return False, str(e)

def test_api_endpoint():
    """Test the API endpoint"""
    print("\n=== Testing API Endpoint ===")
    
    api_url = "http://localhost:5000/api/export"
    
    # Prepare test data
    payload = {
        "data": [
            {
                "first_name": "API",
                "last_name": "Test",
                "email": "api@test.com",
                "phone_number": "555-0123",
                "passport_number": "XYZ789",
                "country": "API Country",
                "birth_date": "1985-05-15",
                "registration_date": "2024-01-15"
            }
        ],
        "filename": "api_test_participants",
        "format": "xlsx"
    }
    
    try:
        print("Sending POST request to API...")
        response = requests.post(
            api_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ API request successful")
            
            # Check headers
            content_type = response.headers.get('content-type', '')
            print(f"✅ Content-Type: {content_type}")
            
            content_disposition = response.headers.get('content-disposition', '')
            print(f"✅ Content-Disposition: {content_disposition}")
            
            # Save the response to a file for testing
            test_file_path = "test_api_download.xlsx"
            with open(test_file_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ File saved as: {test_file_path}")
            
            # Test if file can be read
            try:
                df = pd.read_excel(test_file_path)
                print(f"✅ Downloaded Excel file is readable with {len(df)} rows")
                print("✅ Columns:", list(df.columns))
                
                # Clean up
                os.unlink(test_file_path)
                
                return True, "API test successful"
                
            except Exception as e:
                print(f"❌ Error reading downloaded Excel file: {e}")
                return False, str(e)
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False, f"API returned {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API - is the server running?")
        return False, "Connection error"
    except Exception as e:
        print(f"❌ API test error: {e}")
        return False, str(e)

def test_robust_service():
    """Test the RobustExcelService directly"""
    print("\n=== Testing RobustExcelService Directly ===")
    
    try:
        from robust_excel_service import RobustExcelService
        
        # Create sample data
        data = [
            {
                'name': 'Test User 🌟',  # Unicode character
                'email': 'test@example.com',
                'notes': 'Special chars: <>&"\'',  # Special characters
                'date': datetime.now().strftime('%Y-%m-%d'),
                'number': 12345.67
            }
        ]
        
        service = RobustExcelService()
        result = service.create_excel_file_robust(data, 'robust_test')
        
        if result['success']:
            file_path = result['file_path']
            print(f"✅ Robust Excel file created: {file_path}")
            
            # Test reading
            df = pd.read_excel(file_path)
            print(f"✅ File readable with {len(df)} rows")
            print("✅ Data preview:")
            print(df.to_string())
            
            return True, file_path
        else:
            print(f"❌ Robust service failed: {result['error']}")
            return False, result['error']
            
    except Exception as e:
        print(f"❌ Robust service test error: {e}")
        return False, str(e)

def main():
    """Run all tests"""
    print("🧪 Complete Excel Pipeline Testing")
    print("=" * 50)
    
    results = {
        'local_service': False,
        'api_endpoint': False,
        'robust_service': False
    }
    
    # Test 1: Local Service
    success, result = test_local_service()
    results['local_service'] = success
    
    # Test 2: Robust Service
    success, result = test_robust_service()
    results['robust_service'] = success
    
    # Test 3: API Endpoint
    success, result = test_api_endpoint()
    results['api_endpoint'] = success
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 Test Results Summary")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Excel generation pipeline is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    main()
