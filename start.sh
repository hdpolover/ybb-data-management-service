#!/bin/bash
# Railway startup script for YBB Data Management Service - Complete Mode

# Activate virtual environment if it exists
if [ -d "/opt/venv" ]; then
    source /opt/venv/bin/activate
fi

# Set environment variables
export FLASK_ENV=production
export FLASK_APP=app.py
export PYTHONPATH=/app

# Start the complete application directly
exec python railway_simple.py
