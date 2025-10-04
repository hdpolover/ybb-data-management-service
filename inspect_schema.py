"""
Database Schema Inspector
Checks the actual database schema to match our query builder
"""
import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

def inspect_schema():
    try:
        import pymysql
        
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
        
        tables_to_check = ['participants', 'payments', 'ambassadors', 'users']
        
        for table_name in tables_to_check:
            print(f"\n📋 TABLE: {table_name}")
            print("=" * 50)
            
            try:
                with connection.cursor() as cursor:
                    # Get column information
                    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
                    columns = cursor.fetchall()
                    
                    print(f"Total columns: {len(columns)}")
                    print("\nColumn details:")
                    for col in columns:
                        col_name = col[0]
                        col_type = col[1]
                        nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                        default = f"DEFAULT {col[4]}" if col[4] else ""
                        print(f"  {col_name:<25} {col_type:<20} {nullable} {default}")
                    
                    # Get record count
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"\nTotal records: {count:,}")
                    
                    # Check for common fields we expect
                    column_names = [col[0] for col in columns]
                    expected_fields = ['is_deleted', 'is_active', 'created_at', 'updated_at', 
                                     'form_status', 'payment_status']
                    
                    print(f"\nExpected fields check:")
                    for field in expected_fields:
                        status = "✅" if field in column_names else "❌"
                        print(f"  {status} {field}")
                    
            except Exception as e:
                print(f"❌ Error checking {table_name}: {str(e)}")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")

if __name__ == "__main__":
    inspect_schema()