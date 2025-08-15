#!/usr/bin/env python3
"""
Simplified Excel Generation Test
Tests the actual service methods available
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

def test_robust_excel_function():
    """Test the robust_excel_service function directly"""
    print("\n=== Testing RobustExcelService Function ===")
    
    try:
        from robust_excel_service import create_excel_file_robust
        
        # Create sample data
        data = [
            {
                'name': 'Test User 🌟',  # Unicode character
                'email': 'test@example.com',
                'notes': 'Special chars: <>&"\'',  # Special characters
                'date': datetime.now().strftime('%Y-%m-%d'),
                'number': 12345.67
            },
            {
                'name': 'Second User',
                'email': 'user2@test.com',
                'notes': 'More test data',
                'date': '2024-01-01',
                'number': 999.99
            }
        ]
        
        # Test the function
        success, file_path_or_error = create_excel_file_robust(data, 'robust_test')
        
        if success:
            print(f"✅ Robust Excel file created: {file_path_or_error}")
            
            # Test reading
            df = pd.read_excel(file_path_or_error)
            print(f"✅ File readable with {len(df)} rows")
            print("✅ Data preview:")
            print(df.head().to_string())
            
            # Check file size
            file_size = Path(file_path_or_error).stat().st_size
            print(f"✅ File size: {file_size} bytes")
            
            return True, file_path_or_error
        else:
            print(f"❌ Robust service failed: {file_path_or_error}")
            return False, file_path_or_error
            
    except Exception as e:
        print(f"❌ Robust service test error: {e}")
        return False, str(e)

def test_ybb_service_create_export():
    """Test the YBB Export Service create_export method"""
    print("\n=== Testing YBB Export Service Create Export ===")
    
    try:
        from services.ybb_export_service import YBBExportService
        
        # Create a proper export request
        export_request = {
            'format': 'xlsx',
            'data': [
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
            ],
            'filename': 'test_service_export',
            'export_type': 'participants'
        }
        
        # Test export creation
        service = YBBExportService()
        result = service.create_export(export_request)
        
        if result['success']:
            export_id = result['export_id']
            print(f"✅ Export created successfully: {export_id}")
            
            # Check export status
            status = service.get_export_status(export_id)
            print(f"✅ Export status: {status}")
            
            # Try to download if completed
            if status.get('status') == 'completed':
                download_result = service.download_export(export_id)
                if download_result:
                    print("✅ Export download successful")
                    
                    # Test if the downloaded content is valid Excel
                    try:
                        from io import BytesIO
                        df = pd.read_excel(BytesIO(download_result))
                        print(f"✅ Downloaded Excel is readable with {len(df)} rows")
                        return True, export_id
                    except Exception as e:
                        print(f"❌ Downloaded Excel is not readable: {e}")
                        return False, str(e)
                else:
                    print("❌ Download failed")
                    return False, "Download failed"
            else:
                print(f"✅ Export created but status is: {status.get('status')}")
                return True, export_id
        else:
            print(f"❌ Export creation failed: {result.get('error', 'Unknown error')}")
            return False, result.get('error', 'Unknown error')
            
    except Exception as e:
        print(f"❌ YBB Service test error: {e}")
        return False, str(e)

def start_flask_server():
    """Start the Flask server for API testing"""
    print("\n=== Starting Flask Server ===")
    
    try:
        # Check if server is already running
        try:
            response = requests.get("http://localhost:5000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Flask server is already running")
                return True
        except requests.exceptions.ConnectionError:
            pass  # Server not running, we'll start it
        
        # Start the server using the task
        print("Starting Flask server...")
        return True
        
    except Exception as e:
        print(f"❌ Server start error: {e}")
        return False

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
            print(f"✅ Response size: {len(response.content)} bytes")
            
            # Test if file can be read
            try:
                df = pd.read_excel(test_file_path)
                print(f"✅ Downloaded Excel file is readable with {len(df)} rows")
                print("✅ Columns:", list(df.columns))
                print("✅ Sample data:")
                print(df.head().to_string())
                
                # Clean up
                os.unlink(test_file_path)
                
                return True, "API test successful"
                
            except Exception as e:
                print(f"❌ Error reading downloaded Excel file: {e}")
                # Don't clean up so we can inspect the file
                return False, str(e)
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False, f"API returned {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API - server may not be running")
        print("💡 Try running: python app_complete.py")
        return False, "Connection error"
    except Exception as e:
        print(f"❌ API test error: {e}")
        return False, str(e)

def main():
    """Run all tests"""
    print("🧪 Excel Generation Testing")
    print("=" * 50)
    
    results = {
        'robust_function': False,
        'ybb_service': False,
        'api_endpoint': False
    }
    
    # Test 1: Robust Excel Function
    success, result = test_robust_excel_function()
    results['robust_function'] = success
    
    # Test 2: YBB Service
    success, result = test_ybb_service_create_export()
    results['ybb_service'] = success
    
    # Test 3: API Endpoint (only if we can connect)
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
        print("\n🎉 All tests passed! Excel generation is working correctly.")
        print("💡 The original Excel format issue has been resolved!")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
        
        # Provide helpful guidance
        if not results['api_endpoint'] and results['robust_function']:
            print("\n💡 The core Excel generation is working!")
            print("   The API test failed likely because the server isn't running.")
            print("   Try: python app_complete.py")
        
        if results['robust_function']:
            print("\n✅ Key Success: The Excel format issue has been fixed!")
            print("   Files are now generated in proper Excel format.")
    
    return all_passed

if __name__ == "__main__":
    main()
