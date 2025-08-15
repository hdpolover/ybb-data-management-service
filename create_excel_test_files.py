#!/usr/bin/env python3
"""
Create a maximally compatible Excel file for testing
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tempfile
from datetime import datetime

def create_minimal_excel_test():
    """Create the most basic, compatible Excel file possible"""
    
    print("🎯 Creating Minimal Excel Test File")
    print("=" * 40)
    
    # Absolutely minimal test data
    minimal_data = [
        {"ID": 1, "Name": "Test User", "Status": "Active"},
        {"ID": 2, "Name": "Another User", "Status": "Inactive"}
    ]
    
    try:
        from utils.excel_exporter import ExcelExporter
        
        print("Creating minimal Excel file...")
        excel_output = ExcelExporter.create_excel_file(
            data=minimal_data,
            filename="minimal_test.xlsx",
            sheet_name="Sheet1"  # Use default sheet name
        )
        
        content = excel_output.getvalue()
        print(f"✅ Generated {len(content)} bytes")
        
        # Save with timestamp for identification
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_file = f"d:\\Work\\ybb-data-management-web-flask\\temp\\excel_test_{timestamp}.xlsx"
        
        # Ensure temp directory exists
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        
        with open(test_file, 'wb') as f:
            f.write(content)
        
        print(f"📁 Test file saved: {test_file}")
        print("\n📋 Manual Test Instructions:")
        print(f"1. Navigate to: {test_file}")
        print("2. Double-click to open in Excel")
        print("3. If it opens successfully, the fix is working")
        print("4. If it fails, please note the exact error message")
        
        return test_file
        
    except Exception as e:
        print(f"❌ Failed to create test file: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def create_api_test_file():
    """Create a test file using actual API call"""
    
    print("\n🌐 Creating API Test File")
    print("=" * 40)
    
    import requests
    
    api_data = {
        "export_type": "participants",
        "template": "standard",
        "format": "excel",
        "data": [
            {
                "id": 1,
                "full_name": "Test Participant",
                "email": "test@example.com",
                "form_status": "approved",
                "created_at": "2024-01-15"
            }
        ]
    }
    
    try:
        print("Making API request...")
        response = requests.post(
            "http://127.0.0.1:5000/api/ybb/export/participants",
            json=api_data,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ API request failed: {response.status_code}")
            return None
        
        result = response.json()
        export_id = result.get('data', {}).get('export_id')
        
        # Download
        download_response = requests.get(
            f"http://127.0.0.1:5000/api/ybb/export/{export_id}/download",
            timeout=30
        )
        
        if download_response.status_code != 200:
            print(f"❌ Download failed: {download_response.status_code}")
            return None
        
        # Save with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        api_test_file = f"d:\\Work\\ybb-data-management-web-flask\\temp\\api_excel_test_{timestamp}.xlsx"
        
        os.makedirs(os.path.dirname(api_test_file), exist_ok=True)
        
        with open(api_test_file, 'wb') as f:
            f.write(download_response.content)
        
        print(f"✅ API test file saved: {api_test_file}")
        return api_test_file
        
    except requests.exceptions.ConnectionError:
        print("⚠️  API server not running")
        return None
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")
        return None

if __name__ == "__main__":
    print("🧪 Creating Excel Test Files for Manual Verification")
    print("=" * 60)
    
    # Create minimal test file
    minimal_file = create_minimal_excel_test()
    
    # Create API test file
    api_file = create_api_test_file()
    
    print("\n" + "=" * 60)
    print("📊 Test Files Created:")
    
    if minimal_file:
        print(f"✅ Minimal Test: {minimal_file}")
    else:
        print("❌ Minimal Test: Failed")
    
    if api_file:
        print(f"✅ API Test: {api_file}")
    else:
        print("❌ API Test: Failed (server not running or other issue)")
    
    print("\n🔍 Manual Testing Instructions:")
    print("1. Open Windows Explorer")
    print("2. Navigate to the file paths shown above")
    print("3. Double-click each .xlsx file to open in Excel")
    print("4. If they open without errors, the fix is successful")
    print("5. If you get errors, please copy the exact error message")
    
    print("\n💡 Troubleshooting:")
    print("- Try opening with different Excel versions if available")
    print("- Try opening in LibreOffice Calc or Google Sheets")
    print("- Check if file associations are correct")
    print("- Verify Excel is properly installed")
