"""
Database Connection Test Script
Tests the database connection using the credentials from .env file
"""
import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_connection():
    """Test basic database connection without SQLAlchemy"""
    print("🔍 Testing basic database connection...")
    
    try:
        import pymysql
        
        # Get database config from environment
        db_config = {
            'host': os.environ.get('DB_HOST', 'localhost'),
            'port': int(os.environ.get('DB_PORT', 3306)),
            'user': os.environ.get('DB_USER', 'root'),
            'password': os.environ.get('DB_PASSWORD', ''),
            'database': os.environ.get('DB_NAME', 'ybb_data_management'),
            'charset': 'utf8mb4'
        }
        
        print(f"   Host: {db_config['host']}")
        print(f"   Port: {db_config['port']}")
        print(f"   User: {db_config['user']}")
        print(f"   Database: {db_config['database']}")
        print(f"   Password: {'*' * len(db_config['password']) if db_config['password'] else 'Not set'}")
        
        # Test connection
        connection = pymysql.connect(**db_config)
        
        with connection.cursor() as cursor:
            # Test basic query (simplified for compatibility)
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            
            print(f"✅ Connection successful!")
            print(f"   Test query result: {result[0]}")
            
            # Test additional queries separately 
            cursor.execute("SELECT NOW() as server_time")
            time_result = cursor.fetchone()
            print(f"   Server time: {time_result[0]}")
            
            cursor.execute("SELECT DATABASE() as current_db")
            db_result = cursor.fetchone()
            print(f"   Current database: {db_result[0]}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Basic connection failed: {str(e)}")
        return False

def test_sqlalchemy_connection():
    """Test SQLAlchemy connection with connection pooling"""
    print("\n🔍 Testing SQLAlchemy connection...")
    
    try:
        from sqlalchemy import create_engine, text
        import pandas as pd
        
        # Get database config
        db_config = {
            'host': os.environ.get('DB_HOST', 'localhost'),
            'port': int(os.environ.get('DB_PORT', 3306)),
            'user': os.environ.get('DB_USER', 'root'),
            'password': os.environ.get('DB_PASSWORD', ''),
            'database': os.environ.get('DB_NAME', 'ybb_data_management'),
            'charset': 'utf8mb4'
        }
        
        # Create connection string
        connection_string = (
            f"mysql+pymysql://{db_config['user']}:{db_config['password']}@"
            f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
            f"?charset={db_config['charset']}"
        )
        
        # Create engine
        engine = create_engine(
            connection_string,
            pool_size=2,
            max_overflow=3,
            pool_timeout=30,
            echo=False  # Set to True to see SQL queries
        )
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT VERSION() as version, @@sql_mode as sql_mode"))
            row = result.fetchone()
            
            print(f"✅ SQLAlchemy connection successful!")
            print(f"   MySQL version: {row[0]}")
            print(f"   SQL mode: {row[1]}")
        
        # Test pandas integration
        print("\n🔍 Testing pandas integration...")
        df = pd.read_sql("SELECT 'test' as message, NOW() as timestamp", engine)
        print(f"✅ Pandas integration successful!")
        print(f"   Pandas result: {df.iloc[0]['message']}")
        print(f"   Timestamp: {df.iloc[0]['timestamp']}")
        
        return True
        
    except Exception as e:
        print(f"❌ SQLAlchemy connection failed: {str(e)}")
        return False

def test_table_access():
    """Test access to actual database tables"""
    print("\n🔍 Testing table access...")
    
    try:
        from sqlalchemy import create_engine, text
        import pandas as pd
        
        # Database connection
        db_config = {
            'host': os.environ.get('DB_HOST'),
            'port': int(os.environ.get('DB_PORT', 3306)),
            'user': os.environ.get('DB_USER'),
            'password': os.environ.get('DB_PASSWORD'),
            'database': os.environ.get('DB_NAME'),
            'charset': 'utf8mb4'
        }
        
        connection_string = (
            f"mysql+pymysql://{db_config['user']}:{db_config['password']}@"
            f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
            f"?charset={db_config['charset']}"
        )
        
        engine = create_engine(connection_string, echo=False)
        
        # Check available tables
        with engine.connect() as conn:
            tables_result = conn.execute(text("SHOW TABLES"))
            tables = [row[0] for row in tables_result.fetchall()]
            
            print(f"✅ Found {len(tables)} tables in database:")
            for table in tables[:10]:  # Show first 10 tables
                print(f"   - {table}")
            if len(tables) > 10:
                print(f"   ... and {len(tables) - 10} more tables")
        
        # Test specific table queries if participants table exists
        common_tables = ['participants', 'users', 'payments', 'ambassadors']
        for table_name in common_tables:
            if table_name in tables:
                try:
                    with engine.connect() as conn:
                        count_result = conn.execute(text(f"SELECT COUNT(*) as count FROM {table_name}"))
                        count = count_result.fetchone()[0]
                        print(f"✅ Table '{table_name}': {count} records")
                        
                        # Get a sample record
                        sample_result = conn.execute(text(f"SELECT * FROM {table_name} LIMIT 1"))
                        columns = sample_result.keys()
                        print(f"   Columns ({len(columns)}): {', '.join(list(columns)[:5])}{'...' if len(columns) > 5 else ''}")
                        
                except Exception as table_error:
                    print(f"⚠️ Could not query table '{table_name}': {str(table_error)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Table access test failed: {str(e)}")
        return False

def test_database_integration():
    """Test the actual database integration classes"""
    print("\n🔍 Testing database integration classes...")
    
    try:
        # Import our database classes
        from database.db_connection import DatabaseManager
        from database.query_builder import YBBQueryBuilder
        
        print("✅ Database classes imported successfully")
        
        # Test DatabaseManager
        db_manager = DatabaseManager()
        print("✅ DatabaseManager initialized")
        
        # Test connection
        from sqlalchemy import text
        with db_manager.get_connection() as conn:
            result = conn.execute(text("SELECT 'Database integration working!' as message"))
            message = result.fetchone()[0]
            print(f"✅ DatabaseManager connection test: {message}")
        
        # Test QueryBuilder
        query_builder = YBBQueryBuilder()
        print("✅ QueryBuilder initialized")
        
        # Test query building
        query, params = query_builder.build_count_query('participants', {'is_active': 1})
        print(f"✅ Query builder test successful")
        print(f"   Sample query: {query}")
        print(f"   Sample params: {params}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database integration test failed: {str(e)}")
        import traceback
        print(f"   Full error: {traceback.format_exc()}")
        return False

def main():
    """Run all database tests"""
    print("=" * 60)
    print(f"🔍 YBB Database Connection Test - {datetime.now()}")
    print("=" * 60)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    test_results = []
    
    # Run tests
    test_results.append(("Basic Connection", test_basic_connection()))
    test_results.append(("SQLAlchemy Connection", test_sqlalchemy_connection()))
    test_results.append(("Table Access", test_table_access()))
    test_results.append(("Database Integration", test_database_integration()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nResult: {passed}/{len(test_results)} tests passed")
    
    if passed == len(test_results):
        print("🎉 All tests passed! Database integration is ready to use.")
    else:
        print("⚠️ Some tests failed. Check the error messages above.")
    
    return passed == len(test_results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)