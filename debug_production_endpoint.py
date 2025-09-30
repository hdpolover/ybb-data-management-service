#!/usr/bin/env python3
"""
Debug script to identify the 500 error in production endpoint
"""
import sys
import os
import traceback
import logging

# Add current directory to path
sys.path.insert(0, os.path.abspath('.'))

def test_imports():
    """Test all imports used by the YBB service"""
    print("Testing imports...")
    
    try:
        # Test Flask imports
        from flask import Flask, request, jsonify, send_file, g
        from flask_cors import CORS
        print("✅ Flask imports successful")
    except ImportError as e:
        print(f"❌ Flask import error: {e}")
        return False
    
    try:
        # Test pandas and related
        import pandas as pd
        import numpy as np
        print("✅ Pandas/NumPy imports successful")
    except ImportError as e:
        print(f"❌ Pandas import error: {e}")
        return False
    
    try:
        # Test openpyxl
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment
        print("✅ openpyxl imports successful")
    except ImportError as e:
        print(f"❌ openpyxl import error: {e}")
        return False
    
    try:
        # Test other standard libraries
        import uuid
        import time
        import tempfile
        import zipfile
        from io import BytesIO
        from datetime import datetime, timedelta
        print("✅ Standard library imports successful")
    except ImportError as e:
        print(f"❌ Standard library import error: {e}")
        return False
    
    try:
        # Test psutil (optional)
        import psutil
        print("✅ psutil import successful")
    except ImportError as e:
        print(f"⚠️  psutil import warning: {e} (optional dependency)")
    
    return True

def test_config_imports():
    """Test configuration imports"""
    print("\nTesting config imports...")
    
    try:
        from config import get_config
        config = get_config('production')
        print("✅ Main config import successful")
        print(f"   API_HOST: {config.API_HOST}")
        print(f"   API_PORT: {config.API_PORT}")
        print(f"   DEBUG: {config.DEBUG}")
    except Exception as e:
        print(f"❌ Main config import error: {e}")
        traceback.print_exc()
        return False
    
    try:
        from config.ybb_export_config import (
            EXPORT_TEMPLATES, STATUS_MAPPINGS, SYSTEM_CONFIG
        )
        print("✅ YBB export config import successful")
        print(f"   Templates available: {list(EXPORT_TEMPLATES.keys())}")
    except Exception as e:
        print(f"❌ YBB export config import error: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_service_imports():
    """Test service imports"""
    print("\nTesting service imports...")
    
    try:
        from utils.file_manager import ExportFileManager
        file_manager = ExportFileManager()
        print("✅ File manager import successful")
    except Exception as e:
        print(f"❌ File manager import error: {e}")
        traceback.print_exc()
        return False
    
    try:
        from services.ybb_export_service import YBBExportService
        export_service = YBBExportService()
        print("✅ YBB export service import successful")
    except Exception as e:
        print(f"❌ YBB export service import error: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_route_imports():
    """Test route imports"""
    print("\nTesting route imports...")
    
    try:
        from api.ybb_routes import ybb_bp
        print("✅ YBB routes import successful")
        print(f"   Blueprint name: {ybb_bp.name}")
        print(f"   URL prefix: {ybb_bp.url_prefix}")
    except Exception as e:
        print(f"❌ YBB routes import error: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_app_creation():
    """Test Flask app creation"""
    print("\nTesting Flask app creation...")
    
    try:
        # Set environment to production
        os.environ['FLASK_ENV'] = 'production'
        
        from app import create_app
        app = create_app()
        print("✅ Flask app creation successful")
        
        # Test if the route exists
        with app.test_client() as client:
            response = client.post('/api/ybb/export/participants', 
                                 json={"test": "data"},
                                 headers={'Content-Type': 'application/json'})
            print(f"   Test request status: {response.status_code}")
            print(f"   Test request response: {response.get_json()}")
        
        return True
    except Exception as e:
        print(f"❌ Flask app creation error: {e}")
        traceback.print_exc()
        return False

def test_service_functionality():
    """Test basic service functionality"""
    print("\nTesting basic service functionality...")
    
    try:
        from services.ybb_export_service import YBBExportService
        
        service = YBBExportService()
        
        # Test a simple export request
        test_data = {
            "export_type": "participants",
            "data": [
                {
                    "id": 1,
                    "full_name": "Test User",
                    "email": "test@example.com",
                    "nationality": "USA",
                    "institution": "Test University",
                    "phone_number": "+1234567890",
                    "category": "student",
                    "form_status": "approved",
                    "payment_status": "paid",
                    "created_at": "2025-01-01"
                }
            ],
            "template": "standard",
            "format": "excel"
        }
        
        result = service.create_export(test_data)
        print("✅ Export service functionality test successful")
        print(f"   Result status: {result.get('status')}")
        
        if result.get('status') == 'success':
            export_id = result.get('data', {}).get('export_id')
            print(f"   Export ID: {export_id}")
        
        return True
    except Exception as e:
        print(f"❌ Service functionality error: {e}")
        traceback.print_exc()
        return False

def main():
    """Main debug function"""
    print("=== YBB Production Endpoint Debug ===\n")
    
    # Set up basic logging
    logging.basicConfig(level=logging.DEBUG)
    
    success_count = 0
    total_tests = 6
    
    if test_imports():
        success_count += 1
    
    if test_config_imports():
        success_count += 1
    
    if test_service_imports():
        success_count += 1
    
    if test_route_imports():
        success_count += 1
        
    if test_app_creation():
        success_count += 1
        
    if test_service_functionality():
        success_count += 1
    
    print(f"\n=== Debug Summary ===")
    print(f"Tests passed: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("✅ All tests passed - the issue might be environment-specific")
        print("\nPossible causes for production 500 error:")
        print("1. Missing environment variables in deployment platform")
        print("2. Database connection issues (if using external DB)")
        print("3. Memory constraints in production")
        print("4. Different Python version in production")
        print("5. Missing system dependencies")
        
        print("\nRecommended actions:")
        print("1. Check deployment platform logs for detailed error messages")
        print("2. Verify all environment variables are set")
        print("3. Check memory usage and limits")
        print("4. Test with minimal payload first")
    else:
        print("❌ Some tests failed - fix these issues first")
    
    return success_count == total_tests

if __name__ == "__main__":
    main()
