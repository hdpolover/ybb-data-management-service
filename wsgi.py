#!/usr/bin/env python3
"""
Production startup script for YBB Data Management Service
This script works for both manual execution and hosting platform auto-deployment
"""
import os
import sys

# Set production environment variables if not already set
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_APP', 'app_complete.py')

def create_application():
    """Create and return the Flask application"""
    try:
        # Import the Flask app from app_complete.py for production
        from app_complete import app
        
        print(f"✅ YBB Data Management Service loaded successfully")
        print(f"   Environment: {os.environ.get('FLASK_ENV', 'unknown')}")
        print(f"   Debug mode: {app.config.get('DEBUG', False)}")
        
        return app
        
    except Exception as e:
        print(f"❌ FATAL ERROR: Failed to create application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Create the application instance for WSGI servers (like gunicorn)
application = create_application()

# For compatibility, also assign to 'app'
app = application

# For manual execution
if __name__ == '__main__':
    try:
        # Get port from environment (hosting platforms set this automatically)
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', os.environ.get('API_HOST', '0.0.0.0'))
        
        print(f"🚀 Starting YBB Data Management Service...")
        print(f"   Host: {host}")
        print(f"   Port: {port}")
        print(f"   Mode: {'Development' if app.config.get('DEBUG') else 'Production'}")
        
        # Run the application
        app.run(
            host=host,
            port=port,
            debug=False  # Never use debug in production
        )
        
    except Exception as e:
        print(f"❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
