#!/usr/bin/env python3
"""
Test script to debug payment export issues
Run this with: python test_payment_export.py
"""
import requests
import json
import sys
import time
import os

BASE_URL = "http://localhost:5000"

def test_health():
    """Test if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ Server is running: {response.json().get('service', 'Unknown')}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"❌ Server is not running at {BASE_URL}")
        print("Please start the Flask app with: python app.py")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_payment_export():
    """Test payment export endpoint"""
    print("\n" + "="*60)
    print("Testing Payment Export")
    print("="*60)
    
    payload = {
        "filters": {
            "status": "all"
        },
        "options": {
            "template": "standard",
            "format": "excel",
            "filename": "Test_Payments_Export.xlsx",
            "sheet_name": "Payments"
        }
    }
    
    print(f"\n📤 Sending request to: {BASE_URL}/api/ybb/db/export/payments")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/ybb/db/export/payments",
            json=payload,
            timeout=60
        )
        
        print(f"\n📊 Status Code: {response.status_code}")
        print(f"📋 Response Headers:")
        for key, value in response.headers.items():
            print(f"   {key}: {value}")
        
        # Check content type
        content_type = response.headers.get('Content-Type', '')
        
        if 'application/json' in content_type:
            # JSON response
            print(f"\n📄 JSON Response:")
            try:
                json_data = response.json()
                print(json.dumps(json_data, indent=2))
                
                # Check for errors
                if json_data.get('status') == 'error':
                    print(f"\n❌ Export failed: {json_data.get('message')}")
                    return False
                    
            except Exception as e:
                print(f"Failed to parse JSON: {e}")
                print(f"Raw response: {response.text[:500]}")
            return False
            
        elif 'excel' in content_type or 'spreadsheet' in content_type:
            # Excel file response
            filename = response.headers.get('Content-Disposition', '').split('filename=')[-1].strip('"')
            if not filename:
                filename = "payment_export_unknown.xlsx"
                
            print(f"\n✅ Received Excel file: {filename}")
            print(f"📏 File size: {len(response.content)} bytes")
            
            # Save file
            output_path = f"/tmp/{filename}"
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"💾 Saved to: {output_path}")
            
            # Check if it's a valid Excel file
            if response.content.startswith(b'PK'):
                print("✅ Valid Excel file (PK signature found)")
                return True
            else:
                print("❌ Invalid Excel file (missing PK signature)")
                print(f"First 100 bytes: {response.content[:100]}")
                return False
        else:
            print(f"\n❓ Unknown content type: {content_type}")
            print(f"Response preview: {response.text[:500]}")
            return False
        
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_participant_export():
    """Test participant export for comparison"""
    print("\n" + "="*60)
    print("Testing Participant Export (for comparison)")
    print("="*60)
    
    payload = {
        "filters": {
            "status": "all"
        },
        "options": {
            "template": "standard",
            "format": "excel",
            "filename": "Test_Participants_Export.xlsx",
            "sheet_name": "Participants"
        }
    }
    
    print(f"\n📤 Sending request to: {BASE_URL}/api/ybb/db/export/participants")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/ybb/db/export/participants",
            json=payload,
            timeout=60
        )
        
        print(f"\n📊 Status Code: {response.status_code}")
        
        content_type = response.headers.get('Content-Type', '')
        
        if 'excel' in content_type or 'spreadsheet' in content_type:
            filename = response.headers.get('Content-Disposition', '').split('filename=')[-1].strip('"')
            print(f"✅ Received Excel file: {filename}")
            print(f"📏 File size: {len(response.content)} bytes")
            return True
        elif 'application/json' in content_type:
            json_data = response.json()
            print(f"📄 JSON Response: {json.dumps(json_data, indent=2)[:500]}")
            if json_data.get('status') == 'error':
                print(f"❌ Error: {json_data.get('message')}")
            return False
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_metadata_mode():
    """Test payment export in metadata mode"""
    print("\n" + "="*60)
    print("Testing Payment Export (Metadata Mode)")
    print("="*60)
    
    payload = {
        "filters": {
            "status": "all"
        },
        "options": {
            "template": "standard",
            "format": "excel"
        },
        "response_mode": "metadata"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/ybb/db/export/payments",
            json=payload,
            timeout=60
        )
        
        print(f"\n📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📄 Metadata Response:")
            print(json.dumps(data, indent=2))
            
            if data.get('status') == 'success':
                export_id = data.get('data', {}).get('export_id')
                print(f"\n✅ Export ID: {export_id}")
                
                # Try to download
                if export_id:
                    return test_download(export_id)
            else:
                print(f"❌ Export failed: {data.get('message')}")
                return False
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_download(export_id):
    """Test downloading a specific export"""
    print(f"\n📥 Testing download for export: {export_id}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/ybb/export/{export_id}/download",
            timeout=60
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            filename = response.headers.get('Content-Disposition', '').split('filename=')[-1].strip('"')
            if not filename:
                filename = f"export_{export_id[:8]}.xlsx"
            print(f"✅ Downloaded: {filename}")
            print(f"📏 Size: {len(response.content)} bytes")
            
            # Save file
            output_path = f"/tmp/{filename}"
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"💾 Saved to: {output_path}")
            
            # Validate
            if response.content.startswith(b'PK'):
                print("✅ Valid Excel file")
            else:
                print("❌ Invalid Excel file")
                
            return True
        elif response.status_code == 404:
            json_data = response.json()
            print(f"❌ Download failed (404): {json_data.get('message')}")
            print(f"Suggestion: {json_data.get('suggestion', 'N/A')}")
            return False
        else:
            print(f"❌ Download failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Payment Export Debugging Test Suite")
    print("="*60)
    
    # Test server health
    if not test_health():
        print("\n❌ Server is not running. Please start the Flask app first.")
        print("\nTo start the server, run:")
        print("  cd /Users/mit06/Desktop/personal-projects/ybb-data-management-service")
        print("  python app.py")
        sys.exit(1)
    
    time.sleep(1)
    
    # Run tests
    tests = [
        ("Metadata Mode", test_metadata_mode),
        ("Direct File Download", test_payment_export),
        ("Participant Export Comparison", test_participant_export),
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n\n{'='*60}")
        print(f"Running: {test_name}")
        print(f"{'='*60}")
        results[test_name] = test_func()
        time.sleep(2)
    
    # Summary
    print("\n\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    print("\n" + ("✅ All tests passed!" if all_passed else "❌ Some tests failed"))
    
    print("\n💡 Files saved to /tmp/ directory")
    print("To view Excel files: open /tmp/*.xlsx")
    
    sys.exit(0 if all_passed else 1)
