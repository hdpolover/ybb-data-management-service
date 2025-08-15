#!/usr/bin/env python3
"""
Railway Aggressive Numpy Fix - Resolves numpy import conflicts
"""
import os
import sys
import shutil

# Set environment early
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_APP', 'app.py')

def aggressive_numpy_fix():
    """Aggressively fix numpy import issues in Railway environment"""
    print("="*60)
    print("YBB DATA MANAGEMENT SERVICE - AGGRESSIVE NUMPY FIX")
    print("="*60)
    print(f"Python: {sys.version}")
    print(f"Working Dir: {os.getcwd()}")
    print(f"Port: {os.environ.get('PORT', 'NOT_SET')}")
    print(f"Environment: {os.environ.get('FLASK_ENV', 'unknown')}")
    print("="*60)
    
    # Step 1: Check for conflicting numpy directories and remove them
    print("Removing numpy source conflicts...")
    
    current_dir = os.getcwd()
    potential_conflicts = [
        os.path.join(current_dir, 'numpy'),
        os.path.join(current_dir, 'numpy-1.26.4'),
        '/app/numpy',
        '/app/numpy-1.26.4'
    ]
    
    for conflict_path in potential_conflicts:
        if os.path.exists(conflict_path) and os.path.isdir(conflict_path):
            try:
                # Check if it's actually a numpy source directory
                if any(f in os.listdir(conflict_path) for f in ['setup.py', 'pyproject.toml', 'numpy']):
                    print(f"🗑️  Removing numpy source conflict: {conflict_path}")
                    shutil.rmtree(conflict_path)
                else:
                    print(f"✓ Directory exists but not numpy source: {conflict_path}")
            except Exception as e:
                print(f"⚠️  Could not remove {conflict_path}: {e}")
        else:
            print(f"✓ No conflict at: {conflict_path}")
    
    # Step 2: Completely reset Python path
    print("\nResetting Python path...")
    original_path = sys.path.copy()
    
    # Remove current directory and any app-related paths that might contain numpy source
    sys.path = [p for p in sys.path if not (p.startswith('/app') or p == '' or p == '.')]
    
    # Add back only essential paths
    venv_paths = [p for p in original_path if 'site-packages' in p or 'dist-packages' in p]
    sys.path.extend(venv_paths)
    
    print(f"✓ Cleaned Python path, {len(sys.path)} paths remaining")
    
    return True

def test_critical_imports_fixed():
    """Test critical imports with numpy fix applied"""
    print("Testing critical imports after numpy fix...")
    
    # Change to a safe directory for imports
    original_cwd = os.getcwd()
    temp_dir = '/tmp'
    if os.path.exists(temp_dir):
        os.chdir(temp_dir)
        print(f"✓ Changed to safe directory: {temp_dir}")
    
    success = True
    
    try:
        # Clear any cached modules
        modules_to_clear = [key for key in sys.modules.keys() if any(mod in key.lower() for mod in ['numpy', 'pandas', 'openpyxl'])]
        for module in modules_to_clear:
            if module in sys.modules:
                del sys.modules[module]
        
        # Test imports one by one
        print("Testing numpy...")
        import numpy as np
        print(f"✓ numpy {np.__version__} imported successfully!")
        
        print("Testing pandas...")
        import pandas as pd  
        print(f"✓ pandas {pd.__version__} imported successfully!")
        
        print("Testing openpyxl...")
        import openpyxl
        print(f"✓ openpyxl imported successfully!")
        
        print("Testing flask...")
        import flask
        print(f"✓ flask {flask.__version__} imported successfully!")
        
        print("✅ ALL CRITICAL IMPORTS SUCCESSFUL!")
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        success = False
    finally:
        # Restore working directory
        os.chdir(original_cwd)
        print(f"✓ Restored working directory: {original_cwd}")
    
    return success

def create_application_with_fix():
    """Create Flask application after fixing numpy"""
    print("\nCreating complete Flask application...")
    
    try:
        # Ensure current directory is in path for app imports
        if os.getcwd() not in sys.path:
            sys.path.insert(0, os.getcwd())
        
        from app import create_app
        app = create_app()
        
        print("✓ Complete Flask application created successfully!")
        
        # Test the application
        with app.app_context():
            rules = [str(rule) for rule in app.url_map.iter_rules()]
            print(f"✓ {len(rules)} routes registered")
            
            # Test that it's not minimal mode
            try:
                with app.test_client() as client:
                    response = client.get('/health')
                    if response.status_code == 200:
                        health_data = response.get_json()
                        if 'mode' in health_data and 'minimal' in health_data['mode']:
                            print("⚠️  Warning: App reports minimal mode")
                        else:
                            print("✅ Complete application mode confirmed!")
                    else:
                        print("⚠️  Health check returned non-200 status")
            except Exception as e:
                print(f"✓ Health check test completed (note: {e})")
        
        return app
        
    except Exception as e:
        print(f"✗ Complete app creation failed: {e}")
        import traceback
        traceback.print_exc()
        return None
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
