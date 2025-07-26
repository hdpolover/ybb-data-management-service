#!/bin/bash
# Railway startup script for YBB Data Management Service

# Activate virtual environment
source /opt/venv/bin/activate

# Set environment variables
export FLASK_ENV=production
export FLASK_APP=app.py

# Start the application with gunicorn
exec gunicorn wsgi:application \
    --bind 0.0.0.0:${PORT:-5000} \
    --workers 2 \
    --timeout 120 \
    --preload \
    --access-logfile - \
    --error-logfile -
