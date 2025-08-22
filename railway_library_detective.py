#!/usr/bin/env python3
"""
Railway Library Detective - Find and fix C++ library issues
"""

import os
import glob
import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

def log(message, level="INFO"):
    if level == "ERROR":
        logging.error(message)
    elif level == "WARNING":
        logging.warning(message)
    else:
        logging.info(message)

def run_cmd(command, description=""):
    """Run a command and return success, stdout, stderr"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
        success = result.returncode == 0
        return success, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def find_all_libraries():
    """Find all C++ libraries in the system"""
    log("🔍 Scanning entire system for C++ libraries...")
    
    patterns = [
        "/nix/store/*/lib*/libstdc++.so*",
        "/nix/store/*/lib*/libgcc_s.so*",
        "/usr/lib*/libstdc++.so*",
        "/lib*/libstdc++.so*"
    ]
    
    found = {}
    for pattern in patterns:
        matches = glob.glob(pattern)
        for match in matches:
            lib_name = os.path.basename(match)
            if lib_name not in found:
                found[lib_name] = []
            found[lib_name].append(match)
    
    for lib_name, paths in found.items():
        log(f"📚 Found {lib_name}:")
        for path in paths[:3]:  # Show first 3
            log(f"   → {path}")
        if len(paths) > 3:
            log(f"   ... and {len(paths)-3} more")
    
    return found

def test_library_access():
    """Test if libraries are accessible"""
    log("🧪 Testing library access...")
    
    # Test 1: Direct library check
    test_libs = ["libstdc++.so.6", "libgcc_s.so.1"]
    for lib in test_libs:
        success, stdout, stderr = run_cmd(f"ldconfig -p | grep {lib}")
        if success and stdout.strip():
            log(f"✅ {lib} found in ldconfig")
        else:
            log(f"❌ {lib} not found in ldconfig")
    
    # Test 2: Try importing numpy with different library paths
    libraries = find_all_libraries()
    
    if "libstdc++.so.6" in libraries:
        for lib_path in libraries["libstdc++.so.6"][:3]:
            lib_dir = os.path.dirname(lib_path)
            log(f"🔧 Testing with library path: {lib_dir}")
            
            # Set environment
            env = os.environ.copy()
            env['LD_LIBRARY_PATH'] = f"{lib_dir}:{env.get('LD_LIBRARY_PATH', '')}"
            
            # Test numpy import
            cmd = f'LD_LIBRARY_PATH="{lib_dir}" python -c "import numpy; print(\\"✅ Numpy works!\\")"'
            success, stdout, stderr = run_cmd(cmd)
            
            if success:
                log(f"✅ SUCCESS with library path: {lib_dir}")
                return lib_dir
            else:
                log(f"❌ Failed with {lib_dir}: {stderr[:100]}")
    
    return None

def create_library_links():
    """Create symbolic links to make libraries accessible"""
    log("🔗 Creating library links...")
    
    libraries = find_all_libraries()
    link_dir = "/app/lib"
    
    # Create lib directory
    run_cmd(f"mkdir -p {link_dir}")
    
    for lib_name, paths in libraries.items():
        if lib_name.startswith("libstdc++.so") or lib_name.startswith("libgcc_s.so"):
            if paths:
                best_path = paths[0]  # Use first found
                link_path = f"{link_dir}/{lib_name}"
                
                success, stdout, stderr = run_cmd(f"cp {best_path} {link_path}")
                if success:
                    log(f"✅ Copied {lib_name} to {link_path}")
                else:
                    log(f"❌ Failed to copy {lib_name}: {stderr}")

def setup_final_environment():
    """Set up the final working environment"""
    log("🌍 Setting up final environment...")
    
    # Find working library path
    working_path = test_library_access()
    
    if working_path:
        log(f"✅ Found working library path: {working_path}")
        
        # Set permanent environment
        env_content = f"""
export LD_LIBRARY_PATH="{working_path}:$LD_LIBRARY_PATH"
export LIBRARY_PATH="{working_path}:$LIBRARY_PATH"
"""
        
        with open("/app/library_env.sh", "w") as f:
            f.write(env_content)
        
        log("✅ Created /app/library_env.sh")
        return True
    else:
        log("❌ No working library path found")
        create_library_links()
        return False

def main():
    log("🕵️ Railway Library Detective starting...")
    
    # Step 1: Find all libraries
    libraries = find_all_libraries()
    
    # Step 2: Test access
    working_path = test_library_access()
    
    # Step 3: Set up environment
    success = setup_final_environment()
    
    # Step 4: Final test
    if working_path or os.path.exists("/app/lib/libstdc++.so.6"):
        log("🧪 Final numpy test...")
        if working_path:
            cmd = f'LD_LIBRARY_PATH="{working_path}" python -c "import numpy; print(\\"Final test: Numpy import successful!\\")"'
        else:
            cmd = 'LD_LIBRARY_PATH="/app/lib" python -c "import numpy; print(\\"Final test: Numpy import successful!\\")"'
        
        success, stdout, stderr = run_cmd(cmd)
        if success:
            log("🎉 FINAL SUCCESS: Numpy import working!")
            return True
        else:
            log(f"❌ Final test failed: {stderr[:200]}")
    
    log("❌ Library detective investigation failed")
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)