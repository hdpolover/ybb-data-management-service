#!/usr/bin/env python3
"""
Demo script showing how to export participants data from the YBB API
This demonstrates the same calls that CodeIgniter 4 would make
"""

import requests
import json
from datetime import datetime, timedelta

# API Configuration
API_BASE_URL = "http://127.0.0.1:5000"

def demo_participants_export():
    """Demonstrate participants export with sample data"""
    
    # Sample participants data (this would come from your CI4 database)
    sample_participants = [
        {
            "id": 1,
            "name": "Alice Johnson",
            "email": "alice@ybbsummit2025.com",
            "phone": "+1-555-0101",
            "program_id": 101,
            "form_status": "approved",
            "birthdate": "1999-03-15",
            "country": "USA",
            "university": "Stanford University",
            "created_at": "2025-07-26 09:30:00",
            "updated_at": "2025-07-26 10:15:00"
        },
        {
            "id": 2,
            "name": "Bob Chen",
            "email": "bob@ybbsummit2025.com",
            "phone": "+1-555-0102",
            "program_id": 101,
            "form_status": "pending",
            "birthdate": "1998-11-22",
            "country": "Canada",
            "university": "University of Toronto",
            "created_at": "2025-07-26 10:00:00",
            "updated_at": "2025-07-26 10:30:00"
        },
        {
            "id": 3,
            "name": "Maria Garcia",
            "email": "maria@ybbsummit2025.com",
            "phone": "+1-555-0103",
            "program_id": 101,
            "form_status": "approved",
            "birthdate": "2000-08-10",
            "country": "Mexico",
            "university": "Universidad Nacional",
            "created_at": "2025-07-26 11:00:00",
            "updated_at": "2025-07-26 11:30:00"
        }
    ]
    
    # Export payload (exactly what CI4 would send)
    export_payload = {
        "data": sample_participants,
        "template": "standard",  # Options: standard, detailed, summary, complete
        "format": "excel",       # Options: excel, csv
        "filename": "YBB_Participants_Export_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".xlsx",
        "sheet_name": "Participants Data",
        "filters": {
            "program_id": 101,
            "status": "all",
            "date_from": "2025-07-01",
            "date_to": "2025-07-31"
        },
        "options": {
            "include_related": True,
            "sort_by": "created_at",
            "sort_order": "desc"
        }
    }
    
    print("🚀 Starting Participants Export Demo...")
    print(f"📊 Exporting {len(sample_participants)} participants")
    print(f"🎯 Template: {export_payload['template']}")
    print(f"📄 Format: {export_payload['format']}")
    print(f"📁 Filename: {export_payload['filename']}")
    
    try:
        # Send request to API
        response = requests.post(
            f"{API_BASE_URL}/api/ybb/export/participants",
            json=export_payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"\n📡 API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Export completed successfully!")
            
            # Display results
            data = result.get('data', {})
            metadata = result.get('metadata', {})
            
            print(f"\n📋 Export Details:")
            print(f"   🆔 Export ID: {data.get('export_id')}")
            print(f"   📁 Filename: {data.get('file_name')}")
            print(f"   📊 Records: {data.get('record_count')}")
            print(f"   💾 File Size: {format_file_size(data.get('file_size', 0))}")
            print(f"   ⏱️  Processing Time: {metadata.get('processing_time', 0):.2f}s")
            print(f"   🔗 Download URL: {API_BASE_URL}{data.get('file_url')}")
            print(f"   ⏰ Expires At: {data.get('expires_at')}")
            
            return result
            
        else:
            error_result = response.json()
            print("❌ Export failed!")
            print(f"   Error: {error_result.get('message')}")
            print(f"   Request ID: {error_result.get('request_id')}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return None

def demo_download_export(export_result):
    """Demonstrate downloading the exported file"""
    if not export_result or export_result.get('status') != 'success':
        print("❌ No valid export to download")
        return False
    
    data = export_result.get('data', {})
    download_url = f"{API_BASE_URL}{data.get('file_url')}"
    filename = data.get('file_name')
    
    print(f"\n📥 Downloading export file...")
    print(f"   🔗 URL: {download_url}")
    print(f"   📁 Filename: {filename}")
    
    try:
        response = requests.get(download_url, timeout=30)
        
        if response.status_code == 200:
            # Save file locally for demonstration
            local_filename = f"downloads/{filename}"
            
            # Create downloads directory
            import os
            os.makedirs('downloads', exist_ok=True)
            
            with open(local_filename, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ File downloaded successfully!")
            print(f"   📍 Saved to: {local_filename}")
            print(f"   💾 Size: {format_file_size(len(response.content))}")
            
            return True
        else:
            print(f"❌ Download failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Download error: {e}")
        return False

def format_file_size(bytes_size):
    """Format file size for display"""
    if bytes_size >= 1024*1024:
        return f"{bytes_size / (1024*1024):.2f} MB"
    elif bytes_size >= 1024:
        return f"{bytes_size / 1024:.2f} KB"
    else:
        return f"{bytes_size} bytes"

def demo_available_templates():
    """Show available export templates"""
    print("\n📋 Available Export Templates:")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/ybb/templates/participants")
        
        if response.status_code == 200:
            result = response.json()
            templates = result.get('data', {})
            
            for template_name, template_info in templates.items():
                print(f"\n   🎯 {template_name.upper()}:")
                print(f"      📝 Description: {template_info.get('description', 'No description')}")
                print(f"      📊 Fields: {len(template_info.get('fields', []))} columns")
                if template_info.get('includes_sensitive_data'):
                    print(f"      🔒 Includes sensitive data")
        else:
            print("   ❌ Failed to retrieve templates")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🎯 YBB Data Management API - Participants Export Demo")
    print("=" * 60)
    
    # Show available templates
    demo_available_templates()
    
    # Run export demo
    result = demo_participants_export()
    
    # Download the file if export was successful
    if result:
        demo_download_export(result)
    
    print("\n" + "=" * 60)
    print("✅ Demo completed!")
    print("💡 Use this same pattern in your CodeIgniter 4 application")
    print("=" * 60)