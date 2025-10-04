"""
Debug Query Builder Test
Test what SQL query is being generated
"""
import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_query_builder():
    try:
        from database.query_builder import YBBQueryBuilder
        
        query_builder = YBBQueryBuilder()
        
        print("🔍 Testing Query Builder...")
        
        # Test count query
        print("\n1. Count Query Test:")
        query, params = query_builder.build_count_query('participants', {})
        print(f"   Query: {query}")
        print(f"   Params: {params}")
        
        # Test with filters
        print("\n2. Count Query with Filters:")
        query, params = query_builder.build_count_query('participants', {'is_active': 1})
        print(f"   Query: {query}")
        print(f"   Params: {params}")
        
        # Test export query
        print("\n3. Export Query Test:")
        from config.ybb_export_config import get_template
        template = get_template('participants', 'summary')
        if template:
            query, params = query_builder.build_export_query(
                'participants', 
                template['fields'], 
                filters={},
                limit=5
            )
            print(f"   Template fields: {template['fields']}")
            print(f"   Query: {query}")
            print(f"   Params: {params}")
        
        # Test database execution
        print("\n4. Database Execution Test:")
        from database.db_connection import get_db_manager
        db_manager = get_db_manager()
        
        with db_manager.get_connection() as conn:
            from sqlalchemy import text
            
            # Test simple count
            result = conn.execute(text("SELECT COUNT(*) as count FROM participants"))
            count = result.fetchone()[0]
            print(f"   Direct count query result: {count}")
            
            # Test with our built query
            count_query, count_params = query_builder.build_count_query('participants', {})
            result = conn.execute(text(count_query), count_params)
            count = result.fetchone()[0]
            print(f"   Query builder count result: {count}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        print(f"   Full error: {traceback.format_exc()}")

if __name__ == "__main__":
    test_query_builder()