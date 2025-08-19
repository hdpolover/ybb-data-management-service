#!/usr/bin/env python3
"""
Railway Pandas Installation Fix
Ensures pandas is properly installed with all dependencies on Railway platform
"""
import os
import sys
import subprocess
import tempfile
import shutil

def set_environment():
    """Set up proper environment variables for Railway"""
    print("🔧 Setting up Railway environment...")
    
    # Critical environment variables for pandas/numpy on Railway
    env_vars = {
        'PYTHONPATH': '/app:/opt/venv/lib/python3.11/site-packages',
        'LD_LIBRARY_PATH': '/nix/store/bpq1s72cw9qb2fs8mnmlw6hn2c7iy0ss-gcc-14-20241116-lib/lib:/nix/store/ybjcla5bhj8g1y84998pn4a2drfxybkv-gcc-13.3.0-lib/lib',
        'BLAS': 'openblas',
        'LAPACK': 'openblas',
        'ATLAS': 'None',
        'NPY_NUM_BUILD_JOBS': '1',
        'OPENBLAS_NUM_THREADS': '1',
        'OMP_NUM_THREADS': '1',
        'NUMEXPR_MAX_THREADS': '1'
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"   {key}={value}")
    
    print("✅ Environment configured for pandas compatibility")

def clean_python_cache():
    """Clean Python bytecode cache that might cause import issues"""
    print("🧹 Cleaning Python cache...")
    
    cache_dirs = [
        '/app/__pycache__',
        '/opt/venv/lib/python3.11/site-packages/__pycache__',
        '/tmp/__pycache__'
    ]
    
    removed_count = 0
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                shutil.rmtree(cache_dir)
                print(f"   🗑️  Removed: {cache_dir}")
                removed_count += 1
            except Exception as e:
                print(f"   ⚠️  Could not remove {cache_dir}: {e}")
    
    # Also remove .pyc files
    try:
        result = subprocess.run(['find', '/app', '-name', '*.pyc', '-delete'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("   🗑️  Removed .pyc files")
        else:
            print(f"   ⚠️  Could not remove .pyc files: {result.stderr}")
    except:
        pass
    
    print(f"✅ Cache cleanup completed: {removed_count} directories removed")

def verify_system_libraries():
    """Verify that required system libraries are available"""
    print("🔍 Verifying system libraries...")
    
    required_libs = [
        'libopenblas.so',
        'liblapack.so', 
        'libgfortran.so',
        'libblas.so'
    ]
    
    found_libs = []
    
    # Check common library paths
    lib_paths = [
        '/nix/store/*/lib',
        '/usr/lib',
        '/usr/lib/x86_64-linux-gnu',
        '/lib/x86_64-linux-gnu'
    ]
    
    for lib in required_libs:
        try:
            result = subprocess.run(['find', '/nix/store', '-name', lib, '-type', 'f'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and result.stdout.strip():
                found_path = result.stdout.strip().split('\n')[0]
                found_libs.append((lib, found_path))
                print(f"   ✅ {lib}: {found_path}")
            else:
                print(f"   ❌ {lib}: Not found")
        except:
            print(f"   ⚠️  {lib}: Search failed")
    
    print(f"✅ System libraries check: {len(found_libs)}/{len(required_libs)} found")
    return len(found_libs) >= len(required_libs) // 2  # At least half should be available

def install_pandas_properly():
    """Install pandas using the most compatible method for Railway"""
    print("📦 Installing pandas with proper configuration...")
    
    try:
        # Get the virtual environment python path
        venv_python = '/opt/venv/bin/python'
        if not os.path.exists(venv_python):
            venv_python = sys.executable
        
        print(f"   Using Python: {venv_python}")
        
        # Try multiple installation strategies
        install_strategies = [
            # Strategy 1: Specific versions with binary-only
            {
                'name': 'Binary-only with pinned versions',
                'commands': [
                    [venv_python, '-m', 'pip', 'install', '--only-binary=all', '--no-cache-dir', 
                     '--force-reinstall', 'numpy==1.24.4'],
                    [venv_python, '-m', 'pip', 'install', '--only-binary=all', '--no-cache-dir', 
                     '--force-reinstall', 'pandas==2.0.3'],
                    [venv_python, '-m', 'pip', 'install', '--only-binary=all', '--no-cache-dir', 
                     '--force-reinstall', 'openpyxl==3.1.2']
                ]
            },
            # Strategy 2: Latest compatible versions
            {
                'name': 'Latest compatible versions',
                'commands': [
                    [venv_python, '-m', 'pip', 'install', '--only-binary=all', '--no-cache-dir', 
                     '--force-reinstall', 'numpy>=1.21.0,<1.25.0'],
                    [venv_python, '-m', 'pip', 'install', '--only-binary=all', '--no-cache-dir', 
                     '--force-reinstall', 'pandas>=1.5.0,<2.1.0'],
                    [venv_python, '-m', 'pip', 'install', '--only-binary=all', '--no-cache-dir', 
                     '--force-reinstall', 'openpyxl>=3.0.0']
                ]
            },
            # Strategy 3: Minimal versions
            {
                'name': 'Minimal working versions',
                'commands': [
                    [venv_python, '-m', 'pip', 'install', '--only-binary=all', '--no-cache-dir', 
                     '--force-reinstall', 'numpy==1.21.6'],
                    [venv_python, '-m', 'pip', 'install', '--only-binary=all', '--no-cache-dir', 
                     '--force-reinstall', 'pandas==1.5.3'],
                    [venv_python, '-m', 'pip', 'install', '--only-binary=all', '--no-cache-dir', 
                     '--force-reinstall', 'openpyxl==3.0.10']
                ]
            }
        ]
        
        for strategy in install_strategies:
            print(f"   � Trying strategy: {strategy['name']}")
            
            strategy_success = True
            for cmd in strategy['commands']:
                package_name = cmd[-1].split('==')[0].split('>=')[0].split('<')[0]
                print(f"      Installing {package_name}...")
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    print(f"      ✅ {package_name} installed successfully")
                else:
                    print(f"      ❌ {package_name} installation failed:")
                    print(f"         stderr: {result.stderr[:200]}...")
                    strategy_success = False
                    break
            
            if strategy_success:
                # Test the installation
                print(f"   🧪 Testing {strategy['name']} installation...")
                if test_pandas_import():
                    print(f"   ✅ {strategy['name']} successful!")
                    return True
                else:
                    print(f"   ❌ {strategy['name']} failed import test")
            
            print(f"   ⚠️  {strategy['name']} failed, trying next strategy...")
        
        print("❌ All installation strategies failed")
        return False
        
    except subprocess.TimeoutExpired:
        print("❌ Installation timed out")
        return False
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return False

def test_pandas_import():
    """Test that pandas can be imported and used"""
    print("🧪 Testing pandas import and functionality...")
    
    # Test in a clean subprocess to avoid cache issues
    test_script = '''
import sys
import os

# Ensure clean import
if "pandas" in sys.modules:
    del sys.modules["pandas"]
if "numpy" in sys.modules:
    del sys.modules["numpy"]

try:
    import numpy as np
    print(f"✅ numpy {np.__version__} imported")
    
    import pandas as pd
    print(f"✅ pandas {pd.__version__} imported")
    
    # Test basic functionality
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    result = df.sum().sum()
    print(f"✅ pandas basic test: sum = {result}")
    
    # Test Excel functionality
    from io import BytesIO
    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)
    df2 = pd.read_excel(buffer, engine="openpyxl")
    print(f"✅ pandas Excel test: {len(df2)} rows")
    
    print("SUCCESS")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
'''
    
    try:
        venv_python = '/opt/venv/bin/python'
        if not os.path.exists(venv_python):
            venv_python = sys.executable
            
        result = subprocess.run([venv_python, '-c', test_script], 
                              capture_output=True, text=True, timeout=60)
        
        print("   Test output:")
        for line in result.stdout.strip().split('\n'):
            print(f"     {line}")
        
        if result.stderr:
            print("   Errors:")
            for line in result.stderr.strip().split('\n'):
                print(f"     {line}")
        
        success = "SUCCESS" in result.stdout and result.returncode == 0
        
        if success:
            print("✅ pandas is working correctly!")
        else:
            print("❌ pandas test failed")
            
        return success
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

def main():
    """Main installation and verification process"""
    print("="*60)
    print("RAILWAY PANDAS INSTALLATION FIX")
    print("YBB Data Management Service")
    print("="*60)
    
    # Step 1: Set up environment
    set_environment()
    
    # Step 2: Clean cache
    clean_python_cache()
    
    # Step 3: Verify system libraries
    libs_ok = verify_system_libraries()
    if not libs_ok:
        print("⚠️  Some system libraries missing, but continuing...")
    
    # Step 4: Install pandas properly
    install_ok = install_pandas_properly()
    if not install_ok:
        print("💥 CRITICAL: pandas installation failed!")
        return False
    
    # Step 5: Test pandas
    test_ok = test_pandas_import()
    if not test_ok:
        print("💥 CRITICAL: pandas test failed!")
        return False
    
    print("\n" + "="*60)
    print("🎉 PANDAS INSTALLATION SUCCESSFUL!")
    print("✅ numpy working")
    print("✅ pandas working") 
    print("✅ openpyxl working")
    print("✅ Excel functionality available")
    print("🚀 Ready for full YBB export functionality")
    print("="*60)
    
    return True

if __name__ == '__main__':
    success = main()
    if not success:
        print("\n💥 INSTALLATION FAILED - Check logs above")
        sys.exit(1)
    else:
        print("\n✅ Installation completed successfully")
        sys.exit(0)