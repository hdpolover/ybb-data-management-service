#!/usr/bin/env python3
"""
Railway Production Startup Script
Simplified startup for Railway deployment with comprehensive logging
"""
import os
import sys
import time

# Set environment early
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_APP', 'app.py')

def log_startup_info():
    """Log startup information"""
    print("="*60)
    print("YBB DATA MANAGEMENT SERVICE - RAILWAY STARTUP")
    print("="*60)
    print(f"Python: {sys.version}")
    print(f"Working Dir: {os.getcwd()}")
    print(f"Port: {os.environ.get('PORT', 'NOT_SET')}")
    print(f"Environment: {os.environ.get('FLASK_ENV', 'unknown')}")
    print("="*60)

def test_critical_imports():
    """Test critical imports"""
    print("Testing critical imports...")
    try:
        import pandas
        print("✓ pandas imported")
        import numpy  
        print("✓ numpy imported")
        import openpyxl
        print("✓ openpyxl imported")
        import flask
        print("✓ flask imported")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def create_and_test_app():
    """Create Flask app and test it"""
    print("Creating Flask application...")
    try:
        # Add current dir to path
        sys.path.insert(0, os.getcwd())
        
        from app import create_app
        app = create_app()
        print("✓ Flask app created successfully")
        
        # Test health route
        with app.app_context():
            rules = [str(rule) for rule in app.url_map.iter_rules()]
            health_found = any('/health' in rule for rule in rules)
            export_found = any('/api/ybb/export' in rule for rule in rules)
            
            print(f"✓ Total routes: {len(rules)}")
            print(f"✓ Health endpoint: {'Found' if health_found else 'Missing'}")
            print(f"✓ Export endpoints: {'Found' if export_found else 'Missing'}")
        
        return app
        
    except Exception as e:
        print(f"✗ App creation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main startup function"""
    log_startup_info()
    
    # Test imports
    if not test_critical_imports():
        print("CRITICAL: Dependency test failed!")
        sys.exit(1)
    
    # Create and test app
    app = create_and_test_app()
    if not app:
        print("CRITICAL: App creation failed!")
        sys.exit(1)
    
    print("="*60)
    print("APPLICATION READY - Starting server...")
    print("="*60)
    
    # Start server with Flask's development server for Railway
    port = int(os.environ.get('PORT', 5000))
    
    try:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            threaded=True
        )
    except Exception as e:
        print(f"Server startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
