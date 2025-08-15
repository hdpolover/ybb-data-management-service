#!/usr/bin/env python3
"""
Simple and reliable Railway startup script
"""
import os
import sys

# Set production environment
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_APP', 'app')

# Ensure proper path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main startup function for Railway"""
    try:
        # Import the Flask app
        from app import app
        
        # Get port from environment (Railway sets this)
        port = int(os.environ.get('PORT', 5000))
        host = '0.0.0.0'
        
        print(f"=== YBB Data Management Service ===")
        print(f"Environment: {os.environ.get('FLASK_ENV', 'unknown')}")
        print(f"Host: {host}")
        print(f"Port: {port}")
        print(f"Debug: {app.config.get('DEBUG', False)}")
        print(f"Starting server...")
        
        # Start the Flask app with production settings
        app.run(
            host=host,
            port=port,
            debug=False,
            threaded=True,
            use_reloader=False
        )
        
    except Exception as e:
        print(f"STARTUP ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
