#!/usr/bin/env python3
"""
Railway Production Startup with Numpy Fix
Handles numpy import issues common in containerized environments
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
    print("YBB DATA MANAGEMENT SERVICE - RAILWAY STARTUP (NUMPY FIX)")
    print("="*60)
    print(f"Python: {sys.version}")
    print(f"Working Dir: {os.getcwd()}")
    print(f"Port: {os.environ.get('PORT', 'NOT_SET')}")
    print(f"Environment: {os.environ.get('FLASK_ENV', 'unknown')}")
    print(f"Python Path: {':'.join(sys.path[:3])}...")
    print("="*60)

def fix_numpy_path():
    """Fix numpy import path issues"""
    print("Checking for numpy path conflicts...")
    
    # Remove current working directory from Python path to avoid numpy source conflicts
    if os.getcwd() in sys.path:
        sys.path.remove(os.getcwd())
        print("✓ Removed current directory from Python path")
    
    # Remove any 'numpy' directories from path
    paths_to_remove = []
    for path in sys.path:
        if 'numpy' in path.lower() and os.path.isdir(path):
            paths_to_remove.append(path)
    
    for path in paths_to_remove:
        sys.path.remove(path)
        print(f"✓ Removed numpy source path: {path}")
    
    # Ensure site-packages comes first
    site_packages = [p for p in sys.path if 'site-packages' in p]
    for sp in site_packages:
        if sp in sys.path:
            sys.path.remove(sp)
        sys.path.insert(0, sp)
    
    print(f"✓ Updated Python path, site-packages prioritized")

def test_critical_imports():
    """Test critical imports with numpy fix"""
    print("Testing critical imports...")
    
    # Test numpy first with specific error handling
    try:
        print("Testing numpy import...")
        import numpy as np
        print(f"✓ numpy imported successfully (version: {np.__version__})")
        
        # Test a simple numpy operation
        arr = np.array([1, 2, 3])
        print("✓ numpy operations working")
        
    except ImportError as e:
        print(f"✗ numpy import failed: {e}")
        
        # Try alternative numpy import strategies
        print("Trying alternative numpy import...")
        try:
            # Clear any numpy modules from cache
            for module in list(sys.modules.keys()):
                if 'numpy' in module:
                    del sys.modules[module]
            
            # Try importing again
            import numpy as np
            print(f"✓ numpy imported on retry (version: {np.__version__})")
        except Exception as e2:
            print(f"✗ numpy still failing: {e2}")
            return False
    
    # Test other critical imports
    critical_imports = [
        ('pandas', 'pandas'),
        ('openpyxl', 'openpyxl'),
        ('flask', 'Flask')
    ]
    
    for module, display_name in critical_imports:
        try:
            __import__(module)
            print(f"✓ {display_name} imported")
        except ImportError as e:
            print(f"✗ {display_name} import failed: {e}")
            return False
    
    return True

def create_and_test_app():
    """Create Flask app and test it"""
    print("Creating Flask application...")
    try:
        # Add current dir to path (but after site-packages)
        if os.getcwd() not in sys.path:
            sys.path.append(os.getcwd())
        
        # Force import the complete application
        print("Importing complete YBB application...")
        from app import create_app
        print("✓ create_app imported successfully")
        
        app = create_app()
        print("✓ Flask app created successfully")
        
        # Verify this is the complete app, not minimal
        with app.app_context():
            rules = [str(rule) for rule in app.url_map.iter_rules()]
            health_found = any('/health' in rule for rule in rules)
            export_found = any('/api/ybb/export' in rule for rule in rules)
            certificate_found = any('/api/ybb/certificates' in rule for rule in rules)
            
            print(f"✓ Total routes: {len(rules)}")
            print(f"✓ Health endpoint: {'Found' if health_found else 'Missing'}")
            print(f"✓ Export endpoints: {'Found' if export_found else 'Missing'}")
            print(f"✓ Certificate endpoints: {'Found' if certificate_found else 'Missing'}")
            
            print("✓ Complete app mode confirmed")
        
        return app
        
    except Exception as e:
        print(f"✗ App creation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main startup function with numpy fixes"""
    log_startup_info()
    
    # Fix numpy path issues first
    fix_numpy_path()
    
    # Test imports with fixes
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
    
    # Start server
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
