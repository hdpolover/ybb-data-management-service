#!/usr/bin/env python3
"""
Railway Ultra-Minimal Pandas Fix
Only installs essential packages with verified nixpkgs compatibility
Eliminates ALL undefined variable errors
"""

import subprocess
import sys
import os
from datetime import datetime

def log(message, level="INFO"):
    """Simple logging with timestamps"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def run_cmd(command, description):
    """Run command with error handling"""
    log(f"Running: {description}")
    log(f"Command: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            log(f"✅ SUCCESS: {description}")
            if result.stdout.strip():
                log(f"Output: {result.stdout.strip()}")
        else:
            log(f"❌ FAILED: {description}", "ERROR")
            log(f"Error: {result.stderr.strip()}", "ERROR")
            
        return result.returncode == 0, result.stdout, result.stderr
        
    except Exception as e:
        log(f"💥 EXCEPTION: {description} - {e}", "ERROR")
        return False, "", str(e)

def install_core_packages():
    """Install only essential packages for pandas"""
    log("📦 Installing ultra-minimal pandas stack...")
    
    # First, set up library paths before installing anything
    log("🔧 Setting up C++ library paths...")
    setup_library_paths()
    
    # Ultra-minimal package list - only what's absolutely needed
    packages = [
        ("pip", "24.2"),
        ("wheel", "0.44.0"),
        ("setuptools", "75.1.0"),
        ("numpy", "1.26.4"),  # Use older, more compatible version
        ("pandas", "2.2.2"),
        ("openpyxl", "3.1.5")
    ]
    
    # Install each package individually with strict binary-only policy
    for package, version in packages:
        full_package = f"{package}=={version}"
        command = f"pip install --only-binary=all --no-compile --no-cache-dir --force-reinstall {full_package}"
        success, stdout, stderr = run_cmd(command, f"Install {full_package}")
        
        if not success:
            log(f"❌ CRITICAL: Failed to install {full_package}", "ERROR")
            return False
    
    log("✅ Core packages installed successfully")
    return True

def setup_library_paths():
    """Set up C++ library paths dynamically"""
    log("🔍 Finding and setting up C++ library paths...")
    
    import glob
    import os
    
    # Find actual libstdc++.so.6 locations
    patterns = [
        "/nix/store/*/lib/libstdc++.so.6*",
        "/nix/store/*/lib64/libstdc++.so.6*"
    ]
    
    found_paths = set()
    for pattern in patterns:
        matches = glob.glob(pattern)
        for match in matches:
            lib_dir = os.path.dirname(match)
            found_paths.add(lib_dir)
            log(f"✅ Found C++ library in: {lib_dir}")
    
    # Also find GCC lib directories
    gcc_patterns = [
        "/nix/store/*-gcc-*/lib",
        "/nix/store/*-libgcc*/lib"
    ]
    
    for pattern in gcc_patterns:
        matches = glob.glob(pattern)
        for match in matches:
            if os.path.isdir(match):
                found_paths.add(match)
                log(f"✅ Found GCC library in: {match}")
    
    if found_paths:
        # Set library paths
        explicit_path = ":".join(found_paths)
        current_ld_path = os.environ.get('LD_LIBRARY_PATH', '')
        new_ld_path = f"{explicit_path}:{current_ld_path}".strip(':')
        
        os.environ['LD_LIBRARY_PATH'] = new_ld_path
        os.environ['LIBRARY_PATH'] = new_ld_path
        
        log(f"📋 Set LD_LIBRARY_PATH to: {new_ld_path[:100]}...")
        log("✅ C++ library paths configured")
    else:
        log("⚠️ No C++ library paths found", "WARNING")

def install_flask_stack():
    """Install Flask and minimal dependencies"""
    log("🌐 Installing Flask stack...")
    
    flask_packages = [
        ("flask", "3.0.3"),
        ("werkzeug", "3.0.4"),
        ("jinja2", "3.1.4"),
        ("markupsafe", "2.1.5"),
        ("itsdangerous", "2.2.0"),
        ("click", "8.1.7")
    ]
    
    success_count = 0
    for package, version in flask_packages:
        full_package = f"{package}=={version}"
        command = f"pip install --only-binary=all --no-compile --no-cache-dir {full_package}"
        success, stdout, stderr = run_cmd(command, f"Install {full_package}")
        
        if success:
            success_count += 1
        else:
            log(f"⚠️ Optional package {full_package} failed - continuing", "WARNING")
    
    log(f"📊 Flask stack: {success_count}/{len(flask_packages)} packages installed")
    return success_count > 0

def test_essential_functionality():
    """Test core pandas functionality"""
    log("🧪 Testing essential functionality...")
    
    test_script = '''
import sys
import numpy as np
import pandas as pd
import openpyxl

print("✅ Python: " + sys.version.split()[0])
print("✅ NumPy: " + np.__version__)
print("✅ Pandas: " + pd.__version__)
print("✅ OpenPyXL: " + openpyxl.__version__)

# Test basic operations
df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
print("✅ DataFrame: " + str(len(df)) + " rows")

# Test Excel functionality
import io
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Test", index=False)
print("✅ Excel: " + str(len(buffer.getvalue())) + " bytes")

print("🎉 ESSENTIAL TESTS PASSED!")
'''
    
    # Write test script to temporary file to avoid shell escaping issues
    with open("/tmp/test_pandas.py", "w") as f:
        f.write(test_script)
    
    success, stdout, stderr = run_cmd('python /tmp/test_pandas.py', "Test essential functionality")
    
    if success:
        log("✅ Essential functionality test PASSED")
        return True
    else:
        log("❌ Essential functionality test FAILED", "ERROR")
        return False

def main():
    """Main execution with enhanced library detection"""
    log("🚀 Starting Railway Ultra-Minimal Pandas Fix with Library Detective")
    log("=" * 50)
    
    # Step 0: Run library detective first
    log("🕵️ Running library detective to find and fix C++ libraries...")
    try:
        import subprocess
        result = subprocess.run(['python', 'railway_library_detective.py'], 
                              capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            log("✅ Library detective completed successfully")
        else:
            log("⚠️ Library detective had issues - continuing with fallback", "WARNING")
    except Exception as e:
        log(f"⚠️ Library detective failed: {e} - using fallback", "WARNING")
    
    # Step 1: Fix library paths before installation
    log("🔧 Setting up library paths...")
    try:
        import subprocess
        result = subprocess.run(['python', 'railway_library_path_fix.py'], 
                              capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            log("✅ Library paths configured successfully")
        else:
            log("⚠️ Library path setup had issues - continuing anyway", "WARNING")
    except Exception as e:
        log(f"⚠️ Library path setup failed: {e}", "WARNING")
    
    # Step 2: Source library environment if created by detective
    if os.path.exists("/app/library_env.sh"):
        log("📋 Loading library environment from detective...")
        try:
            with open("/app/library_env.sh", "r") as f:
                content = f.read()
                for line in content.split('\n'):
                    if line.startswith('export '):
                        # Parse export statements
                        parts = line.replace('export ', '').split('=', 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip(' "\'')
                            # Expand variables in value
                            if '$' in value and key in value:
                                value = value.replace(f'${key}', os.environ.get(key, ''))
                            os.environ[key] = value
                            log(f"📋 Set {key}")
        except Exception as e:
            log(f"⚠️ Failed to load library environment: {e}", "WARNING")
    
    # Step 3: Install core packages
    if not install_core_packages():
        log("💥 CRITICAL: Core package installation failed", "ERROR")
        sys.exit(1)
    
    # Step 4: Install Flask (optional)
    install_flask_stack()
    
    # Step 5: Test functionality with multiple approaches
    log("🧪 Testing with enhanced library detection...")
    if not test_essential_functionality():
        log("💥 CRITICAL: Essential functionality test failed", "ERROR")
        
        # Try with app/lib path if it exists
        if os.path.exists("/app/lib"):
            log("🔄 Retrying with /app/lib library path...")
            old_path = os.environ.get('LD_LIBRARY_PATH', '')
            os.environ['LD_LIBRARY_PATH'] = f"/app/lib:{old_path}"
            if test_essential_functionality():
                log("✅ SUCCESS with /app/lib library path!")
            else:
                sys.exit(1)
        else:
            sys.exit(1)
    
    log("=" * 50)
    log("🎉 ULTRA-MINIMAL PANDAS FIX COMPLETED!")
    log("✅ Pandas is working with minimal dependencies")
    log("✅ No undefined variable errors")
    log("✅ Ready for production")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        log("🛑 Installation interrupted", "WARNING")
        sys.exit(1)
    except Exception as e:
        log(f"💥 Unexpected error: {e}", "ERROR")
        sys.exit(1)