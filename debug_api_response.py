#!/usr/bin/env python3
"""
Debug API Response - Check what the API is actually returning
"""
import requests
import json

def debug_api_response():
    """Debug the API response to understand the workflow"""
    
    api_url = "http://localhost:5000/api/ybb/export/participants"
    
    # Simple test payload
    payload = {
        "data": [
            {
                "first_name": "Test",
                "last_name": "User",
                "email": "test@example.com"
            }
        ],
        "format": "xlsx"
    }
    
    try:
        print("🔍 Debugging API Response")
        print("=" * 30)
        print(f"URL: {api_url}")
        
        response = requests.post(
            api_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Response Size: {len(response.content)} bytes")
        
        # Try to parse as JSON
        try:
            json_response = response.json()
            print("\n📄 JSON Response:")
            print(json.dumps(json_response, indent=2))
            
            # Check if it's an export creation response
            if 'data' in json_response and 'export_id' in json_response['data']:
                export_id = json_response['data']['export_id']
                print(f"\n✅ Export created with ID: {export_id}")
                
                # Try to download the file
                download_url = f"http://localhost:5000/api/ybb/export/{export_id}/download"
                print(f"🔗 Trying download URL: {download_url}")
                
                download_response = requests.get(download_url, timeout=30)
                print(f"Download Status: {download_response.status_code}")
                print(f"Download Content-Type: {download_response.headers.get('content-type')}")
                print(f"Download Size: {len(download_response.content)} bytes")
                
                if download_response.status_code == 200:
                    # Save the file
                    with open('debug_downloaded_file.xlsx', 'wb') as f:
                        f.write(download_response.content)
                    
                    print("✅ File downloaded and saved as: debug_downloaded_file.xlsx")
                    
                    # Test reading
                    import pandas as pd
                    try:
                        df = pd.read_excel('debug_downloaded_file.xlsx')
                        print(f"✅ File readable! {len(df)} rows")
                        print("✅ SUCCESS: The API workflow is working!")
                        return True
                    except Exception as e:
                        print(f"❌ File not readable: {e}")
                        return False
                else:
                    print(f"❌ Download failed: {download_response.text}")
                    return False
            else:
                print("❌ No export_id in response")
                return False
                
        except json.JSONDecodeError:
            print("❌ Response is not JSON")
            print(f"Raw response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        return False

if __name__ == "__main__":
    debug_api_response()
