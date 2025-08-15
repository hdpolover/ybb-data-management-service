#!/usr/bin/env python3
"""
Test gunicorn WSGI setup for Railway deployment
"""
import os
import sys
import subprocess
import time
import requests
import signal
from threading import Thread

# Add current directory to path
sys.path.insert(0, os.path.abspath('.'))

def test_gunicorn_startup():
    """Test that gunicorn can start the application"""
    print("Testing gunicorn WSGI setup...")
    
    # Set production environment
    env = os.environ.copy()
    env['FLASK_ENV'] = 'production'
    env['PORT'] = '5001'  # Use different port to avoid conflicts
    
    gunicorn_process = None
    try:
        # Start gunicorn
        cmd = [
            sys.executable, '-m', 'gunicorn',
            'wsgi:application',
            '--bind', '0.0.0.0:5001',
            '--workers', '1',
            '--timeout', '30',
            '--preload'
        ]
        
        print(f"Starting: {' '.join(cmd)}")
        gunicorn_process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit for startup
        time.sleep(5)
        
        # Check if process is running
        if gunicorn_process.poll() is not None:
            stdout, stderr = gunicorn_process.communicate()
            print(f"ERROR: Gunicorn failed to start")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
        
        # Test health endpoint
        try:
            response = requests.get('http://localhost:5001/health', timeout=10)
            print(f"Health check: {response.status_code}")
            
            if response.status_code == 200:
                print(f"SUCCESS: Gunicorn startup test passed!")
                health_data = response.json()
                print(f"Service: {health_data.get('service')}")
                print(f"Status: {health_data.get('status')}")
                return True
            else:
                print(f"ERROR: Health check failed with {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Failed to connect to health endpoint: {e}")
            return False
    
    except Exception as e:
        print(f"ERROR: Gunicorn test failed: {e}")
        return False
    
    finally:
        # Clean up
        if gunicorn_process:
            try:
                gunicorn_process.terminate()
                gunicorn_process.wait(timeout=5)
            except:
                gunicorn_process.kill()

def test_wsgi_import():
    """Test that wsgi module can be imported"""
    print("Testing WSGI import...")
    
    try:
        # Set production environment
        os.environ['FLASK_ENV'] = 'production'
        os.environ['PORT'] = '5000'
        
        import wsgi
        app = wsgi.application
        
        print(f"SUCCESS: WSGI import successful")
        print(f"App type: {type(app)}")
        
        return True
    
    except Exception as e:
        print(f"ERROR: WSGI import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=== Testing Railway Deployment Configuration ===\n")
    
    # Test WSGI import first
    import_success = test_wsgi_import()
    
    # Test gunicorn startup
    gunicorn_success = False
    if import_success:
        gunicorn_success = test_gunicorn_startup()
    
    print(f"\n=== Results ===")
    print(f"WSGI Import: {'SUCCESS' if import_success else 'FAILED'}")
    print(f"Gunicorn Startup: {'SUCCESS' if gunicorn_success else 'FAILED'}")
    
    if import_success and gunicorn_success:
        print("\nSUCCESS: Railway deployment should work!")
        print("The health check failure was likely due to configuration issues that are now fixed.")
    elif import_success:
        print("\nWARNING: WSGI works but gunicorn startup failed")
        print("Check if gunicorn is installed and available")
    else:
        print("\nERROR: Basic WSGI import failed - need to fix import issues first")
    
    return import_success and gunicorn_success

if __name__ == "__main__":
    main()
