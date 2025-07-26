#!/usr/bin/env python3
"""
Setup and startup script for hosting platforms
This installs dependencies and then starts the Flask app
"""
import subprocess
import sys
import os

def install_requirements():
    """Install requirements if they don't exist"""
    try:
        import flask
        print("✅ Flask already installed")
    except ImportError:
        print("📦 Installing requirements...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print("✅ Requirements installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install requirements: {e}")
            return False
    return True

def start_application():
    """Start the Flask application"""
    try:
        # Import after ensuring dependencies are installed
        from app import app
        
        # Get port and host from environment
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', '0.0.0.0')
        
        print(f"🚀 Starting Flask application on {host}:{port}")
        app.run(host=host, port=port, debug=False)
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    print("🔧 Setting up YBB Data Management Service...")
    
    # Install requirements first
    if not install_requirements():
        print("❌ Setup failed - could not install requirements")
        sys.exit(1)
    
    # Start the application
    if not start_application():
        print("❌ Failed to start application")
        sys.exit(1)
