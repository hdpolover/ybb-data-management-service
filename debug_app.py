#!/usr/bin/env python3
"""
Simple Flask app test for debugging 500 errors
"""
import sys
import os
import traceback

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Starting Flask app test...")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path[:3]}")

try:
    print("1. Importing Flask...")
    from flask import Flask
    print("✓ Flask imported successfully")
    
    print("2. Testing configuration import...")
    from config import get_config
    config = get_config()
    print(f"✓ Configuration loaded: {config.__class__.__name__}")
    
    print("3. Testing YBB routes import...")
    from api.ybb_routes import ybb_bp
    print("✓ YBB routes imported successfully")
    
    print("4. Creating Flask app...")
    app = Flask(__name__)
    app.config.from_object(config)
    print("✓ Flask app created successfully")
    
    print("5. Testing basic route...")
    @app.route('/test')
    def test_route():
        return {'status': 'success', 'message': 'Flask app is working!'}
    
    print("6. Testing app startup...")
    if __name__ == '__main__':
        print("✓ All imports successful!")
        print("Starting Flask development server...")
        app.run(debug=True, host='0.0.0.0', port=5000)
        
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print(f"Missing module: {e.name if hasattr(e, 'name') else 'unknown'}")
    traceback.print_exc()
except Exception as e:
    print(f"❌ Error: {e}")
    traceback.print_exc()
