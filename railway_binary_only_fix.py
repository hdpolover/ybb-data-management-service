#!/usr/bin/env python3
"""
Railway Binary-Only Pandas Fix
Ensures pandas/numpy work using pre-compiled binary wheels only
Avoids all compilation and Fortran dependencies
"""

import subprocess
import sys
import os
import json
from datetime import datetime

def log_message(message, level="INFO"):
    """Enhanced logging with timestamps"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def run_command(command, description):
    """Run command with enhanced error handling"""
    log_message(f"Running: {description}")
    log_message(f"Command: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            log_message(f"✅ SUCCESS: {description}")
            if result.stdout.strip():
                log_message(f"Output: {result.stdout.strip()}")
        else:
            log_message(f"❌ FAILED: {description}", "ERROR")
            log_message(f"Error: {result.stderr.strip()}", "ERROR")
            
        return result.returncode == 0, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        log_message(f"⏱️ TIMEOUT: {description}", "ERROR")
        return False, "", "Command timed out"
    except Exception as e:
        log_message(f"💥 EXCEPTION: {description} - {e}", "ERROR")
        return False, "", str(e)

def check_system_libraries():
    """Check if required system libraries are available"""
    log_message("🔍 Checking system libraries...")
    
    libraries = [
        "openblas",
        "lapack", 
        "blas"
    ]
    
    available = []
    missing = []
    
    for lib in libraries:
        success, stdout, stderr = run_command(f"pkg-config --exists {lib}", f"Check {lib}")
        if success:
            available.append(lib)
        else:
            missing.append(lib)
    
    log_message(f"📊 Available libraries: {available}")
    if missing:
        log_message(f"⚠️ Missing libraries: {missing}", "WARNING")
    
    return len(available) > 0

def install_binary_only_packages():
    """Install packages using binary wheels only"""
    log_message("📦 Installing binary-only packages...")
    
    # Core packages with exact versions known to work
    packages = [
        "pip==24.2",
        "setuptools==75.1.0", 
        "wheel==0.44.0",
        "numpy==1.26.4",
        "pandas==2.2.2",
        "openpyxl==3.1.5",
        "xlsxwriter==3.2.0"
    ]
    
    # Install each package individually with strict binary-only policy
    for package in packages:
        command = f"pip install --only-binary=all --no-compile --no-cache-dir --force-reinstall {package}"
        success, stdout, stderr = run_command(command, f"Install {package}")
        
        if not success:
            log_message(f"❌ Failed to install {package}", "ERROR")
            return False
    
    log_message("✅ All core packages installed successfully")
    return True

def install_optional_packages():
    """Install optional packages for enhanced functionality"""
    log_message("🎯 Installing optional enhancement packages...")
    
    optional_packages = [
        "flask==3.0.3",
        "sqlalchemy==2.0.23",
        "pymysql==1.1.1",
        "python-dotenv==1.0.1",
        "werkzeug==3.0.4"
    ]
    
    success_count = 0
    for package in optional_packages:
        command = f"pip install --only-binary=all --no-compile --no-cache-dir {package}"
        success, stdout, stderr = run_command(command, f"Install optional {package}")
        
        if success:
            success_count += 1
        else:
            log_message(f"⚠️ Optional package {package} failed - continuing", "WARNING")
    
    log_message(f"📊 Installed {success_count}/{len(optional_packages)} optional packages")
    return success_count > 0

def test_pandas_functionality():
    """Test core pandas functionality"""
    log_message("🧪 Testing pandas functionality...")
    
    test_code = '''
import sys
import numpy as np
import pandas as pd
import openpyxl
import xlsxwriter

print(f"✅ Python: {sys.version}")
print(f"✅ NumPy: {np.__version__}")
print(f"✅ Pandas: {pd.__version__}")
print(f"✅ OpenPyXL: {openpyxl.__version__}")
print(f"✅ XlsxWriter: {xlsxwriter.__version__}")

# Test basic DataFrame operations
df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, 30, 35],
    "Score": [95.5, 87.2, 92.8]
})

print(f"✅ DataFrame creation: {len(df)} rows")

# Test Excel export (in-memory)
import io
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Test", index=False)

print(f"✅ Excel export: {len(excel_buffer.getvalue())} bytes")

# Test statistical operations
stats = df["Score"].describe()
print(f"✅ Statistics: mean={stats['mean']:.2f}")

# Test memory usage
memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
print(f"✅ Memory usage: {memory_mb:.4f} MB")

print("🎉 ALL TESTS PASSED - PANDAS FULLY FUNCTIONAL!")
'''
    
    success, stdout, stderr = run_command(f'python -c "{test_code}"', "Test pandas functionality")
    
    if success:
        log_message("✅ Pandas functionality test PASSED")
        return True
    else:
        log_message("❌ Pandas functionality test FAILED", "ERROR")
        log_message(f"Error details: {stderr}", "ERROR")
        return False

def generate_diagnostic_report():
    """Generate comprehensive diagnostic report"""
    log_message("📋 Generating diagnostic report...")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "python_version": sys.version,
        "platform": sys.platform,
        "executable": sys.executable,
        "packages": {},
        "system_info": {}
    }
    
    # Check installed packages
    packages_to_check = ["numpy", "pandas", "openpyxl", "xlsxwriter", "flask"]
    
    for package in packages_to_check:
        try:
            module = __import__(package)
            report["packages"][package] = {
                "version": getattr(module, "__version__", "unknown"),
                "location": getattr(module, "__file__", "unknown"),
                "status": "✅ OK"
            }
        except ImportError as e:
            report["packages"][package] = {
                "status": f"❌ FAILED: {e}",
                "error": str(e)
            }
    
    # System information
    report["system_info"]["environment_variables"] = {
        "PYTHONPATH": os.environ.get("PYTHONPATH", "not set"),
        "LD_LIBRARY_PATH": os.environ.get("LD_LIBRARY_PATH", "not set"),
        "BLAS": os.environ.get("BLAS", "not set"),
        "LAPACK": os.environ.get("LAPACK", "not set")
    }
    
    # Save report
    report_file = "railway_diagnostic_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    log_message(f"📄 Diagnostic report saved to: {report_file}")
    
    # Print summary
    log_message("📊 DIAGNOSTIC SUMMARY:")
    for package, info in report["packages"].items():
        log_message(f"  {package}: {info['status']}")
    
    return report

def main():
    """Main execution flow"""
    log_message("🚀 Starting Railway Binary-Only Pandas Fix")
    log_message("=" * 60)
    
    # Step 1: Check system libraries
    if not check_system_libraries():
        log_message("⚠️ Some system libraries missing - continuing with binary wheels", "WARNING")
    
    # Step 2: Install core packages
    if not install_binary_only_packages():
        log_message("💥 CRITICAL: Core package installation failed", "ERROR")
        sys.exit(1)
    
    # Step 3: Install optional packages
    install_optional_packages()
    
    # Step 4: Test functionality
    if not test_pandas_functionality():
        log_message("💥 CRITICAL: Pandas functionality test failed", "ERROR")
        sys.exit(1)
    
    # Step 5: Generate report
    report = generate_diagnostic_report()
    
    log_message("=" * 60)
    log_message("🎉 RAILWAY BINARY-ONLY PANDAS FIX COMPLETED SUCCESSFULLY!")
    log_message("✅ Pandas is now fully functional with binary wheels")
    log_message("✅ No compilation or Fortran dependencies required")
    log_message("✅ Ready for production use")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        log_message("🛑 Installation interrupted by user", "WARNING")
        sys.exit(1)
    except Exception as e:
        log_message(f"💥 Unexpected error: {e}", "ERROR")
        sys.exit(1)