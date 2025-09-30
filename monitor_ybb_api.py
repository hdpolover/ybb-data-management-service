#!/usr/bin/env python3
"""
Monitor script for YBB Export Service
Use this to check export availability and prevent 404 errors
"""
import sys
import os
import requests
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_api_health(api_url):
    """Check if the API is running"""
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)

def get_storage_info(api_url):
    """Get storage information from the API"""
    try:
        response = requests.get(f"{api_url}/api/ybb/storage/info", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def create_test_export(api_url):
    """Create a test export to verify functionality"""
    test_data = {
        'export_type': 'participants',
        'data': [
            {'id': 1, 'name': 'Monitor Test', 'email': 'test@monitor.com'}
        ],
        'filename': f'Monitor_Test_{datetime.now().strftime("%H%M%S")}.xlsx'
    }
    
    try:
        response = requests.post(
            f"{api_url}/api/ybb/export/participants",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def check_export_download(api_url, export_id):
    """Check if an export can be downloaded (prevents 404)"""
    try:
        response = requests.get(f"{api_url}/api/ybb/export/{export_id}/download", timeout=10)
        if response.status_code == 200:
            return True, f"File size: {len(response.content)} bytes"
        elif response.status_code == 404:
            return False, "Export not found (404 error)"
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)

def monitor_ybb_api(api_url="http://localhost:5000"):
    """Main monitoring function"""
    print("🔍 YBB Export Service Monitor")
    print("=" * 50)
    print(f"API URL: {api_url}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. Check API Health
    print("1️⃣ Checking API Health...")
    health_ok, health_result = check_api_health(api_url)
    if health_ok:
        print(f"   ✅ API is healthy")
        print(f"   📊 Service: {health_result.get('service', 'Unknown')}")
        print(f"   📊 Version: {health_result.get('version', 'Unknown')}")
    else:
        print(f"   ❌ API health check failed: {health_result}")
        return False
    
    # 2. Check Storage Status
    print("\n2️⃣ Checking Storage Status...")
    storage_ok, storage_result = get_storage_info(api_url)
    if storage_ok:
        print(f"   ✅ Storage info retrieved")
        print(f"   📊 Total exports: {storage_result.get('total_exports', 0)}")
        print(f"   📊 Total files: {storage_result.get('total_files', 0)}")
        print(f"   📊 Storage used: {storage_result.get('total_size_mb', 0):.2f} MB")
        print(f"   📊 Max concurrent: {storage_result.get('max_concurrent_exports', 0)}")
        
        # Check if approaching limits
        total_exports = storage_result.get('total_exports', 0)
        max_exports = storage_result.get('max_concurrent_exports', 20)
        if total_exports >= max_exports * 0.8:  # 80% threshold
            print(f"   ⚠️  Warning: Approaching export limit ({total_exports}/{max_exports})")
    else:
        print(f"   ❌ Storage check failed: {storage_result}")
    
    # 3. Test Export Creation & Download
    print("\n3️⃣ Testing Export Creation & Download...")
    export_ok, export_result = create_test_export(api_url)
    if export_ok and export_result.get('status') == 'success':
        export_id = export_result.get('data', {}).get('export_id')
        print(f"   ✅ Test export created: {export_id}")
        
        # Test immediate download (this is where 404 errors occurred)
        print("   🔄 Testing immediate download (404 error check)...")
        download_ok, download_result = check_export_download(api_url, export_id)
        if download_ok:
            print(f"   ✅ Download successful: {download_result}")
            print(f"   🎉 No 404 error - export immediately available!")
        else:
            print(f"   ❌ Download failed: {download_result}")
            print(f"   🚨 This would cause a 404 error in CodeIgniter!")
            return False
    else:
        print(f"   ❌ Test export failed: {export_result}")
        return False
    
    # 4. Summary
    print("\n📋 Monitor Summary:")
    if health_ok and storage_ok and export_ok and download_ok:
        print("   🎉 ALL CHECKS PASSED")
        print("   ✅ API is healthy")
        print("   ✅ Storage is working")
        print("   ✅ Exports can be created")
        print("   ✅ Downloads work immediately (no 404 errors)")
        print("\n   💡 The 404 error fix is working correctly!")
        return True
    else:
        print("   ⚠️  SOME CHECKS FAILED")
        print("   🔧 Review the issues above")
        return False

def main():
    """Main function"""
    # Check if custom API URL provided
    api_url = "http://localhost:5000"
    if len(sys.argv) > 1:
        api_url = sys.argv[1]
    
    try:
        success = monitor_ybb_api(api_url)
        if success:
            print(f"\n✅ Monitoring completed successfully")
            sys.exit(0)
        else:
            print(f"\n❌ Monitoring detected issues")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⏹️  Monitoring stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Monitoring failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
