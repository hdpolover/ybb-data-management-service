"""
Quick Database Query Test
Test actual table queries to see what's available
"""
import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_direct_query():
    try:
        import pymysql
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
        
        connection = pymysql.connect(**db_config)
        
        # Test different queries
        queries_to_test = [
            "SELECT COUNT(*) as count FROM participants",
            "SELECT COUNT(*) as count FROM participants WHERE is_deleted = 0",
            "SELECT COUNT(*) as count FROM participants WHERE is_deleted IS NULL OR is_deleted = 0",
            "SHOW COLUMNS FROM participants",
            "SELECT * FROM participants LIMIT 3"
        ]
        
        for i, query in enumerate(queries_to_test):
            print(f"\n🔍 Query {i+1}: {query}")
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    if "SHOW COLUMNS" in query:
                        columns = cursor.fetchall()
                        print(f"✅ Columns found: {len(columns)}")
                        for col in columns[:10]:  # Show first 10 columns
                            print(f"   - {col[0]} ({col[1]})")
                    elif "SELECT *" in query:
                        results = cursor.fetchall()
                        print(f"✅ Sample records found: {len(results)}")
                        if results:
                            print(f"   First record keys: {len(results[0]) if results[0] else 0} columns")
                    else:
                        result = cursor.fetchone()
                        count = result[0] if result else 0
                        print(f"✅ Count: {count}")
            except Exception as e:
                print(f"❌ Failed: {str(e)}")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")

if __name__ == "__main__":
    test_direct_query()