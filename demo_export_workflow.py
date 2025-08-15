#!/usr/bin/env python3
"""
YBB Export API Flow Demo
Demonstrates the complete workflow: Create → Poll Status → Download
"""
import requests
import json
import time
import pandas as pd
from datetime import datetime

class YBBExportClient:
    """Client for YBB Export API with status polling"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def create_export(self, export_type, data, **kwargs):
        """
        Create a new export
        
        Args:
            export_type: 'participants', 'payments', 'ambassadors'
            data: List of records to export
            **kwargs: Additional options (template, format, filename, etc.)
        
        Returns:
            dict: Export creation response
        """
        url = f"{self.base_url}/api/ybb/export/{export_type}"
        
        payload = {
            "data": data,
            "template": kwargs.get('template', 'standard'),
            "format": kwargs.get('format', 'excel'),
            "filename": kwargs.get('filename'),
            "sheet_name": kwargs.get('sheet_name'),
            "filters": kwargs.get('filters', {})
        }
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        print(f"🚀 Creating {export_type} export...")
        print(f"📊 Records: {len(data)}")
        print(f"📝 Template: {payload['template']}")
        print(f"📁 Format: {payload['format']}")
        
        response = self.session.post(
            url, 
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            export_id = result.get('data', {}).get('export_id')
            print(f"✅ Export created: {export_id}")
            return result
        else:
            print(f"❌ Export creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    
    def poll_status(self, export_id, max_attempts=30, poll_interval=1):
        """
        Poll export status until completion
        
        Args:
            export_id: Export ID to check
            max_attempts: Maximum polling attempts
            poll_interval: Seconds between polls
            
        Returns:
            dict: Final status response
        """
        url = f"{self.base_url}/api/ybb/export/{export_id}/status"
        
        print(f"🔄 Polling status for export: {export_id}")
        
        for attempt in range(max_attempts):
            try:
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    status = response.json()
                    
                    print(f"📈 Status check {attempt + 1}/{max_attempts}: {status.get('status')}")
                    
                    if status.get('status') == 'success':
                        download_ready = status.get('download_info', {}).get('ready', True)
                        if download_ready:
                            print("✅ Export completed and ready for download!")
                            return status
                    elif status.get('status') == 'error':
                        print(f"❌ Export failed: {status.get('message')}")
                        return status
                    
                    # Still processing, wait and try again
                    if attempt < max_attempts - 1:
                        time.sleep(poll_interval)
                        
                elif response.status_code == 404:
                    print("❌ Export not found or expired")
                    return None
                else:
                    print(f"⚠️ Status check failed: {response.status_code}")
                    if attempt < max_attempts - 1:
                        time.sleep(poll_interval)
                        
            except Exception as e:
                print(f"⚠️ Status check error: {e}")
                if attempt < max_attempts - 1:
                    time.sleep(poll_interval)
        
        print(f"⏰ Timeout: Export still processing after {max_attempts} attempts")
        return None
    
    def download_export(self, export_id, file_type='single', save_path=None):
        """
        Download export file
        
        Args:
            export_id: Export ID to download
            file_type: 'single' or 'zip'
            save_path: Optional path to save file
            
        Returns:
            tuple: (success, filename, content)
        """
        url = f"{self.base_url}/api/ybb/export/{export_id}/download"
        
        if file_type != 'single':
            url += f"?type={file_type}"
        
        print(f"⬇️ Downloading export: {export_id}")
        
        try:
            response = self.session.get(url, timeout=60)
            
            if response.status_code == 200:
                # Get filename from headers
                content_disposition = response.headers.get('content-disposition', '')
                filename = 'export_file'
                
                if 'filename=' in content_disposition:
                    filename = content_disposition.split('filename=')[1].strip('"')
                
                content_type = response.headers.get('content-type', '')
                file_size = len(response.content)
                
                print(f"✅ Download successful!")
                print(f"📄 Filename: {filename}")
                print(f"📁 Content-Type: {content_type}")
                print(f"📊 Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
                
                # Save file if path provided
                if save_path:
                    full_path = f"{save_path}/{filename}" if save_path != filename else save_path
                    with open(full_path, 'wb') as f:
                        f.write(response.content)
                    print(f"💾 Saved as: {full_path}")
                
                return True, filename, response.content
                
            elif response.status_code == 404:
                print("❌ Export not found or expired")
                return False, None, None
            else:
                print(f"❌ Download failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False, None, None
                
        except Exception as e:
            print(f"❌ Download error: {e}")
            return False, None, None
    
    def complete_workflow(self, export_type, data, **kwargs):
        """
        Complete workflow: Create → Poll → Download
        
        Returns:
            tuple: (success, export_data, file_content)
        """
        print("🎯 Starting Complete Export Workflow")
        print("=" * 50)
        
        # Step 1: Create Export
        result = self.create_export(export_type, data, **kwargs)
        if not result:
            return False, None, None
        
        export_id = result.get('data', {}).get('export_id')
        if not export_id:
            print("❌ No export ID returned")
            return False, result, None
        
        print(f"\n📋 Export Details:")
        print(f"   ID: {export_id}")
        print(f"   Records: {result.get('data', {}).get('record_count')}")
        print(f"   Size: {result.get('data', {}).get('file_size_mb')} MB")
        print(f"   Processing: {result.get('performance_metrics', {}).get('processing_time_ms')} ms")
        
        # Step 2: Poll Status (for large exports, this might take time)
        print(f"\n🔄 Checking Export Status...")
        status = self.poll_status(export_id)
        if not status or status.get('status') != 'success':
            print("❌ Export did not complete successfully")
            return False, result, None
        
        # Step 3: Download File
        print(f"\n⬇️ Downloading File...")
        success, filename, content = self.download_export(
            export_id, 
            file_type=kwargs.get('download_type', 'single'),
            save_path=kwargs.get('save_path')
        )
        
        if success:
            print(f"\n🎉 Complete Workflow SUCCESS!")
            print(f"   ✅ Export created and processed")
            print(f"   ✅ File downloaded: {filename}")
            print(f"   ✅ Content size: {len(content):,} bytes")
            
            # Validate file if it's Excel
            if filename.endswith('.xlsx'):
                try:
                    from io import BytesIO
                    df = pd.read_excel(BytesIO(content))
                    print(f"   ✅ Excel validation: {len(df)} rows, {len(df.columns)} columns")
                except Exception as e:
                    print(f"   ⚠️ Excel validation failed: {e}")
            
            return True, result, content
        else:
            print(f"\n❌ Workflow failed at download step")
            return False, result, None

def demo_participants_export():
    """Demo: Export participants data"""
    
    # Sample participant data
    participants_data = [
        {
            "first_name": "John",
            "last_name": "Doe", 
            "email": "john.doe@example.com",
            "phone_number": "+1-555-0123",
            "passport_number": "A12345678",
            "country": "United States",
            "birth_date": "1990-05-15",
            "registration_date": "2024-01-15",
            "notes": "Demo participant with standard data"
        },
        {
            "first_name": "María",
            "last_name": "González",
            "email": "maria@example.com", 
            "phone_number": "+34-600-123-456",
            "passport_number": "ESP123456",
            "country": "Spain",
            "birth_date": "1988-12-03",
            "registration_date": "2024-01-20",
            "notes": "Unicode test: 🌟 ñáéíóú"
        },
        {
            "first_name": "田中",
            "last_name": "太郎",
            "email": "tanaka@example.jp",
            "phone_number": "+81-90-1234-5678", 
            "passport_number": "JP9876543",
            "country": "Japan",
            "birth_date": "1992-08-20",
            "registration_date": "2024-01-25",
            "notes": "Japanese characters test"
        },
        {
            "first_name": "Ahmed",
            "last_name": "Al-Rahman",
            "email": "ahmed@example.com",
            "phone_number": "+971-50-123-4567",
            "passport_number": "UAE789012", 
            "country": "United Arab Emirates",
            "birth_date": "1995-03-10",
            "registration_date": "2024-02-01",
            "notes": "Arabic name test"
        }
    ]
    
    client = YBBExportClient()
    
    # Test complete workflow
    success, export_data, file_content = client.complete_workflow(
        export_type='participants',
        data=participants_data,
        template='standard',
        format='excel',
        filename='demo_participants_export',
        save_path='.'
    )
    
    return success

def demo_status_polling_only():
    """Demo: Just status polling for an existing export"""
    
    # You can use this to check status of a previous export
    export_id = input("Enter export ID to check status: ")
    if not export_id:
        print("No export ID provided")
        return
    
    client = YBBExportClient()
    
    print(f"Checking status for export: {export_id}")
    status = client.poll_status(export_id, max_attempts=5)
    
    if status:
        print("\n📊 Final Status:")
        print(json.dumps(status, indent=2, default=str))
        
        if status.get('status') == 'success':
            # Offer to download
            download = input("Download file? (y/n): ")
            if download.lower() == 'y':
                success, filename, content = client.download_export(export_id, save_path='.')
                if success:
                    print(f"File saved: {filename}")

def main():
    """Main demo function"""
    print("🧪 YBB Export API Flow Demo")
    print("=" * 40)
    
    print("Available demos:")
    print("1. Complete participants export workflow")
    print("2. Status polling for existing export")
    print("3. Both")
    
    choice = input("Select demo (1-3): ").strip()
    
    if choice == '1' or choice == '3':
        print(f"\n{'='*60}")
        print("🎯 DEMO 1: Complete Participants Export Workflow")
        print("="*60)
        demo_participants_export()
    
    if choice == '2' or choice == '3':
        print(f"\n{'='*60}")
        print("🔍 DEMO 2: Status Polling for Existing Export")
        print("="*60)
        demo_status_polling_only()

if __name__ == "__main__":
    main()
