#!/usr/bin/env python3
"""
Simple startup script for hosting platforms
This file can be used as the main application entry point
"""
import os
import sys

# Ensure we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment to production
os.environ.setdefault('FLASK_ENV', 'production')

try:
    # Import and create the Flask application
    from app import app
    
    # This is the WSGI application that hosting platforms will use
    application = app
    
    if __name__ == '__main__':
        # For direct execution (testing)
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=False)
        
except Exception as e:
    print(f"Failed to start application: {e}")
    import traceback
    traceback.print_exc()
    raise
