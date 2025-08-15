#!/usr/bin/env python3
"""
Railway Debug Startup Script
Provides detailed logging for Railway deployment debugging
"""
import os
import sys
import time
import traceback

# Set environment variables early
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_APP', 'app.py')

def debug_environment():
    """Print detailed environment information"""
    print("=" * 60)
    print("RAILWAY DEBUG STARTUP - YBB Data Management Service")
    print("=" * 60)
    print(f"Python Version: {sys.version}")
    print(f"Python Path: {sys.executable}")
    print(f"Working Directory: {os.getcwd()}")
    print(f"PORT Environment Variable: {os.environ.get('PORT', 'NOT SET')}")
    print(f"FLASK_ENV: {os.environ.get('FLASK_ENV', 'NOT SET')}")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'NOT SET')}")
    
    # List files in current directory
    print("\nFiles in current directory:")
    try:
        files = os.listdir('.')
        for file in sorted(files):
            if os.path.isfile(file):
                print(f"  FILE: {file}")
            else:
                print(f"  DIR:  {file}/")
    except Exception as e:
        print(f"  ERROR listing files: {e}")
    
    # Check if key files exist
    key_files = ['app.py', 'wsgi.py', 'config.py', 'requirements.txt']
    print("\nKey files check:")
    for file in key_files:
        exists = "✓" if os.path.exists(file) else "✗"
        print(f"  {exists} {file}")
    
    print("=" * 60)

def test_imports():
    """Test critical imports"""
    print("\nTesting critical imports...")
    
    critical_imports = [
        ('flask', 'Flask'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'), 
        ('openpyxl', 'openpyxl'),
        ('reportlab', 'reportlab'),
        ('PIL', 'Pillow'),
        ('PyPDF2', 'PyPDF2'),
        ('psutil', 'psutil')
    ]
    
    for module, display_name in critical_imports:
        try:
            __import__(module)
            print(f"  ✓ {display_name} - OK")
        except ImportError as e:
            print(f"  ✗ {display_name} - FAILED: {e}")
            return False
    
    return True

def test_app_creation():
    """Test application creation"""
    print("\nTesting application creation...")
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, os.getcwd())
        
        # Import and create app
        from app import create_app
        print("  ✓ Successfully imported create_app")
        
        app = create_app()
        print("  ✓ Successfully created Flask application")
        
        # Test routes
        with app.app_context():
            rules = [str(rule) for rule in app.url_map.iter_rules()]
            print(f"  ✓ Found {len(rules)} registered routes")
            
            # Check for critical routes
            if any('/health' in rule for rule in rules):
                print("  ✓ Health endpoint found")
            else:
                print("  ✗ Health endpoint missing!")
                
            if any('/api/ybb/export' in rule for rule in rules):
                print("  ✓ YBB export endpoints found")
            else:
                print("  ✗ YBB export endpoints missing!")
        
        return app
        
    except Exception as e:
        print(f"  ✗ Application creation failed: {e}")
        traceback.print_exc()
        return None

def start_server(app):
    """Start the server"""
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'
    
    print(f"\nStarting server on {host}:{port}")
    print("Health check should be available at: http://0.0.0.0:{}/health".format(port))
    print("=" * 60)
    
    try:
        app.run(
            host=host,
            port=port,
            debug=False,
            threaded=True
        )
    except Exception as e:
        print(f"Server startup failed: {e}")
        traceback.print_exc()
        sys.exit(1)

def main():
    """Main startup function"""
    debug_environment()
    
    if not test_imports():
        print("CRITICAL: Import test failed!")
        sys.exit(1)
    
    app = test_app_creation()
    if not app:
        print("CRITICAL: Application creation failed!")
        sys.exit(1)
    
    # Give Railway a moment to set up
    print("Waiting 2 seconds before starting server...")
    time.sleep(2)
    
    start_server(app)

if __name__ == '__main__':
    main()
