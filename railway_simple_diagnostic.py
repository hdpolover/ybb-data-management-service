#!/usr/bin/env python3
"""
Railway Simple C++ Library Check
Quick verification that C++ libraries are available for numpy
"""

import os
import glob
import sys

def log(message):
    """Simple logging"""
    print(f"[DIAGNOSTIC] {message}")

def main():
    """Quick C++ library check"""
    log("🔍 Checking C++ runtime libraries for numpy...")
    
    # Check for essential C++ library
    patterns = [
        "/nix/store/*/lib/libstdc++.so*",
        "/nix/store/*/lib64/libstdc++.so*"
    ]
    
    found_libstdcpp = False
    for pattern in patterns:
        matches = glob.glob(pattern)
        if matches:
            found_libstdcpp = True
            log(f"✅ Found libstdc++: {matches[0]}")
            break
    
    if found_libstdcpp:
        log("✅ C++ libraries available - numpy installation should work")
        log("✅ Diagnostic PASSED - proceeding to package installation")
        return True
    else:
        log("❌ C++ libraries missing - numpy will fail")
        log("❌ Diagnostic FAILED - need to add stdenv.cc.cc to nixpkgs")
        return False

if __name__ == "__main__":
    try:
        success = main()
        # Always exit 0 to not block the build process
        # The main installation script will handle actual failures
        log(f"🎯 Diagnostic result: {'SUCCESS' if success else 'WARNING'}")
        log("⏭️  Continuing to package installation...")
        sys.exit(0)
    except Exception as e:
        log(f"⚠️  Diagnostic error: {e}")
        log("⏭️  Continuing anyway...")
        sys.exit(0)