#!/usr/bin/env python3
"""
Railway Library Path Fixer
Set explicit library paths based on actual found libraries
"""

import os
import glob
import subprocess
import sys

def log(message):
    """Simple logging"""
    print(f"[LIBPATH] {message}")

def find_actual_library_paths():
    """Find the actual paths where C++ libraries are located"""
    log("🔍 Finding actual C++ library paths...")
    
    # Find libstdc++.so.6 specifically
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
        "/nix/store/*-gcc-*/lib64",
        "/nix/store/*-libgcc/lib",
        "/nix/store/*-libgcc/lib64"
    ]
    
    for pattern in gcc_patterns:
        matches = glob.glob(pattern)
        for match in matches:
            if os.path.isdir(match):
                found_paths.add(match)
                log(f"✅ Found GCC library in: {match}")
    
    return list(found_paths)

def set_library_paths(lib_paths):
    """Set library paths in environment"""
    if not lib_paths:
        log("❌ No library paths found!")
        return False
    
    # Create explicit library path
    explicit_path = ":".join(lib_paths)
    
    # Set environment variables
    current_ld_path = os.environ.get('LD_LIBRARY_PATH', '')
    new_ld_path = f"{explicit_path}:{current_ld_path}".strip(':')
    
    os.environ['LD_LIBRARY_PATH'] = new_ld_path
    
    current_lib_path = os.environ.get('LIBRARY_PATH', '')
    new_lib_path = f"{explicit_path}:{current_lib_path}".strip(':')
    
    os.environ['LIBRARY_PATH'] = new_lib_path
    
    log(f"📋 Set LD_LIBRARY_PATH to: {new_ld_path[:200]}...")
    log(f"📋 Set LIBRARY_PATH to: {new_lib_path[:200]}...")
    
    return True

def test_library_access():
    """Test if libstdc++.so.6 can be found"""
    log("🧪 Testing library access...")
    
    try:
        # Use ldd to check if libraries can be found
        result = subprocess.run(['python', '-c', 'import ctypes; ctypes.CDLL("libstdc++.so.6")'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            log("✅ libstdc++.so.6 can be loaded successfully")
            return True
        else:
            log(f"❌ libstdc++.so.6 loading failed: {result.stderr}")
            return False
            
    except Exception as e:
        log(f"⚠️ Library test failed: {e}")
        return False

def main():
    """Main execution"""
    log("🚀 Starting Library Path Fix")
    
    # Find actual library paths
    lib_paths = find_actual_library_paths()
    
    if not lib_paths:
        log("💥 CRITICAL: No C++ library paths found")
        return False
    
    # Set explicit library paths
    if not set_library_paths(lib_paths):
        log("💥 CRITICAL: Failed to set library paths")
        return False
    
    # Test library access
    if test_library_access():
        log("✅ Library path fix successful")
        return True
    else:
        log("⚠️ Library path fix may not be complete")
        return True  # Continue anyway

if __name__ == "__main__":
    try:
        success = main()
        if success:
            log("🎯 Library paths configured - continuing installation...")
        else:
            log("⚠️ Library path issues detected - may affect numpy")
        sys.exit(0)  # Don't block build
    except Exception as e:
        log(f"💥 Library path fixer failed: {e}")
        sys.exit(0)  # Don't block build