#!/usr/bin/env python3
"""
Railway Pandas Troubleshooting Script
Comprehensive diagnostics for pandas installation issues
"""
import sys
import os
import subprocess
import tempfile

def check_python_environment():
    """Check Python environment details"""
    print("="*50)
    print("PYTHON ENVIRONMENT CHECK")
    print("="*50)
    
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Platform: {sys.platform}")
    print(f"Current working directory: {os.getcwd()}")
    
    print("\nPython path:")
    for i, path in enumerate(sys.path[:10]):
        print(f"  {i}: {path}")
    if len(sys.path) > 10:
        print(f"  ... and {len(sys.path) - 10} more")
    
    print("\nEnvironment variables (pandas-related):")
    pandas_env_vars = [
        'PYTHONPATH', 'LD_LIBRARY_PATH', 'BLAS', 'LAPACK', 'ATLAS',
        'NPY_NUM_BUILD_JOBS', 'OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS'
    ]
    for var in pandas_env_vars:
        value = os.environ.get(var, 'NOT_SET')
        print(f"  {var}: {value}")

def check_system_libraries():
    """Check for required system libraries"""
    print("\n" + "="*50)
    print("SYSTEM LIBRARIES CHECK")
    print("="*50)
    
    # Check for library files
    lib_patterns = [
        'libopenblas*',
        'liblapack*',
        'libblas*',
        'libgfortran*',
        'libquadmath*',
        'libgomp*'
    ]
    
    for pattern in lib_patterns:
        print(f"\nSearching for {pattern}:")
        try:
            result = subprocess.run(['find', '/nix/store', '-name', pattern, '-type', 'f'], 
                                  capture_output=True, text=True, timeout=30)
            if result.stdout.strip():
                libs = result.stdout.strip().split('\n')[:3]  # Show first 3 matches
                for lib in libs:
                    print(f"  ✅ Found: {lib}")
                total_matches = len(result.stdout.strip().split('\n'))
                if total_matches > 3:
                    print(f"  ... and {total_matches - 3} more")
            else:
                print(f"  ❌ Not found: {pattern}")
        except Exception as e:
            print(f"  ⚠️  Search failed: {e}")

def check_package_installations():
    """Check which packages are actually installed"""
    print("\n" + "="*50)
    print("PACKAGE INSTALLATION CHECK")
    print("="*50)
    
    packages_to_check = [
        'pip', 'setuptools', 'wheel', 'numpy', 'pandas', 'openpyxl',
        'flask', 'requests', 'python-dateutil', 'pytz'
    ]
    
    for package in packages_to_check:
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'show', package], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                # Extract version from pip show output
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        version = line.split(':', 1)[1].strip()
                        print(f"  ✅ {package}: {version}")
                        break
                else:
                    print(f"  ✅ {package}: installed (version unknown)")
            else:
                print(f"  ❌ {package}: not installed")
        except Exception as e:
            print(f"  ⚠️  {package}: check failed ({e})")

def test_numpy_import():
    """Test numpy import and basic functionality"""
    print("\n" + "="*50)
    print("NUMPY IMPORT TEST")
    print("="*50)
    
    try:
        import numpy as np
        print(f"✅ numpy import successful")
        print(f"   Version: {np.__version__}")
        print(f"   Location: {np.__file__}")
        
        # Test basic functionality
        arr = np.array([1, 2, 3, 4, 5])
        result = np.sum(arr)
        print(f"   Basic test: sum([1,2,3,4,5]) = {result}")
        
        # Test BLAS functionality
        try:
            matrix1 = np.random.random((100, 100))
            matrix2 = np.random.random((100, 100))
            result = np.dot(matrix1, matrix2)
            print(f"   BLAS test: matrix multiplication successful ({result.shape})")
        except Exception as e:
            print(f"   ⚠️  BLAS test failed: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ numpy import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ numpy test failed: {e}")
        return False

def test_pandas_import():
    """Test pandas import and basic functionality"""
    print("\n" + "="*50)
    print("PANDAS IMPORT TEST")
    print("="*50)
    
    try:
        import pandas as pd
        print(f"✅ pandas import successful")
        print(f"   Version: {pd.__version__}")
        print(f"   Location: {pd.__file__}")
        
        # Test basic functionality
        df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
        result = df.sum().sum()
        print(f"   Basic test: DataFrame sum = {result}")
        
        # Test Excel functionality
        try:
            from io import BytesIO
            buffer = BytesIO()
            df.to_excel(buffer, index=False, engine='openpyxl')
            buffer.seek(0)
            df2 = pd.read_excel(buffer, engine='openpyxl')
            print(f"   Excel test: read/write successful ({len(df2)} rows)")
        except Exception as e:
            print(f"   ⚠️  Excel test failed: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        
        # Try to get more details about the import error
        try:
            import numpy as np
            print(f"   ℹ️  numpy is available ({np.__version__})")
            print("   ℹ️  pandas import failure despite numpy availability suggests C++ library issues")
        except ImportError:
            print("   ℹ️  numpy is also not available - fundamental installation problem")
        
        return False
    except Exception as e:
        print(f"❌ pandas test failed: {e}")
        return False

def suggest_fixes():
    """Suggest potential fixes based on diagnostic results"""
    print("\n" + "="*50)
    print("SUGGESTED FIXES")
    print("="*50)
    
    print("Based on the diagnostic results, try these fixes:")
    print()
    print("1. **Library Path Issues**:")
    print("   - Add missing system libraries to nixpacks.toml")
    print("   - Set LD_LIBRARY_PATH environment variable")
    print("   - Use: export LD_LIBRARY_PATH=/nix/store/*/lib:$LD_LIBRARY_PATH")
    print()
    print("2. **Package Installation Issues**:")
    print("   - Reinstall with: pip install --only-binary=all --force-reinstall numpy pandas")
    print("   - Try alternative versions: numpy==1.21.6 pandas==1.5.3")
    print("   - Use conda-forge: pip install --extra-index-url https://pypi.anaconda.org/conda-forge/simple pandas")
    print()
    print("3. **Environment Issues**:")
    print("   - Set: export BLAS=openblas LAPACK=openblas")
    print("   - Set: export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1")
    print("   - Clear Python cache: find /app -name '*.pyc' -delete")
    print()
    print("4. **Railway-Specific Issues**:")
    print("   - Add system packages: openblas, lapack-reference, gfortran")
    print("   - Use virtual environment: python -m venv venv && source venv/bin/activate")
    print("   - Install in sequence: numpy → pandas → openpyxl")

def main():
    """Run complete diagnostic"""
    print("RAILWAY PANDAS TROUBLESHOOTING")
    print("YBB Data Management Service")
    print("Timestamp:", __import__('datetime').datetime.now())
    
    # Run all checks
    check_python_environment()
    check_system_libraries()
    check_package_installations()
    
    numpy_ok = test_numpy_import()
    pandas_ok = test_pandas_import()
    
    # Summary
    print("\n" + "="*50)
    print("DIAGNOSTIC SUMMARY")
    print("="*50)
    
    print(f"numpy:  {'✅ WORKING' if numpy_ok else '❌ FAILED'}")
    print(f"pandas: {'✅ WORKING' if pandas_ok else '❌ FAILED'}")
    
    if not pandas_ok:
        suggest_fixes()
    
    if pandas_ok:
        print("\n🎉 pandas is working correctly!")
        print("✅ Full export functionality available")
    else:
        print("\n💥 pandas is not working")
        print("❌ Export functionality limited")
    
    return pandas_ok

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)