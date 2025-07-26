#!/usr/bin/env python3
"""
Railway.app startup script for YBB Data Management Service
"""
import os
import sys

# Set environment variables for Railway
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_APP', 'app.py')

if __name__ == '__main__':
    # Import and run the app
    from app import app
    
    # Get port from Railway environment
    port = int(os.environ.get('PORT', 5000))
    
    print(f"🚀 Starting YBB Data Management Service on port {port}")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )
