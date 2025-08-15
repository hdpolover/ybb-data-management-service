#!/bin/bash
# Railway startup script for YBB Data Management Service - Numpy Fix

# Activate virtual environment if it exists
if [ -d "/opt/venv" ]; then
    source /opt/venv/bin/activate
fi

# Set environment variables
export FLASK_ENV=production
export FLASK_APP=app.py
export PYTHONPATH=/app

# Start the complete application with numpy fixes
# Start the complete application with ultimate numpy fix
exec python railway_ultimate_fix.py
