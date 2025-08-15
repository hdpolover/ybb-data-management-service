#!/usr/bin/env python3
"""
Production WSGI startup script for YBB Data Management Service
Ensures complete application with all dependencies loads properly
"""
import os
import sys

# Set production environment variables if not already set
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_APP', 'app.py')

# Ensure Python can find our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_application():
    """Create and return the complete Flask application"""
    try:
        print("=== YBB Data Management Service - Complete Mode ===")
        print(f"Python version: {sys.version}")
        print(f"Working directory: {os.getcwd()}")
        print(f"Environment: {os.environ.get('FLASK_ENV', 'unknown')}")
        print(f"Port: {os.environ.get('PORT', '5000')}")
        
        # Test critical dependencies first
        try:
            import pandas as pd
            import numpy as np
            import openpyxl
            print("SUCCESS: Core data dependencies loaded (pandas, numpy, openpyxl)")
        except ImportError as e:
            print(f"ERROR: Critical dependency missing: {e}")
            raise e
        
        # Import the complete Flask application
        from app import app
        
        print("SUCCESS: Complete YBB application loaded successfully")
        print(f"Debug mode: {app.config.get('DEBUG', False)}")
        print(f"Registered blueprints: {list(app.blueprints.keys())}")
        
        # Test that critical routes are registered
        rules = [str(rule) for rule in app.url_map.iter_rules()]
        critical_routes = ['/health', '/api/ybb/export/participants']
        
        for route in critical_routes:
            if any(route in rule for rule in rules):
                print(f"SUCCESS: Route {route} is registered")
            else:
                print(f"WARNING: Route {route} not found in registered routes")
        
        print("=== Application Ready ===")
        return app
        
    except ImportError as e:
        print(f"IMPORT ERROR: {e}")
        print("This indicates missing dependencies or module path issues")
        import traceback
        traceback.print_exc()
        raise e
    except Exception as e:
        print(f"STARTUP ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise e

# Create the application instance for WSGI servers (like gunicorn)
try:
    application = create_application()
    # For compatibility, also assign to 'app'
    app = application
    print("SUCCESS: WSGI application created and ready for gunicorn")
except Exception as e:
    print(f"CRITICAL: Failed to create WSGI application: {e}")
    # Don't call sys.exit() in WSGI context - let gunicorn handle it
    raise e

# For manual execution (development/testing)
if __name__ == '__main__':
    try:
        # Get port from environment (hosting platforms set this automatically)
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', os.environ.get('API_HOST', '0.0.0.0'))
        
        print(f"Manual execution mode")
        print(f"Starting server on {host}:{port}")
        
        # Run the application directly
        application.run(
            host=host,
            port=port,
            debug=False  # Never use debug in production
        )
        
    except Exception as e:
        print(f"MANUAL STARTUP ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
