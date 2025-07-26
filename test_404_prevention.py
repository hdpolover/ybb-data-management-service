#!/usr/bin/env python3
"""
Test the improved cleanup system to prevent 404 errors
"""
import sys
import os
import time
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.ybb_export_service import YBBExportService

def test_export_availability():
    """Test that exports remain available after creation"""
    print("🧪 Testing Export Availability (404 Error Prevention)")
    print("=" * 60)
    
    service = YBBExportService()
    
    # Test data
    test_data = {
        'export_type': 'participants',
        'data': [
            {'id': 1, 'name': 'Test User 1', 'email': 'test1@example.com'},
            {'id': 2, 'name': 'Test User 2', 'email': 'test2@example.com'},
            {'id': 3, 'name': 'Test User 3', 'email': 'test3@example.com'}
        ],
        'filename': 'Test_Export_Availability.xlsx'
    }
    
    # Step 1: Create multiple exports
    print("\n📋 Step 1: Creating multiple exports...")
    export_ids = []
    
    for i in range(5):
        test_data['filename'] = f'Test_Export_{i+1}.xlsx'
        result = service.create_export(test_data)
        
        if result.get('status') == 'success':
            export_id = result.get('data', {}).get('export_id')
            if export_id:
                export_ids.append(export_id)
                print(f"✅ Created export {i+1}: {export_id}")
            else:
                print(f"❌ Export {i+1} created but no export_id returned: {result}")
        else:
            print(f"❌ Failed to create export {i+1}: {result.get('message')}")
    
    if not export_ids:
        print("❌ No exports were created successfully, aborting test")
        return False
    
    # Step 2: Verify all exports are downloadable
    print(f"\n🔍 Step 2: Verifying all {len(export_ids)} exports are downloadable...")
    available_exports = []
    
    for i, export_id in enumerate(export_ids):
        if not export_id:
            print(f"❌ Export {i+1}: Invalid export_id")
            continue
            
        try:
            file_content, filename = service.download_export(export_id)
            if file_content:
                available_exports.append(export_id)
                print(f"✅ Export {i+1} ({export_id[:8]}...): Available - {filename}")
            else:
                print(f"❌ Export {i+1} ({export_id[:8]}...): NOT FOUND (404 error would occur)")
        except Exception as e:
            print(f"❌ Export {i+1} ({export_id[:8]}...): Error - {str(e)}")
    
    # Step 3: Create additional exports to test cleanup behavior
    print(f"\n🔄 Step 3: Creating additional exports to test cleanup...")
    
    for i in range(3):
        test_data['filename'] = f'Additional_Export_{i+1}.xlsx'
        result = service.create_export(test_data)
        
        if result.get('status') == 'success':
            export_id = result.get('data', {}).get('export_id')
            if export_id:
                print(f"✅ Created additional export {i+1}: {export_id}")
            else:
                print(f"❌ Additional export {i+1} created but no export_id returned")
            
            # Small delay to ensure different timestamps
            time.sleep(1)
        else:
            print(f"❌ Failed to create additional export {i+1}")
    
    # Step 4: Check which exports are still available
    print(f"\n🔍 Step 4: Checking export availability after additional creation...")
    still_available = []
    
    for i, export_id in enumerate(export_ids):
        if not export_id:
            print(f"❌ Original export {i+1}: Invalid export_id")
            continue
            
        try:
            file_content, filename = service.download_export(export_id)
            if file_content:
                still_available.append(export_id)
                print(f"✅ Original export {i+1}: Still available")
            else:
                print(f"⚠️  Original export {i+1}: Cleaned up (would cause 404)")
        except Exception as e:
            print(f"❌ Original export {i+1}: Error - {str(e)}")
    
    # Step 5: Display cleanup configuration
    print(f"\n⚙️ Step 5: Current cleanup configuration:")
    print(f"   Max concurrent exports: {service.max_concurrent_exports}")
    print(f"   Cleanup on startup: {service.cleanup_on_startup}")
    print(f"   Cleanup on export: {service.cleanup_on_export}")
    print(f"   Cleanup interval: {getattr(service, 'cleanup_interval_minutes', 'N/A')} minutes")
    print(f"   Min export age: {getattr(service, 'min_export_age_minutes', 'N/A')} minutes")
    
    # Step 6: Storage information
    print(f"\n📊 Step 6: Current storage status:")
    storage_info = service.get_storage_info()
    print(f"   Total exports: {storage_info['total_exports']}")
    print(f"   Total files: {storage_info['total_files']}")
    print(f"   Storage used: {storage_info['total_size_mb']:.2f} MB")
    
    # Summary
    print(f"\n📋 Summary:")
    print(f"   ✅ Created exports: {len(export_ids)}")
    print(f"   ✅ Initially available: {len(available_exports)}")
    print(f"   ✅ Still available after cleanup: {len(still_available)}")
    print(f"   ⚠️  Cleaned up: {len(export_ids) - len(still_available)}")
    
    # Recommendations
    if len(still_available) >= 3:  # Keep at least 3 recent exports
        print(f"\n🎉 SUCCESS: Export availability looks good!")
        print(f"   Recent exports are being preserved, reducing 404 errors.")
    else:
        print(f"\n⚠️ WARNING: Too many exports were cleaned up!")
        print(f"   This could cause 404 errors in CodeIgniter application.")
        print(f"   Consider increasing max_concurrent_exports or min_export_age_minutes.")
    
    return len(still_available) >= 3

def test_time_based_cleanup():
    """Test that cleanup respects time intervals"""
    print(f"\n🕒 Testing Time-Based Cleanup...")
    
    service = YBBExportService()
    
    # Check if cleanup should run initially
    should_cleanup = service._should_run_cleanup()
    print(f"   Should run cleanup initially: {should_cleanup}")
    
    # Force a cleanup
    service._cleanup_old_exports()
    print(f"   Forced cleanup completed")
    
    # Check if cleanup should run immediately after
    should_cleanup_after = service._should_run_cleanup()
    print(f"   Should run cleanup immediately after: {should_cleanup_after}")
    
    if not should_cleanup_after:
        print(f"   ✅ Time-based cleanup is working correctly")
        return True
    else:
        print(f"   ⚠️ Time-based cleanup may not be working")
        return False

def main():
    """Run availability tests"""
    print("🚀 YBB Export Availability Tests (404 Error Prevention)")
    print("=" * 70)
    
    try:
        # Test export availability
        availability_ok = test_export_availability()
        
        # Test time-based cleanup
        time_based_ok = test_time_based_cleanup()
        
        print(f"\n" + "=" * 70)
        if availability_ok and time_based_ok:
            print("🎉 ALL TESTS PASSED: Export availability system is working!")
            print("   - Exports remain available after creation")
            print("   - Cleanup is less aggressive") 
            print("   - Time-based cleanup prevents excessive cleanup")
            print("   - 404 errors should be significantly reduced")
            return 0
        else:
            print("⚠️ SOME TESTS FAILED: Review cleanup configuration")
            return 1
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
