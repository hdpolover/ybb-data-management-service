"""
Database Schema Explorer
Explore the actual database structure for participant export requirements
"""
import os
import sys
from dotenv import load_dotenv
import pymysql
import pandas as pd

# Load environment
load_dotenv()

def explore_tables():
    """Explore the relevant tables for participant export"""
    try:
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
        
        # Tables to examine based on specs
        tables_to_examine = [
            'users', 'participants', 'participant_essays', 'participant_statuses',
            'participant_subthemes', 'payments', 'program_payments', 'program_essays', 
            'program_subthemes', 'programs', 'participant_competition_categories', 
            'competition_categories'
        ]
        
        for table in tables_to_examine:
            print(f"\n{'='*60}")
            print(f"📋 TABLE: {table}")
            print(f"{'='*60}")
            
            try:
                with connection.cursor() as cursor:
                    # Get table structure
                    cursor.execute(f"DESCRIBE {table}")
                    columns = cursor.fetchall()
                    
                    print(f"Columns ({len(columns)}):")
                    for col in columns:
                        print(f"  {col[0]:<25} {col[1]:<30} {'NULL' if col[2] == 'YES' else 'NOT NULL':<10} {f'DEFAULT {col[4]}' if col[4] else ''}")
                    
                    # Get record count
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"\nTotal records: {count:,}")
                    
                    # Get sample data (first 3 records)
                    if count > 0:
                        cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                        sample_data = cursor.fetchall()
                        
                        if sample_data:
                            print(f"\nSample data (first record):")
                            col_names = [desc[0] for desc in cursor.description]
                            first_record = sample_data[0]
                            
                            for i, (col_name, value) in enumerate(zip(col_names, first_record)):
                                if i < 10:  # Show first 10 columns
                                    print(f"  {col_name}: {value}")
                            if len(col_names) > 10:
                                print(f"  ... and {len(col_names) - 10} more columns")
                    
            except Exception as e:
                print(f"❌ Error examining table {table}: {str(e)}")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")

def explore_relationships():
    """Explore key relationships for participant export"""
    try:
        db_config = {
            'host': os.environ.get('DB_HOST'),
            'port': int(os.environ.get('DB_PORT', 3306)),
            'user': os.environ.get('DB_USER'),
            'password': os.environ.get('DB_PASSWORD'),
            'database': os.environ.get('DB_NAME'),
            'charset': 'utf8mb4'
        }
        
        connection = pymysql.connect(**db_config)
        
        print(f"\n{'='*60}")
        print("🔗 KEY RELATIONSHIPS & DATA SAMPLES")
        print(f"{'='*60}")
        
        # Test queries based on specs
        test_queries = [
            ("Program IDs available", "SELECT DISTINCT program_id, COUNT(*) as participants FROM participants GROUP BY program_id LIMIT 10"),
            ("Category distribution", "SELECT category, COUNT(*) as count FROM participants GROUP BY category"),
            ("Form statuses", "SELECT status, COUNT(*) as count FROM participant_statuses GROUP BY status"),
            ("Payment statuses", "SELECT status, COUNT(*) as count FROM payments GROUP BY status"),
            ("Program payments", "SELECT id, program_id, name, amount FROM program_payments LIMIT 5"),
            ("Sample participant with user", """
                SELECT p.id, p.full_name, u.email, p.phone_number, p.country_code, p.category 
                FROM participants p 
                JOIN users u ON p.user_id = u.id 
                LIMIT 3
            """),
            ("Essays existence", "SELECT COUNT(DISTINCT participant_id) as participants_with_essays FROM participant_essays"),
            ("Subthemes connection", "SELECT COUNT(DISTINCT participant_id) as participants_with_subthemes FROM participant_subthemes"),
        ]
        
        for description, query in test_queries:
            print(f"\n📊 {description}:")
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    results = cursor.fetchall()
                    
                    if results:
                        col_names = [desc[0] for desc in cursor.description]
                        print(f"   Columns: {', '.join(col_names)}")
                        
                        for i, row in enumerate(results[:5]):  # Show first 5 results
                            print(f"   Row {i+1}: {row}")
                        
                        if len(results) > 5:
                            print(f"   ... and {len(results) - 5} more rows")
                    else:
                        print("   No results found")
                        
            except Exception as e:
                print(f"   ❌ Query failed: {str(e)}")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Relationships exploration failed: {str(e)}")

if __name__ == "__main__":
    print("🔍 Exploring Database Structure for Participant Export")
    print("=" * 80)
    
    explore_tables()
    explore_relationships()
    
    print(f"\n{'='*80}")
    print("✅ Database exploration completed!")
    print("=" * 80)