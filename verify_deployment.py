#!/usr/bin/env python3
"""
Railway Deployment Verification
Quick verification that all components are working for YBB service
"""
import sys
import os
import requests
import json
from datetime import datetime

def test_pandas_available():
    """Quick test that pandas is available"""
    try:
        import pandas as pd
        import numpy as np
        
        # Quick functionality test
        df = pd.DataFrame({'test': [1, 2, 3, 4, 5]})
        result = df['test'].sum()
        
        print(f"✅ pandas {pd.__version__} - Basic test passed (sum={result})")
        return True
    except Exception as e:
        print(f"❌ pandas test failed: {e}")
        return False

def test_excel_functionality():
    """Test Excel export/import"""
    try:
        import pandas as pd
        from io import BytesIO
        
        # Create test data
        test_data = {
            'participant_id': ['YBB001', 'YBB002', 'YBB003'],
            'name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
            'email': ['john@test.com', 'jane@test.com', 'bob@test.com'],
            'status': ['approved', 'pending', 'approved']
        }
        
        df = pd.DataFrame(test_data)
        
        # Test Excel export
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Participants', index=False)
        
        # Test Excel import
        buffer.seek(0)
        imported_df = pd.read_excel(buffer, sheet_name='Participants', engine='openpyxl')
        
        if len(imported_df) == len(df):
            print(f"✅ Excel functionality - Export/import test passed ({len(df)} rows)")
            return True
        else:
            print(f"❌ Excel functionality - Row count mismatch: {len(df)} vs {len(imported_df)}")
            return False
            
    except Exception as e:
        print(f"❌ Excel functionality test failed: {e}")
        return False

def test_flask_app():
    """Test that Flask app can be imported and configured"""
    try:
        from app import create_app
        
        app = create_app()
        
        # Test health endpoint
        with app.test_client() as client:
            response = client.get('/health')
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ Flask app - Health endpoint working (status: {data.get('status', 'unknown')})")
                return True
            else:
                print(f"❌ Flask app - Health endpoint returned {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def test_export_endpoints():
    """Test that export endpoints are available (basic route check)"""
    try:
        from app import create_app
        
        app = create_app()
        
        # Check if export routes exist
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        
        required_routes = [
            '/api/ybb/export/participants',
            '/health'
        ]
        
        found_routes = 0
        for required in required_routes:
            if any(required in route for route in routes):
                found_routes += 1
                print(f"✅ Route found: {required}")
            else:
                print(f"❌ Route missing: {required}")
        
        if found_routes == len(required_routes):
            print(f"✅ Export endpoints - All {found_routes} required routes available")
            return True
        else:
            print(f"❌ Export endpoints - Only {found_routes}/{len(required_routes)} routes found")
            return False
            
    except Exception as e:
        print(f"❌ Export endpoints test failed: {e}")
        return False

def main():
    """Run deployment verification"""
    print("="*60)
    print("RAILWAY DEPLOYMENT VERIFICATION")
    print(f"YBB Data Management Service - {datetime.now()}")
    print("="*60)
    
    tests = [
        ("Pandas Available", test_pandas_available),
        ("Excel Functionality", test_excel_functionality),
        ("Flask App", test_flask_app),
        ("Export Endpoints", test_export_endpoints)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        try:
            if test_func():
                passed += 1
            else:
                print(f"   Test failed")
        except Exception as e:
            print(f"   Test error: {e}")
    
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASS" if i < passed else "❌ FAIL"
        print(f"{status} | {test_name}")
    
    print(f"\nOVERALL: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Service is ready for production.")
        print("✅ pandas working")
        print("✅ Excel export/import working")
        print("✅ Flask app working")
        print("✅ Export endpoints available")
        return True
    else:
        print("⚠️  SOME TESTS FAILED! Check configuration.")
        return False

if __name__ == '__main__':
    success = main()
    print(f"\n{'='*60}")
    if success:
        print("🚀 DEPLOYMENT VERIFICATION PASSED")
    else:
        print("💥 DEPLOYMENT VERIFICATION FAILED")
    print("="*60)
    
    sys.exit(0 if success else 1)