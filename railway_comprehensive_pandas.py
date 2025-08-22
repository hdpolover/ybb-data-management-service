#!/usr/bin/env python3
"""
Railway Comprehensive Pandas Installation Fix
Ensures pandas is properly installed with all dependencies on Railway platform
Latest versions and comprehensive functionality for August 2025
"""
import os
import sys
import subprocess
import tempfile
import shutil

def set_environment():
    """Set up proper environment variables for Railway"""
    print("🔧 Setting up comprehensive Railway environment...")
    
    # Critical environment variables for pandas/numpy on Railway
    env_vars = {
        'PYTHONPATH': '/app:/opt/venv/lib/python3.11/site-packages',
        'LD_LIBRARY_PATH': '/nix/store/*/lib:/nix/store/*/lib64',
        'LIBRARY_PATH': '/nix/store/*/lib:/nix/store/*/lib64',
        'C_INCLUDE_PATH': '/nix/store/*/include',
        'CPLUS_INCLUDE_PATH': '/nix/store/*/include',
        'PKG_CONFIG_PATH': '/nix/store/*/lib/pkgconfig:/nix/store/*/share/pkgconfig',
        'BLAS': 'openblas',
        'LAPACK': 'openblas',
        'ATLAS': 'None',
        'NPY_NUM_BUILD_JOBS': '1',
        'OPENBLAS_NUM_THREADS': '1',
        'OMP_NUM_THREADS': '1',
        'NUMEXPR_MAX_THREADS': '1',
        'MKL_NUM_THREADS': '1',
        'OPENBLAS_VERBOSE': '0'
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"   {key}={value}")
    
    print("✅ Comprehensive environment configured for pandas compatibility")

def clean_python_cache():
    """Clean Python bytecode cache that might cause import issues"""
    print("🧹 Cleaning Python cache comprehensively...")
    
    cache_dirs = [
        '/app/__pycache__',
        '/opt/venv/lib/python3.11/site-packages/__pycache__',
        '/tmp/__pycache__',
        '/app/.pytest_cache',
        '/app/.mypy_cache'
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
    print("🔍 Verifying comprehensive system libraries...")
    
    required_libs = [
        'libopenblas.so*',
        'liblapack.so*', 
        'libblas.so*',
        'libgfortran.so*',
        'libquadmath.so*',
        'libgomp.so*',
        'libgcc_s.so*'
    ]
    
    found_libs = []
    
    for lib_pattern in required_libs:
        lib_name = lib_pattern.replace('.so*', '')
        print(f"\nSearching for {lib_name}:")
        try:
            result = subprocess.run(['find', '/nix/store', '-name', lib_pattern, '-type', 'f'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and result.stdout.strip():
                libs = result.stdout.strip().split('\n')[:2]  # Show first 2 matches
                for lib in libs:
                    found_libs.append(lib)
                    print(f"   ✅ Found: {lib}")
                total_matches = len(result.stdout.strip().split('\n'))
                if total_matches > 2:
                    print(f"   ... and {total_matches - 2} more")
            else:
                print(f"   ❌ Not found: {lib_name}")
        except Exception as e:
            print(f"   ⚠️  Search failed for {lib_name}: {e}")
    
    print(f"✅ System libraries check: {len(found_libs)} libraries found")
    return len(found_libs) >= 4  # Need at least 4 critical libraries

def install_pandas_comprehensive():
    """Install comprehensive pandas stack with latest versions"""
    print("📦 Installing comprehensive pandas stack (August 2025 versions)...")
    
    try:
        # Get the virtual environment python path
        venv_python = '/opt/venv/bin/python'
        if not os.path.exists(venv_python):
            venv_python = sys.executable
        
        print(f"   Using Python: {venv_python}")
        
        # Comprehensive installation strategies with latest versions
        install_strategies = [
            # Strategy 1: Latest stable versions (August 2025)
            {
                'name': 'Latest stable versions (August 2025)',
                'packages': [
                    ('numpy', '1.26.4'),
                    ('pandas', '2.2.2'),
                    ('openpyxl', '3.1.5'),
                    ('scipy', '1.13.1'),
                    ('xlsxwriter', '3.2.0'),
                    ('matplotlib', '3.9.1'),
                    ('seaborn', '0.13.2')
                ]
            },
            # Strategy 2: Previous stable versions
            {
                'name': 'Previous stable versions',
                'packages': [
                    ('numpy', '1.25.2'),
                    ('pandas', '2.1.4'),
                    ('openpyxl', '3.1.2'),
                    ('scipy', '1.11.4'),
                    ('xlsxwriter', '3.1.9'),
                    ('matplotlib', '3.8.4')
                ]
            },
            # Strategy 3: Conservative versions
            {
                'name': 'Conservative stable versions',
                'packages': [
                    ('numpy', '1.24.4'),
                    ('pandas', '2.0.3'),
                    ('openpyxl', '3.1.2'),
                    ('scipy', '1.10.1'),
                    ('xlsxwriter', '3.1.0')
                ]
            }
        ]
        
        for strategy in install_strategies:
            print(f"   🔄 Trying strategy: {strategy['name']}")
            
            strategy_success = True
            installed_packages = []
            
            for package_name, version in strategy['packages']:
                print(f"      Installing {package_name}=={version}...")
                
                cmd = [venv_python, '-m', 'pip', 'install', '--only-binary=all', '--no-cache-dir', 
                       '--force-reinstall', f'{package_name}=={version}']
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=400)
                
                if result.returncode == 0:
                    print(f"      ✅ {package_name} {version} installed successfully")
                    installed_packages.append((package_name, version))
                else:
                    print(f"      ❌ {package_name} {version} installation failed:")
                    print(f"         stderr: {result.stderr[:200]}...")
                    strategy_success = False
                    break
            
            if strategy_success:
                # Test the installation comprehensively
                print(f"   🧪 Testing {strategy['name']} installation...")
                if test_comprehensive_functionality():
                    print(f"   ✅ {strategy['name']} successful with full functionality!")
                    print(f"   📋 Installed packages: {len(installed_packages)}")
                    for pkg, ver in installed_packages:
                        print(f"      - {pkg}: {ver}")
                    return True
                else:
                    print(f"   ❌ {strategy['name']} failed comprehensive functionality test")
            
            print(f"   ⚠️  {strategy['name']} failed, trying next strategy...")
        
        print("❌ All installation strategies failed")
        return False
        
    except subprocess.TimeoutExpired:
        print("❌ Installation timed out")
        return False
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return False

def test_comprehensive_functionality():
    """Test comprehensive pandas functionality needed for YBB service"""
    print("      🔍 Testing comprehensive functionality...")
    
    try:
        # Test numpy
        print("         Testing numpy...")
        import numpy as np
        test_array = np.array([1, 2, 3, 4, 5])
        test_sum = np.sum(test_array)
        print(f"         ✅ numpy {np.__version__}: sum test = {test_sum}")
        
        # Test matrix operations
        matrix1 = np.random.random((50, 50))
        matrix2 = np.random.random((50, 50))
        result = np.dot(matrix1, matrix2)
        print(f"         ✅ numpy BLAS: matrix multiplication {result.shape}")
        
        # Test pandas
        print("         Testing pandas...")
        import pandas as pd
        test_df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        test_total = test_df.sum().sum()
        print(f"         ✅ pandas {pd.__version__}: DataFrame test = {test_total}")
        
        # Test Excel functionality
        print("         Testing Excel functionality...")
        from io import BytesIO
        buffer = BytesIO()
        test_df.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)
        read_df = pd.read_excel(buffer, engine='openpyxl')
        print(f"         ✅ Excel: {len(read_df)} rows read successfully")
        
        # Test advanced pandas operations
        print("         Testing advanced operations...")
        large_df = pd.DataFrame({
            'category': ['A', 'B', 'A', 'B', 'A'] * 200,
            'value': range(1000),
            'date': pd.date_range('2025-01-01', periods=1000, freq='H')
        })
        
        # Test groupby
        grouped = large_df.groupby('category')['value'].agg(['sum', 'mean', 'std'])
        print(f"         ✅ GroupBy: {len(grouped)} groups processed")
        
        # Test time series
        time_series = large_df.set_index('date')['value'].resample('D').mean()
        print(f"         ✅ Time series: {len(time_series)} daily averages")
        
        # Test memory operations
        memory_df = pd.DataFrame(np.random.randn(2000, 20))
        memory_result = memory_df.describe()
        print(f"         ✅ Memory: {memory_result.shape} statistics computed")
        
        # Test multi-sheet Excel
        print("         Testing multi-sheet Excel...")
        multi_buffer = BytesIO()
        with pd.ExcelWriter(multi_buffer, engine='openpyxl') as writer:
            test_df.to_excel(writer, sheet_name='Sheet1', index=False)
            grouped.to_excel(writer, sheet_name='Summary')
            memory_result.to_excel(writer, sheet_name='Statistics')
        multi_buffer.seek(0)
        excel_sheets = pd.read_excel(multi_buffer, sheet_name=None, engine='openpyxl')
        print(f"         ✅ Multi-sheet Excel: {len(excel_sheets)} sheets created")
        
        # Test scipy integration
        print("         Testing scipy integration...")
        try:
            import scipy
            from scipy import stats
            sample_data = np.random.normal(0, 1, 1000)
            stat, p_value = stats.normaltest(sample_data)
            print(f"         ✅ scipy {scipy.__version__}: statistics test completed")
        except ImportError:
            print("         ℹ️  scipy: not available (optional)")
        
        # Test additional packages
        try:
            import xlsxwriter
            print(f"         ✅ xlsxwriter: {xlsxwriter.__version__}")
        except ImportError:
            print("         ℹ️  xlsxwriter: not available (optional)")
        
        try:
            import matplotlib
            print(f"         ✅ matplotlib: {matplotlib.__version__}")
        except ImportError:
            print("         ℹ️  matplotlib: not available (optional)")
        
        return True
        
    except Exception as e:
        print(f"      ❌ Comprehensive functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main comprehensive installation and verification process"""
    print("="*60)
    print("RAILWAY COMPREHENSIVE PANDAS INSTALLATION")
    print("YBB Data Management Service - August 2025")
    print("="*60)
    
    # Step 1: Set up comprehensive environment
    set_environment()
    
    # Step 2: Clean cache comprehensively
    clean_python_cache()
    
    # Step 3: Verify system libraries
    libs_ok = verify_system_libraries()
    if not libs_ok:
        print("⚠️  Some system libraries missing, but continuing...")
    
    # Step 4: Install comprehensive pandas stack
    install_ok = install_pandas_comprehensive()
    if not install_ok:
        print("💥 CRITICAL: Comprehensive pandas installation failed!")
        return False
    
    print("\n" + "="*60)
    print("🎉 COMPREHENSIVE PANDAS INSTALLATION SUCCESSFUL!")
    print("✅ numpy with BLAS support working")
    print("✅ pandas with full functionality working") 
    print("✅ openpyxl Excel support working")
    print("✅ Advanced operations working")
    print("✅ Multi-sheet Excel export working")
    print("✅ Time series and groupby operations working")
    print("🚀 Ready for complete YBB export functionality")
    print("="*60)
    
    return True

if __name__ == '__main__':
    success = main()
    if not success:
        print("\n💥 COMPREHENSIVE INSTALLATION FAILED - Check logs above")
        sys.exit(1)
    else:
        print("\n✅ Comprehensive installation completed successfully")
        sys.exit(0)