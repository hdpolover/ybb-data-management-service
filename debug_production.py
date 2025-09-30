#!/usr/bin/env python3
"""
Simple test to verify what's happening with production exports
"""
import requests
import json
import time

def test_production_issue():
    api_url = "https://ybb-data-management-service-production.up.your-deployment-service.com"
    
    print("🔍 Investigating Production 404 Issues")
    print("=" * 50)
    
    # Test data
    test_data = {
        'export_type': 'participants',
        'data': [
            {'id': 1, 'name': 'Debug Test', 'email': 'debug@test.com'}
        ],
        'filename': 'Debug_Test.xlsx'
    }
    
    print("🔄 Creating export and testing download timing...")
    
    try:
        # Create export
        response = requests.post(f'{api_url}/api/ybb/export/participants', json=test_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            export_id = result.get('data', {}).get('export_id')
            print(f"✅ Export created: {export_id}")
            
            # Test immediate download
            print("🔄 Testing immediate download...")
            download_response = requests.get(f'{api_url}/api/ybb/export/{export_id}/download', timeout=10)
            
            if download_response.status_code == 200:
                print(f"✅ Immediate download: SUCCESS ({len(download_response.content)} bytes)")
            elif download_response.status_code == 404:
                print(f"❌ Immediate download: 404 ERROR")
                
                # Try again after a short delay
                print("🔄 Trying download after 2 seconds...")
                time.sleep(2)
                download_response2 = requests.get(f'{api_url}/api/ybb/export/{export_id}/download', timeout=10)
                
                if download_response2.status_code == 200:
                    print(f"✅ Delayed download: SUCCESS ({len(download_response2.content)} bytes)")
                else:
                    print(f"❌ Delayed download: HTTP {download_response2.status_code}")
            else:
                print(f"❌ Download failed: HTTP {download_response.status_code}")
                
        else:
            print(f"❌ Export creation failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_production_issue()
