# Railway Pandas Installation Fix
# Alternative installation approach for pandas on Railway

import subprocess
import sys
import os

def install_pandas_railway():
    """Railway-specific pandas installation"""
    print("🚀 Railway Pandas Installation Starting...")
    
    # Set environment variables for compilation
    env = os.environ.copy()
    env.update({
        'NPY_NUM_BUILD_JOBS': '1',
        'OPENBLAS_NUM_THREADS': '1',
        'OMP_NUM_THREADS': '1',
        'BLAS': 'openblas',
        'LAPACK': 'openblas'
    })
    
    # Try different pandas installation approaches
    approaches = [
        {
            'name': 'Pre-compiled wheels from PyPI',
            'commands': [
                [sys.executable, '-m', 'pip', 'install', '--only-binary=all', '--no-deps', 'numpy==1.24.4'],
                [sys.executable, '-m', 'pip', 'install', '--only-binary=all', '--no-deps', 'pandas==2.0.3'],
                [sys.executable, '-m', 'pip', 'install', '--no-deps', 'python-dateutil', 'pytz', 'tzdata'],
                [sys.executable, '-m', 'pip', 'install', '--only-binary=all', 'openpyxl==3.1.2']
            ]
        },
        {
            'name': 'Alternative wheel sources',
            'commands': [
                [sys.executable, '-m', 'pip', 'install', '--only-binary=all', '--index-url', 'https://pypi.org/simple', 'numpy==1.21.6'],
                [sys.executable, '-m', 'pip', 'install', '--only-binary=all', '--index-url', 'https://pypi.org/simple', 'pandas==1.5.3'],
                [sys.executable, '-m', 'pip', 'install', '--only-binary=all', 'openpyxl==3.0.10']
            ]
        },
        {
            'name': 'Conda-forge style installation',
            'commands': [
                [sys.executable, '-m', 'pip', 'install', '--only-binary=all', '--extra-index-url', 'https://pypi.anaconda.org/conda-forge/simple', 'numpy'],
                [sys.executable, '-m', 'pip', 'install', '--only-binary=all', '--extra-index-url', 'https://pypi.anaconda.org/conda-forge/simple', 'pandas'],
                [sys.executable, '-m', 'pip', 'install', '--only-binary=all', 'openpyxl']
            ]
        }
    ]
    
    for approach in approaches:
        print(f"\n🔄 Trying: {approach['name']}")
        
        success = True
        for cmd in approach['commands']:
            package = cmd[-1] if not cmd[-1].startswith('--') else cmd[-2]
            print(f"   Installing {package}...")
            
            try:
                result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    print(f"   ✅ {package} installed")
                else:
                    print(f"   ❌ {package} failed: {result.stderr[:100]}...")
                    success = False
                    break
            except Exception as e:
                print(f"   ❌ {package} error: {e}")
                success = False
                break
        
        if success:
            # Test import
            try:
                import pandas as pd
                import numpy as np
                print(f"   ✅ Import test passed: pandas {pd.__version__}, numpy {np.__version__}")
                return True
            except ImportError as e:
                print(f"   ❌ Import test failed: {e}")
        
        print(f"   ⚠️  {approach['name']} failed, trying next approach...")
    
    print("❌ All approaches failed")
    return False

if __name__ == '__main__':
    success = install_pandas_railway()
    sys.exit(0 if success else 1)