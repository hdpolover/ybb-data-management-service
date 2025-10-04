"""
Debug Database Export Service
Test the actual database export service to see where it's failing
"""
import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_export_service():
    try:
        from services.db_export_service import DatabaseExportService
        
        print("🔍 Testing Database Export Service...")
        
        # Create service
        service = DatabaseExportService()
        print("✅ Service initialized")
        
        # Test record count method
        print("\n1. Testing get_export_record_count:")
        try:
            count = service.get_export_record_count('participants', {})
            print(f"   Count result: {count}")
        except Exception as e:
            print(f"   ❌ Count failed: {str(e)}")
            import traceback
            print(f"   Full error: {traceback.format_exc()}")
        
        # Test with filters
        print("\n2. Testing with filters:")
        try:
            count = service.get_export_record_count('participants', {'is_active': 1})
            print(f"   Count with filter result: {count}")
        except Exception as e:
            print(f"   ❌ Count with filter failed: {str(e)}")
        
        # Test preview method
        print("\n3. Testing get_export_preview:")
        try:
            preview = service.get_export_preview('participants', 'summary', {}, limit=3)
            print(f"   Preview result count: {len(preview)}")
            if preview:
                print(f"   First record keys: {list(preview[0].keys())}")
                print(f"   First record sample: {preview[0]}")
        except Exception as e:
            print(f"   ❌ Preview failed: {str(e)}")
            import traceback
            print(f"   Full error: {traceback.format_exc()}")
        
    except Exception as e:
        print(f"❌ Service test failed: {str(e)}")
        import traceback
        print(f"   Full error: {traceback.format_exc()}")

if __name__ == "__main__":
    test_export_service()