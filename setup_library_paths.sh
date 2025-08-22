#!/bin/bash
# Railway Library Path Setup
# Dynamically find and set C++ library paths

echo "[SETUP] 🔍 Setting up dynamic library paths..."

# Find actual libstdc++.so.6 locations
LIBSTDCPP_PATHS=$(find /nix/store -name "libstdc++.so.6*" -type f 2>/dev/null | head -5)
LIBGCC_PATHS=$(find /nix/store -name "libgcc_s.so*" -type f 2>/dev/null | head -5)

echo "[SETUP] Found libstdc++ files:"
echo "$LIBSTDCPP_PATHS"

# Extract unique directory paths
LIB_DIRS=""
for lib_file in $LIBSTDCPP_PATHS $LIBGCC_PATHS; do
    if [ -f "$lib_file" ]; then
        lib_dir=$(dirname "$lib_file")
        if [[ ":$LIB_DIRS:" != *":$lib_dir:"* ]]; then
            LIB_DIRS="$LIB_DIRS:$lib_dir"
        fi
    fi
done

# Clean up the path (remove leading colon)
LIB_DIRS=${LIB_DIRS#:}

if [ -n "$LIB_DIRS" ]; then
    echo "[SETUP] ✅ Setting library paths to: $LIB_DIRS"
    export LD_LIBRARY_PATH="$LIB_DIRS:$LD_LIBRARY_PATH"
    export LIBRARY_PATH="$LIB_DIRS:$LIBRARY_PATH"
    
    # Test if libstdc++.so.6 can be found
    if ldconfig -p | grep -q "libstdc++.so.6"; then
        echo "[SETUP] ✅ libstdc++.so.6 is now accessible"
    else
        echo "[SETUP] ⚠️ libstdc++.so.6 may still not be accessible"
    fi
else
    echo "[SETUP] ❌ No C++ library paths found"
fi

echo "[SETUP] 🎯 Library path setup complete"