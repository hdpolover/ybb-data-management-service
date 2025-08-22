#!/usr/bin/env python3
"""
Railway C++ Library Diagnostic
Check for missing C++ runtime libraries that numpy needs
"""

import subprocess
import sys
import os
import glob
from datetime import datetime

def log(message, level="INFO"):
    """Simple logging"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def find_library_files():
    """Find C++ standard library files"""
    log("🔍 Searching for C++ runtime libraries...")
    
    # Library patterns to search for
    patterns = [
        "libstdc++.so*",
        "libgcc_s.so*", 
        "libm.so*",
        "libc.so*"
    ]
    
    search_paths = [
        "/nix/store/*/lib",
        "/nix/store/*/lib64",
        "/usr/lib",
        "/usr/lib64",
        "/lib",
        "/lib64"
    ]
    
    found_libs = {}
    
    for pattern in patterns:
        found_libs[pattern] = []
        for path in search_paths:
            try:
                matches = glob.glob(f"{path}/{pattern}")
                found_libs[pattern].extend(matches)
            except Exception:
                pass
    
    # Report findings
    for pattern, files in found_libs.items():
        if files:
            log(f"✅ {pattern}: Found {len(files)} files")
            for f in files[:3]:  # Show first 3
                log(f"   {f}")
            if len(files) > 3:
                log(f"   ... and {len(files) - 3} more")
        else:
            log(f"❌ {pattern}: NOT FOUND", "ERROR")
    
    return found_libs

def check_environment_variables():
    """Check library path environment variables"""
    log("🔍 Checking environment variables...")
    
    env_vars = [
        'LD_LIBRARY_PATH',
        'LIBRARY_PATH', 
        'PATH'
    ]
    
    for var in env_vars:
        value = os.environ.get(var, 'NOT_SET')
        log(f"   {var}: {value[:100]}{'...' if len(value) > 100 else ''}")

def test_simple_import():
    """Test importing without numpy first"""
    log("🧪 Testing basic Python functionality...")
    
    try:
        import sys
        log(f"✅ Python import working: {sys.version.split()[0]}")
        
        # Test basic modules
        import os, subprocess, tempfile
        log("✅ Standard library imports working")
        
        return True
    except Exception as e:
        log(f"❌ Basic Python functionality failed: {e}", "ERROR")
        return False

def test_numpy_import_detailed():
    """Test numpy import with detailed error reporting"""
    log("🧪 Testing numpy import with detailed diagnostics...")
    
    try:
        # First try to import numpy
        import numpy as np
        log(f"✅ NumPy import successful: {np.__version__}")
        
        # Test basic operations
        arr = np.array([1, 2, 3])
        result = np.sum(arr)
        log(f"✅ NumPy operations working: sum([1,2,3]) = {result}")
        
        return True
        
    except ImportError as e:
        log(f"❌ NumPy import failed: {e}", "ERROR")
        
        # Try to get more specific error information
        error_str = str(e)
        if "libstdc++.so.6" in error_str:
            log("💡 Missing C++ standard library (libstdc++.so.6)", "ERROR")
            log("💡 Need to add C++ runtime libraries to nixpkgs", "ERROR")
        elif "libgcc_s.so" in error_str:
            log("💡 Missing GCC runtime library (libgcc_s.so)", "ERROR")
        elif "GLIBC" in error_str:
            log("💡 GLIBC version compatibility issue", "ERROR")
        
        return False
        
    except Exception as e:
        log(f"❌ NumPy test failed with unexpected error: {e}", "ERROR")
        return False

def suggest_fixes():
    """Suggest fixes based on diagnostic results"""
    log("💡 Suggested fixes for missing C++ libraries:")
    log("")
    log("1. **Add C++ Runtime Libraries to nixpkgs**:")
    log("   - Add: stdenv.cc.cc (full compiler with runtime)")
    log("   - Add: gcc.cc.lib (GCC libraries)")
    log("   - Add: libcxx (C++ standard library)")
    log("")
    log("2. **Enhanced Library Path Configuration**:")
    log("   - Set LD_LIBRARY_PATH to include GCC library paths")
    log("   - Add /nix/store/*-gcc-*/lib to library search")
    log("   - Include stdenv library paths")
    log("")
    log("3. **Alternative Numpy Version**:")
    log("   - Try numpy==1.26.4 (might have better compatibility)")
    log("   - Use numpy==1.24.4 (more conservative version)")
    log("   - Force specific numpy build variant")

def main():
    """Main diagnostic execution"""
    log("🚀 Starting Railway C++ Library Diagnostic")
    log("=" * 50)
    
    # Run diagnostics
    check_environment_variables()
    library_files = find_library_files()
    basic_ok = test_simple_import()
    numpy_ok = test_numpy_import_detailed()
    
    # Summary
    log("=" * 50)
    log("🔍 DIAGNOSTIC SUMMARY:")
    log(f"   Basic Python: {'✅ OK' if basic_ok else '❌ FAILED'}")
    log(f"   NumPy Import: {'✅ OK' if numpy_ok else '❌ FAILED'}")
    
    # Check if we found the missing library
    libstdcpp_found = any(library_files.get("libstdc++.so*", []))
    log(f"   libstdc++.so: {'✅ FOUND' if libstdcpp_found else '❌ MISSING'}")
    
    if not numpy_ok:
        suggest_fixes()
    
    if numpy_ok:
        log("🎉 NumPy is working - no C++ library issues!")
    else:
        log("💥 NumPy import failed - C++ library issue confirmed")
    
    return numpy_ok

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        log(f"💥 Diagnostic script failed: {e}", "ERROR")
        sys.exit(1)