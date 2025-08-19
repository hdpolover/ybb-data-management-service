#!/usr/bin/env python3
"""
Pandas Installation Test for Railway
Tests all pandas functionality needed for the YBB data management service
"""
import sys
import os
from io import BytesIO
import json

def test_pandas_basic():
    """Test basic pandas functionality"""
    print("🔍 Testing basic pandas functionality...")
    
    try:
        import pandas as pd
        print(f"✅ pandas {pd.__version__} imported successfully")
        
        # Test DataFrame creation
        test_data = {
            'name': ['John', 'Jane', 'Bob', 'Alice'],
            'age': [25, 30, 35, 28],
            'email': ['john@test.com', 'jane@test.com', 'bob@test.com', 'alice@test.com']
        }
        
        df = pd.DataFrame(test_data)
        print(f"✅ DataFrame created: {len(df)} rows, {len(df.columns)} columns")
        
        # Test basic operations
        avg_age = df['age'].mean()
        print(f"✅ Basic operations: Average age = {avg_age}")
        
        # Test filtering
        filtered_df = df[df['age'] > 28]
        print(f"✅ Filtering: {len(filtered_df)} records with age > 28")
        
        return True, df
        
    except Exception as e:
        print(f"❌ Basic pandas test failed: {e}")
        return False, None

def test_excel_functionality(df):
    """Test Excel read/write functionality"""
    print("\n🔍 Testing Excel functionality...")
    
    try:
        import pandas as pd
        
        # Test Excel writing
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='TestData', index=False)
            
            # Add a second sheet
            summary_data = pd.DataFrame({
                'metric': ['total_records', 'avg_age', 'unique_names'],
                'value': [len(df), df['age'].mean(), df['name'].nunique()]
            })
            summary_data.to_excel(writer, sheet_name='Summary', index=False)
        
        buffer.seek(0)
        print(f"✅ Excel file written: {len(buffer.getvalue())} bytes")
        
        # Test Excel reading
        read_df = pd.read_excel(buffer, sheet_name='TestData', engine='openpyxl')
        print(f"✅ Excel file read: {len(read_df)} rows recovered")
        
        # Verify data integrity
        if read_df.equals(df):
            print("✅ Data integrity verified: Original and read data match")
        else:
            print("⚠️  Data integrity issue: Some differences found")
            
        # Test reading specific sheet
        buffer.seek(0)
        summary_df = pd.read_excel(buffer, sheet_name='Summary', engine='openpyxl')
        print(f"✅ Summary sheet read: {len(summary_df)} metrics")
        
        return True
        
    except Exception as e:
        print(f"❌ Excel functionality test failed: {e}")
        return False

def test_large_dataset():
    """Test handling of larger datasets"""
    print("\n🔍 Testing large dataset handling...")
    
    try:
        import pandas as pd
        import numpy as np
        
        # Create a larger test dataset (simulating YBB participant data)
        np.random.seed(42)
        size = 1000
        
        large_data = {
            'participant_id': [f"YBB2025_{i:04d}" for i in range(1, size + 1)],
            'full_name': [f"Participant {i}" for i in range(1, size + 1)],
            'email': [f"participant{i}@example.com" for i in range(1, size + 1)],
            'country': np.random.choice(['Indonesia', 'Malaysia', 'Singapore', 'Thailand', 'Vietnam'], size),
            'age': np.random.randint(18, 30, size),
            'university': [f"University {i % 50}" for i in range(size)],
            'gpa': np.round(np.random.uniform(2.5, 4.0, size), 2),
            'registration_date': pd.date_range('2025-01-01', periods=size, freq='H'),
            'status': np.random.choice(['approved', 'pending', 'rejected'], size, p=[0.7, 0.2, 0.1])
        }
        
        large_df = pd.DataFrame(large_data)
        print(f"✅ Large dataset created: {len(large_df)} rows, {len(large_df.columns)} columns")
        
        # Test grouping and aggregation
        country_stats = large_df.groupby('country').agg({
            'age': ['mean', 'min', 'max'],
            'gpa': 'mean',
            'participant_id': 'count'
        }).round(2)
        print(f"✅ Grouping and aggregation: {len(country_stats)} countries analyzed")
        
        # Test filtering and sorting
        top_performers = large_df[large_df['gpa'] > 3.5].sort_values('gpa', ascending=False).head(10)
        print(f"✅ Filtering and sorting: {len(top_performers)} top performers identified")
        
        # Test Excel export with large dataset
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            large_df.to_excel(writer, sheet_name='Participants', index=False)
            country_stats.to_excel(writer, sheet_name='CountryStats')
            top_performers.to_excel(writer, sheet_name='TopPerformers', index=False)
        
        buffer.seek(0)
        file_size = len(buffer.getvalue())
        print(f"✅ Large Excel export: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
        
        # Verify we can read it back
        read_large_df = pd.read_excel(buffer, sheet_name='Participants', engine='openpyxl')
        print(f"✅ Large Excel import: {len(read_large_df)} rows read back")
        
        return True
        
    except Exception as e:
        print(f"❌ Large dataset test failed: {e}")
        return False

def test_json_integration():
    """Test JSON data processing (common in API workflows)"""
    print("\n🔍 Testing JSON integration...")
    
    try:
        import pandas as pd
        
        # Simulate API response data
        api_response = {
            "status": "success",
            "data": [
                {"id": 1, "name": "John Doe", "email": "john@example.com", "scores": [85, 90, 88]},
                {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "scores": [92, 87, 95]},
                {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "scores": [78, 82, 80]}
            ],
            "metadata": {"total": 3, "page": 1}
        }
        
        # Convert to DataFrame
        df = pd.DataFrame(api_response['data'])
        print(f"✅ JSON to DataFrame: {len(df)} records converted")
        
        # Handle nested data (scores array)
        df['avg_score'] = df['scores'].apply(lambda x: sum(x) / len(x))
        df['max_score'] = df['scores'].apply(max)
        df['min_score'] = df['scores'].apply(min)
        
        print(f"✅ Nested data processing: Average scores calculated")
        
        # Convert back to JSON format
        result_json = df.drop('scores', axis=1).to_json(orient='records')
        result_data = json.loads(result_json)
        print(f"✅ DataFrame to JSON: {len(result_data)} records exported")
        
        return True
        
    except Exception as e:
        print(f"❌ JSON integration test failed: {e}")
        return False

def main():
    """Run all pandas tests"""
    print("="*60)
    print("PANDAS INSTALLATION TEST FOR RAILWAY")
    print("YBB Data Management Service")
    print("="*60)
    
    # Test results
    test_results = []
    
    # Basic functionality test
    basic_ok, test_df = test_pandas_basic()
    test_results.append(("Basic Functionality", basic_ok))
    
    if basic_ok and test_df is not None:
        # Excel functionality test
        excel_ok = test_excel_functionality(test_df)
        test_results.append(("Excel Functionality", excel_ok))
        
        # Large dataset test
        large_ok = test_large_dataset()
        test_results.append(("Large Dataset Handling", large_ok))
        
        # JSON integration test
        json_ok = test_json_integration()
        test_results.append(("JSON Integration", json_ok))
    else:
        print("\n⚠️  Skipping advanced tests due to basic functionality failure")
        test_results.extend([
            ("Excel Functionality", False),
            ("Large Dataset Handling", False),
            ("JSON Integration", False)
        ])
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} | {test_name}")
    
    print(f"\nOVERALL: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Pandas is fully functional for YBB service.")
        return True
    elif passed_tests > 0:
        print("⚠️  PARTIAL SUCCESS: Some pandas functionality available.")
        return False
    else:
        print("💥 ALL TESTS FAILED! Pandas is not properly installed.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)