# Environment Variables Setup Guide

## For Development (Local)
Use the `.env` file that's already created:
- Contains development-friendly settings
- Debug mode enabled
- Localhost binding
- Detailed logging

## For Production (files.ybbfoundation.com)

### Option 1: Environment Variables in Hosting Panel
Set these environment variables in your hosting control panel:

```bash
FLASK_ENV=production
FLASK_APP=app.py
SECRET_KEY=ybb-flask-production-secret-key-2024-secure
API_HOST=0.0.0.0
API_PORT=5000
LOG_LEVEL=INFO
MAX_CONTENT_LENGTH=104857600
CORS_ORIGINS=https://files.ybbfoundation.com,https://ybbfoundation.com
# PYTHONPATH=/home/yourusername/public_html  # Only if not using virtual environment
```

### Option 2: Upload .env.production File
1. Rename `.env.production` to `.env`
2. Update the `SECRET_KEY` with a secure random string
3. Upload to your hosting root directory

## Important Notes:

### 🔐 Security
- **MUST** change the `SECRET_KEY` in production
- Set restrictive `CORS_ORIGINS` for production
- Never commit `.env` files to version control

### 🚀 Performance
- Production uses smaller chunk sizes for better memory management
- Reduced timeout values for faster response times
- Higher log retention for monitoring

### 📝 Logging
- Development: DEBUG level with console output
- Production: INFO level, file-only logging
- Larger log files and longer retention in production

## Quick Test Commands:

```bash
# Test development setup
python app.py

# Test configuration loading
python -c "from config import get_config; print(get_config().__dict__)"
```
