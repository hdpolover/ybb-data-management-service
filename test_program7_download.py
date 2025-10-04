#!/usr/bin/env python3
"""
Program 7 Export Test with Download
Test participant export for program 7 and save downloadable file
"""

import requests
import json
import time
import os
from datetime import datetime

# Test configuration
BASE_URL = 'http://localhost:5000'
PROGRAM_ID = 7

def test_program7_export():
    """Test program 7 export and download file"""
    print("🧪 Program 7 Export & Download Test")
    print("="*60)
    
    # Check if server is running
    try:
        health_response = requests.get(f'{BASE_URL}/health')
        if health_response.status_code != 200:
            print("❌ Server not running")
            return
        print("✅ Server is running")
    except:
        print("❌ Cannot connect to server")
        return

    # Get record count first
    print(f"\n📊 Checking Program {PROGRAM_ID} record count...")
    count_url = f'{BASE_URL}/api/ybb/db/export/count'
    count_data = {
        'program_id': PROGRAM_ID
    }
    
    try:
        count_response = requests.post(count_url, json=count_data)
        if count_response.status_code == 200:
            count_result = count_response.json()
            total_records = count_result['total_records']
            print(f"   📈 Total records: {total_records:,}")
            print(f"   📊 Estimated file size: {count_result['estimates']['estimated_file_size_mb']:.1f} MB")
            print(f"   ⏱️ Estimated processing time: {count_result['estimates']['estimated_processing_time_seconds']:.1f} seconds")
        else:
            print(f"   ❌ Count check failed: {count_response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Count check error: {e}")
        return

    # Test basic export
    print(f"\n🚀 Starting Program {PROGRAM_ID} Export...")
    export_url = f'{BASE_URL}/api/ybb/db/export/participants'
    export_data = {
        'program_id': PROGRAM_ID,
        'filters': {}  # No filters - all participants
    }
    
    start_time = time.time()
    
    try:
        export_response = requests.post(export_url, json=export_data)
        processing_time = time.time() - start_time
        
        if export_response.status_code == 200:
            # Save the file
            filename = f'program_{PROGRAM_ID}_participants_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            downloads_path = os.path.expanduser('~/Downloads')
            file_path = os.path.join(downloads_path, filename)
            
            # Write file content
            with open(file_path, 'wb') as f:
                f.write(export_response.content)
            
            file_size = len(export_response.content)
            file_size_mb = file_size / (1024 * 1024)
            
            print("   ✅ Export successful!")
            print(f"   📄 File saved to: {file_path}")
            print(f"   📊 File size: {file_size_mb:.2f} MB ({file_size:,} bytes)")
            print(f"   ⏱️ Processing time: {processing_time:.2f} seconds")
            
            # Calculate throughput
            if total_records > 0:
                throughput = total_records / processing_time
                print(f"   🚀 Throughput: {throughput:.0f} records/second")
            
            # Parse response headers for additional info
            if 'Content-Disposition' in export_response.headers:
                print(f"   📋 Original filename: {export_response.headers['Content-Disposition']}")
            
        else:
            print(f"   ❌ Export failed: {export_response.status_code}")
            try:
                error_data = export_response.json()
                print(f"   ❌ Error: {error_data.get('message', 'Unknown error')}")
            except:
                print(f"   ❌ Error response: {export_response.text[:200]}...")
                
    except Exception as e:
        print(f"   ❌ Export error: {e}")

    print("\n🎯 Test completed!")

def test_with_essay_filter():
    """Test export with essay filter"""
    print(f"\n📚 Testing with_essay filter...")
    
    export_url = f'{BASE_URL}/api/ybb/db/export/participants'
    export_data = {
        'program_id': PROGRAM_ID,
        'filters': {
            'with_essay': True
        }
    }
    
    start_time = time.time()
    
    try:
        export_response = requests.post(export_url, json=export_data)
        processing_time = time.time() - start_time
        
        if export_response.status_code == 200:
            # Save the file
            filename = f'program_{PROGRAM_ID}_with_essays_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            downloads_path = os.path.expanduser('~/Downloads')
            file_path = os.path.join(downloads_path, filename)
            
            with open(file_path, 'wb') as f:
                f.write(export_response.content)
            
            file_size_mb = len(export_response.content) / (1024 * 1024)
            
            print("   ✅ Essay filter export successful!")
            print(f"   📄 File saved to: {file_path}")
            print(f"   📊 File size: {file_size_mb:.2f} MB")
            print(f"   ⏱️ Processing time: {processing_time:.2f} seconds")
            
        else:
            print(f"   ❌ Essay filter export failed: {export_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Essay filter error: {e}")

if __name__ == "__main__":
    test_program7_export()
    test_with_essay_filter()