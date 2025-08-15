#!/usr/bin/env python3
"""
Test Railway deployment compatibility for Excel export
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tempfile
import pandas as pd

def test_railway_excel_compatibility():
    """Test Excel export in Railway-like environment"""
    
    print("🚂 Testing Railway Deployment Compatibility")
    print("=" * 50)
    
    # Simulate Railway environment constraints
    os.environ['FLASK_ENV'] = 'production'
    
    # Test data similar to production usage
    test_data = [
        {
            "id": 1,
            "full_name": "Railway Test User",
            "email": "railway@test.com",
            "form_status": "approved",
            "created_at": "2024-01-15 10:30:00"
        },
        {
            "id": 2,
            "full_name": "Production User",
            "email": "prod@test.com",
            "form_status": "pending",
            "created_at": "2024-01-16 14:20:00"
        }
    ]
    
    print("Testing Excel export with Railway constraints...")
    
    # Test each method individually to see which ones work
    methods_status = {}
    
    # Test Method 1: openpyxl manual
    print("\n1. Testing openpyxl manual method...")
    try:
        from utils.excel_exporter import ExcelExporter
        df = pd.DataFrame(test_data)
        df = ExcelExporter.sanitize_dataframe(df)
        
        output = ExcelExporter._create_with_openpyxl_manual(df, "Railway_Test", None)
        methods_status['openpyxl_manual'] = f"✅ Success ({len(output.getvalue())} bytes)"
        print(f"  ✅ openpyxl manual: Success")
    except Exception as e:
        methods_status['openpyxl_manual'] = f"❌ Failed: {str(e)}"
        print(f"  ❌ openpyxl manual: {str(e)}")
    
    # Test Method 2: pandas openpyxl
    print("\n2. Testing pandas with openpyxl engine...")
    try:
        output = ExcelExporter._create_with_pandas_openpyxl(df, "Railway_Test", None)
        methods_status['pandas_openpyxl'] = f"✅ Success ({len(output.getvalue())} bytes)"
        print(f"  ✅ pandas openpyxl: Success")
    except Exception as e:
        methods_status['pandas_openpyxl'] = f"❌ Failed: {str(e)}"
        print(f"  ❌ pandas openpyxl: {str(e)}")
    
    # Test Method 3: xlsxwriter (may not be available)
    print("\n3. Testing xlsxwriter engine...")
    try:
        output = ExcelExporter._create_with_xlsxwriter(df, "Railway_Test", None)
        methods_status['xlsxwriter'] = f"✅ Success ({len(output.getvalue())} bytes)"
        print(f"  ✅ xlsxwriter: Success")
    except Exception as e:
        methods_status['xlsxwriter'] = f"⚠️  Expected failure: {str(e)}"
        print(f"  ⚠️  xlsxwriter: {str(e)} (expected in minimal env)")
    
    # Test the main create_excel_file method
    print("\n4. Testing main create_excel_file method...")
    try:
        excel_output = ExcelExporter.create_excel_file(
            data=test_data,
            filename="railway_test.xlsx",
            sheet_name="Railway Data"
        )
        
        content = excel_output.getvalue()
        methods_status['main_method'] = f"✅ Success ({len(content)} bytes)"
        print(f"  ✅ Main method: Success ({len(content)} bytes)")
        
        # Verify file integrity
        if content.startswith(b'PK'):
            print(f"  ✅ File has correct Excel signature")
        else:
            print(f"  ❌ File has incorrect signature")
            
        # Save test file for verification
        test_file = "d:\\Work\\ybb-data-management-web-flask\\temp\\railway_test.xlsx"
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        
        with open(test_file, 'wb') as f:
            f.write(content)
        print(f"  📁 Test file saved: {test_file}")
        
        # Quick pandas verification
        df_test = pd.read_excel(test_file)
        print(f"  ✅ File verification: {df_test.shape}")
        
    except Exception as e:
        methods_status['main_method'] = f"❌ Failed: {str(e)}"
        print(f"  ❌ Main method failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return methods_status

def test_minimal_requirements():
    """Test with minimal requirements (simulating Railway fallback)"""
    
    print("\n📦 Testing Minimal Requirements Scenario")
    print("=" * 50)
    
    # Temporarily "hide" xlsxwriter to simulate minimal environment
    original_modules = sys.modules.copy()
    
    # Remove xlsxwriter from sys.modules if it exists
    if 'xlsxwriter' in sys.modules:
        del sys.modules['xlsxwriter']
    
    try:
        # Try import xlsxwriter - should fail in minimal env
        try:
            import xlsxwriter
            print("⚠️ xlsxwriter is available (not a minimal environment)")
        except ImportError:
            print("✅ xlsxwriter not available (simulating minimal environment)")
        
        # Test Excel creation in this scenario
        test_data = [{"id": 1, "name": "Minimal Test"}]
        
        from utils.excel_exporter import ExcelExporter
        excel_output = ExcelExporter.create_excel_file(
            data=test_data,
            sheet_name="Minimal"
        )
        
        content = excel_output.getvalue()
        print(f"✅ Excel creation successful in minimal env: {len(content)} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Minimal environment test failed: {str(e)}")
        return False
    finally:
        # Restore original modules
        sys.modules.clear()
        sys.modules.update(original_modules)

def test_production_app_compatibility():
    """Test compatibility with app_complete.py (Railway's entry point)"""
    
    print("\n🏭 Testing Production App Compatibility")
    print("=" * 50)
    
    try:
        # Check if the production app can be imported
        import app_complete
        print("✅ app_complete.py can be imported")
        
        # Check if our utils are accessible from the production app
        from utils.excel_exporter import ExcelExporter
        print("✅ ExcelExporter can be imported from production context")
        
        return True
    except Exception as e:
        print(f"❌ Production app compatibility issue: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Railway Deployment Excel Export Test")
    print("=" * 60)
    
    # Test 1: Method compatibility
    methods_status = test_railway_excel_compatibility()
    
    # Test 2: Minimal requirements
    minimal_ok = test_minimal_requirements()
    
    # Test 3: Production app
    prod_ok = test_production_app_compatibility()
    
    print("\n" + "=" * 60)
    print("📊 Railway Compatibility Results:")
    
    print("\n🔧 Excel Creation Methods:")
    for method, status in methods_status.items():
        print(f"  {method}: {status}")
    
    print(f"\n📦 Minimal Environment: {'✅ PASS' if minimal_ok else '❌ FAIL'}")
    print(f"🏭 Production App: {'✅ PASS' if prod_ok else '❌ FAIL'}")
    
    # Overall assessment
    working_methods = sum(1 for status in methods_status.values() if "✅" in status)
    
    if working_methods >= 2 and minimal_ok and prod_ok:
        print("\n🎉 Railway deployment should work correctly!")
        print("✅ Multiple Excel creation methods available")
        print("✅ Graceful fallback for missing dependencies")
        print("✅ Production app compatibility confirmed")
    elif working_methods >= 1:
        print("\n⚠️  Railway deployment should work with limitations")
        print(f"⚠️  {working_methods} method(s) available")
        print("💡 Consider updating requirements_complete.txt if needed")
    else:
        print("\n❌ Railway deployment may have issues")
        print("🚨 No working Excel creation methods found")
        print("💡 Check dependencies and requirements files")
    
    print("\n🚀 Next Steps for Railway Deployment:")
    print("1. Commit the updated requirements_complete.txt")
    print("2. Deploy to Railway")
    print("3. Test the /api/ybb/export endpoints")
    print("4. Monitor logs for any method fallbacks")
