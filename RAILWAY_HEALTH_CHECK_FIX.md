# Railway Health Check Failure - Complete Fix Guide

## 🚨 Current Issue
Railway deployment is failing with health check timeouts:
- Service builds successfully
- Health check at `/health` fails with "service unavailable"
- Multiple retry attempts all fail within the timeout window

## 🔍 Root Cause Analysis

The health check failure is likely caused by one of these issues:

1. **Port Binding Issues**: App not binding to Railway's `$PORT` environment variable
2. **Startup Time**: App taking longer than the health check timeout to start
3. **Import/Dependency Issues**: Missing or failing imports causing startup failures
4. **WSGI Configuration**: Gunicorn or WSGI configuration issues

## 🔧 Applied Fixes

### 1. Simplified Startup Script (`railway_start.py`)
```python
#!/usr/bin/env python3
"""
Simple and reliable Railway startup script
"""
import os
import sys

# Set production environment
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_APP', 'app')

# Ensure proper path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main startup function for Railway"""
    try:
        from app import app
        
        # Get port from Railway's environment variable
        port = int(os.environ.get('PORT', 5000))
        host = '0.0.0.0'
        
        print(f"=== YBB Data Management Service ===")
        print(f"Environment: {os.environ.get('FLASK_ENV', 'unknown')}")
        print(f"Host: {host}")
        print(f"Port: {port}")
        print(f"Starting server...")
        
        # Start Flask with production settings
        app.run(
            host=host,
            port=port,
            debug=False,
            threaded=True,
            use_reloader=False
        )
        
    except Exception as e:
        print(f"STARTUP ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
```

### 2. Updated Railway Configuration (`railway.toml`)
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = ". /opt/venv/bin/activate && python railway_start.py"
healthcheckPath = "/health"
healthcheckTimeout = 120
restartPolicyType = "on_failure"

[env]
PYTHONPATH = "/app"
FLASK_APP = "app.py"
FLASK_ENV = "production"
```

### 3. Fixed WSGI Configuration (`wsgi.py`)
```python
#!/usr/bin/env python3
"""
Production startup script for YBB Data Management Service
"""
import os
import sys

# Set production environment variables if not already set
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_APP', 'app.py')

def create_application():
    """Create and return the Flask application"""
    try:
        from app import app
        
        print(f"SUCCESS: YBB Data Management Service loaded successfully")
        print(f"   Environment: {os.environ.get('FLASK_ENV', 'unknown')}")
        print(f"   Port: {os.environ.get('PORT', '5000')}")
        print(f"   Debug mode: {app.config.get('DEBUG', False)}")
        
        return app
        
    except Exception as e:
        print(f"ERROR: FATAL ERROR: Failed to create application: {e}")
        import traceback
        traceback.print_exc()
        raise e

# Create the application instance for WSGI servers (like gunicorn)
application = create_application()
app = application
```

## 🚀 Alternative Deployment Strategies

### Option A: Use Gunicorn (Recommended)
Update `railway.toml`:
```toml
[deploy]
startCommand = ". /opt/venv/bin/activate && gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --preload --access-logfile - --error-logfile -"
```

### Option B: Use Flask Development Server (Fallback)
Keep current configuration with `railway_start.py`

### Option C: Use Alternative WSGI Server
```toml
[deploy]
startCommand = ". /opt/venv/bin/activate && waitress-serve --host=0.0.0.0 --port=$PORT wsgi:application"
```

## 🔍 Debugging Railway Issues

### Check Railway Logs
1. Go to Railway dashboard
2. Select your service
3. Click on "Deployments"
4. Check the latest deployment logs for startup errors

### Common Log Patterns to Look For:
- `ImportError`: Missing dependencies
- `ModuleNotFoundError`: Import path issues
- `Address already in use`: Port binding conflicts
- `Permission denied`: File permission issues
- `Timeout`: Health check taking too long

### Manual Health Check Test
Once deployed, test health endpoint directly:
```bash
curl https://your-railway-app-url.up.railway.app/health
```

## 📝 Deployment Checklist

- [x] Fixed `railway.toml` to use correct startup command
- [x] Created reliable `railway_start.py` script
- [x] Fixed WSGI imports in `wsgi.py`
- [x] Removed Unicode characters that cause encoding issues
- [x] Ensured proper port binding to `$PORT` environment variable
- [x] Set reasonable health check timeout (120 seconds)
- [ ] Deploy to Railway and monitor logs
- [ ] Test health endpoint after successful deployment
- [ ] Test export endpoints with sample data

## 🔄 Next Steps

1. **Commit and Push Changes**:
   ```bash
   git add .
   git commit -m "Fix Railway deployment configuration and health check issues"
   git push
   ```

2. **Monitor Railway Deployment**:
   - Watch the deployment logs in Railway dashboard
   - Look for startup success messages
   - Wait for health check to pass

3. **Test After Deployment**:
   ```bash
   # Test health endpoint
   curl https://your-app.up.railway.app/health
   
   # Test export endpoint
   curl -X POST -H "Content-Type: application/json" \
        -d '{"data":[{"full_name":"Test","email":"test@test.com"}]}' \
        https://your-app.up.railway.app/api/ybb/export/participants
   ```

## 🛟 Emergency Rollback

If the deployment still fails, you can quickly rollback by updating `railway.toml`:

```toml
[deploy]
startCommand = ". /opt/venv/bin/activate && python -m flask run --host=0.0.0.0 --port=$PORT"
healthcheckPath = "/health"
healthcheckTimeout = 60
```

This uses Flask's built-in server with minimal configuration.

---
**Status**: ✅ Ready for deployment  
**Updated**: August 15, 2025  
**Priority**: High - Fixes production service availability
