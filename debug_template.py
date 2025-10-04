"""
Debug Template Issue
Test template loading directly
"""
import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_template():
    try:
        from config.ybb_export_config import get_template, get_chunk_size, should_use_chunked_processing
        
        print("🔍 Testing Template Functions...")
        
        # Test template loading
        print("\n1. Testing get_template:")
        template = get_template('participants', 'summary')
        print(f"   Template type: {type(template)}")
        print(f"   Template content: {template}")
        
        if template:
            print(f"   Template fields: {template.get('fields', 'NOT FOUND')}")
            print(f"   Template headers: {template.get('headers', 'NOT FOUND')}")
        
        # Test chunk size
        print("\n2. Testing get_chunk_size:")
        try:
            chunk_size = get_chunk_size('participants', 'summary', 10000)
            print(f"   Chunk size result: {chunk_size}")
        except Exception as e:
            print(f"   ❌ Chunk size failed: {str(e)}")
            import traceback
            print(f"   Full error: {traceback.format_exc()}")
        
        # Test chunking decision
        print("\n3. Testing should_use_chunked_processing:")
        if template:
            try:
                should_chunk = should_use_chunked_processing(10000, template)
                print(f"   Should chunk (10k records): {should_chunk}")
            except Exception as e:
                print(f"   ❌ Chunking decision failed: {str(e)}")
        
    except Exception as e:
        print(f"❌ Template test failed: {str(e)}")
        import traceback
        print(f"   Full error: {traceback.format_exc()}")

if __name__ == "__main__":
    test_template()