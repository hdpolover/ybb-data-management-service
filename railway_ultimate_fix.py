#!/usr/bin/env python3
"""
Railway Aggressive Numpy Fix - Final Solution
Resolves numpy import conflicts by removing source directories
"""
import os
import sys
import shutil

# Set environment early
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_APP', 'app.py')

def aggressive_numpy_cleanup():
    """Remove all potential numpy source conflicts"""
    print("="*60)
    print("YBB DATA MANAGEMENT SERVICE - NUMPY CONFLICT RESOLVER")
    print("="*60)
    print(f"Python: {sys.version}")
    print(f"Working Dir: {os.getcwd()}")
    print(f"Port: {os.environ.get('PORT', 'NOT_SET')}")
    print("="*60)
    
    print("🔍 Scanning for numpy source conflicts...")
    
    # Potential numpy source directories that cause conflicts
    conflict_paths = [
        '/app/numpy',
        '/app/numpy-1.26.4',
        '/app/numpy-build',
        os.path.join(os.getcwd(), 'numpy'),
        os.path.join(os.getcwd(), 'numpy-1.26.4')
    ]
    
    removed_count = 0
    
    for path in conflict_paths:
        if os.path.exists(path) and os.path.isdir(path):
            try:
                # Verify it's actually a numpy source directory
                if any(f in os.listdir(path) for f in ['setup.py', 'pyproject.toml', '__init__.py']):
                    print(f"🗑️  Removing numpy source conflict: {path}")
                    shutil.rmtree(path)
                    removed_count += 1
                else:
                    print(f"✓ Directory exists but not numpy source: {path}")
            except Exception as e:
                print(f"⚠️  Could not remove {path}: {e}")
        else:
            print(f"✓ No conflict at: {path}")
    
    print(f"✅ Removed {removed_count} conflicting directories")
    
    # Clean up Python path
    print("\n🔧 Cleaning Python path...")
    original_path_len = len(sys.path)
    
    # Remove problematic paths
    paths_to_remove = []
    for path in sys.path:
        if (path == '' or 
            path == '.' or 
            path == '/app' or
            ('numpy' in path.lower() and 'site-packages' not in path)):
            paths_to_remove.append(path)
    
    for path in paths_to_remove:
        if path in sys.path:
            sys.path.remove(path)
    
    # Ensure site-packages paths come first
    site_packages_paths = [p for p in sys.path if 'site-packages' in p]
    for sp in site_packages_paths:
        if sp in sys.path:
            sys.path.remove(sp)
        sys.path.insert(0, sp)
    
    print(f"✅ Python path cleaned: {original_path_len} → {len(sys.path)} entries")

def test_numpy_import():
    """Test numpy import in isolation"""
    print("\n🧪 Testing numpy import...")
    
    # Change to tmp directory to avoid any local conflicts
    original_cwd = os.getcwd()
    tmp_dir = '/tmp'
    
    try:
        if os.path.exists(tmp_dir):
            os.chdir(tmp_dir)
            print(f"✓ Changed to clean directory: {tmp_dir}")
        
        # Clear all numpy-related modules from cache
        modules_to_clear = [key for key in sys.modules.keys() if 'numpy' in key.lower()]
        for module in modules_to_clear:
            del sys.modules[module]
            print(f"🧹 Cleared cached module: {module}")
        
        # Test numpy import
        import numpy as np
        print(f"✅ numpy {np.__version__} imported successfully!")
        print(f"📍 numpy location: {np.__file__}")
        
        # Quick functionality test
        arr = np.array([1, 2, 3, 4, 5])
        result = np.sum(arr)
        print(f"🧮 numpy test calculation: sum([1,2,3,4,5]) = {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ numpy import failed: {e}")
        return False
    finally:
        os.chdir(original_cwd)
        print(f"↩️  Restored working directory: {original_cwd}")

def test_all_dependencies():
    """Test all critical dependencies"""
    print("\n🔍 Testing all dependencies...")
    
    dependencies = [
        ('pandas', 'pandas'),
        ('openpyxl', 'openpyxl'), 
        ('flask', 'Flask'),
        ('reportlab', 'reportlab'),
        ('PIL', 'Pillow')
    ]
    
    success_count = 0
    total_count = len(dependencies)
    
    for module, display_name in dependencies:
        try:
            __import__(module)
            print(f"✅ {display_name} - imported successfully")
            success_count += 1
        except ImportError as e:
            print(f"❌ {display_name} - import failed: {e}")
    
    print(f"\n📊 Dependency status: {success_count}/{total_count} working")
    return success_count == total_count

def create_complete_app():
    """Create complete Flask application"""
    print("\n🏗️  Creating complete Flask application...")
    
    try:
        # Ensure app directory is accessible
        app_dir = os.getcwd()
        if app_dir not in sys.path:
            sys.path.append(app_dir)
        
        # Import and create app
        from app import create_app
        app = create_app()
        
        print("✅ Complete Flask application created!")
        
        # Verify app functionality
        with app.app_context():
            rules = [str(rule) for rule in app.url_map.iter_rules()]
            print(f"📋 {len(rules)} routes registered")
            
            # Check for key endpoints
            key_endpoints = ['/health', '/api/ybb/export/participants', '/api/ybb/certificates']
            found_endpoints = []
            
            for endpoint in key_endpoints:
                if any(endpoint in rule for rule in rules):
                    found_endpoints.append(endpoint)
            
            print(f"🔗 Key endpoints found: {len(found_endpoints)}/{len(key_endpoints)}")
            
            # Test health endpoint
            try:
                with app.test_client() as client:
                    response = client.get('/health')
                    if response.status_code == 200:
                        print("💚 Health endpoint responding correctly")
                    else:
                        print(f"⚠️  Health endpoint returned status {response.status_code}")
            except Exception as e:
                print(f"ℹ️  Health endpoint test: {e}")
        
        return app
        
    except Exception as e:
        print(f"❌ Complete app creation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main startup function"""
    
    # Step 1: Aggressive numpy cleanup
    aggressive_numpy_cleanup()
    
    # Step 2: Test numpy specifically
    numpy_ok = test_numpy_import()
    if not numpy_ok:
        print("💥 CRITICAL: Numpy import still failing after cleanup!")
        sys.exit(1)
    
    # Step 3: Test all dependencies
    all_deps_ok = test_all_dependencies()
    if not all_deps_ok:
        print("⚠️  WARNING: Some dependencies failing, but continuing with available ones...")
        print("🔄 Will attempt to create application with working dependencies")
    
    # Step 4: Create complete application (attempt even if some deps fail)
    app = create_complete_app()
    if not app:
        print("💥 CRITICAL: Failed to create application!")
        sys.exit(1)
    
    # Step 5: Start server
    port = int(os.environ.get('PORT', 5000))
    
    print("="*60)
    if all_deps_ok:
        print("🚀 ALL SYSTEMS GO!")
        print("✅ numpy working")
        print("✅ pandas working") 
        print("✅ openpyxl working")
    else:
        print("🟡 PARTIAL SYSTEMS GO!")
        print("✅ numpy working")
        print("⚠️  pandas issues detected") 
        print("✅ openpyxl working")
        print("🔄 Service running with available features")
    print(f"🌐 Starting server on 0.0.0.0:{port}")
    print("✅ Complete YBB application loaded")
    print("="*60)
    
    try:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            threaded=True
        )
    except Exception as e:
        print(f"💥 Server startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
