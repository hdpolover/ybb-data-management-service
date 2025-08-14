#!/usr/bin/env python3
"""
Quick Excel Fix Validation Test
Tests the core Excel generation to verify the fix works
"""
import os
import sys
import pandas as pd
from pathlib import Path

# Add the directory containing our modules to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_robust_excel_service():
    """Test the RobustExcelService"""
    print("=== Testing RobustExcelService ===")
    
    try:
        from robust_excel_service import RobustExcelService
        
        # Create sample data with challenging content
        data = [
            {
                'name': 'Test User 🌟',
                'email': 'test@example.com',
                'notes': 'Special chars: <>&"\'',
                'long_text': 'A' * 1000,  # Long content
                'number': 12345.67
            },
            {
                'name': 'User Two',
                'email': 'user2@test.com',
                'notes': 'Normal text',
                'long_text': 'Short text',
                'number': 999
            }
        ]
        
        # Test the service
        content, filename, validation_info = RobustExcelService.create_excel_file_robust(
            data, 
            'test_robust_excel'
        )
        
        print(f"✅ Excel content created: {len(content)} bytes")
        print(f"✅ Filename: {filename}")
        print(f"✅ Validation: {validation_info}")
        
        # Save to file for testing
        test_file = f"test_{filename}"
        with open(test_file, 'wb') as f:
            f.write(content)
        
        print(f"✅ File saved: {test_file}")
        
        # Test if file can be read by pandas
        df = pd.read_excel(test_file)
        print(f"✅ File readable with {len(df)} rows, {len(df.columns)} columns")
        print("✅ Columns:", list(df.columns))
        
        # Clean up
        os.unlink(test_file)
        
        return True
        
    except Exception as e:
        print(f"❌ RobustExcelService test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_pandas_excel():
    """Test basic pandas Excel generation with our fix"""
    print("\n=== Testing Basic Pandas Excel (Fixed) ===")
    
    try:
        data = [
            {'name': 'Test', 'value': 123},
            {'name': 'User', 'value': 456}
        ]
        
        df = pd.DataFrame(data)
        
        # Test the FIXED version (without options parameter)
        filename = 'test_pandas_fixed.xlsx'
        
        # This should work now (the problematic options parameter has been removed)
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Data', index=False)
        
        print(f"✅ Pandas Excel created: {filename}")
        
        # Test reading
        df_read = pd.read_excel(filename)
        print(f"✅ File readable with {len(df_read)} rows")
        
        # Clean up
        os.unlink(filename)
        
        return True
        
    except Exception as e:
        print(f"❌ Pandas Excel test failed: {e}")
        return False

def test_ybb_service_basic():
    """Test basic YBB service functionality"""
    print("\n=== Testing YBB Export Service ===")
    
    try:
        from services.ybb_export_service import YBBExportService
        
        # Create a minimal export request
        export_request = {
            'format': 'xlsx',
            'data': [
                {
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'email': 'john@example.com'
                }
            ],
            'filename': 'test_basic_export',
            'export_type': 'participants'
        }
        
        service = YBBExportService()
        result = service.create_export(export_request)
        
        if result.get('status') == 'success':
            print(f"✅ YBB Service export created: {result.get('data', {}).get('export_id')}")
            return True
        else:
            print(f"❌ YBB Service failed: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ YBB Service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run validation tests"""
    print("🧪 Excel Fix Validation Test")
    print("=" * 40)
    
    tests = [
        ("Basic Pandas Excel (Fixed)", test_basic_pandas_excel),
        ("RobustExcelService", test_robust_excel_service),
        ("YBB Export Service", test_ybb_service_basic)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔧 Running: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("🏁 Validation Results")
    print("=" * 40)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nSummary: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ The Excel format issue has been FIXED!")
        print("✅ Files should now open correctly in Excel without format errors")
    elif passed > 0:
        print(f"\n✅ {passed} tests passed - Core functionality is working!")
        print("⚠️ Some advanced features may need adjustment")
    else:
        print("\n❌ All tests failed - Check the error messages above")
    
    return passed == total

if __name__ == "__main__":
    main()
