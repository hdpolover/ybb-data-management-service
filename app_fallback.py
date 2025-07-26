"""
Fallback app.py for production deployment with numpy/pandas issues
"""
from flask import Flask, request, jsonify, g
from flask_cors import CORS
import json
import os
from datetime import datetime
import tempfile
from io import BytesIO
import logging
import uuid
import time
import sys

# Try to import pandas/numpy, use fallback if failed
try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Warning: Pandas/Numpy not available: {str(e)}")
    PANDAS_AVAILABLE = False

# Flask app initialization
app = Flask(__name__)
CORS(app, origins="*")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Basic health check route
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "YBB Data Processing Service",
        "version": "1.0.0",
        "pandas_available": PANDAS_AVAILABLE,
        "request_id": str(uuid.uuid4())[:8]
    })

# Temporary export endpoint that works without pandas
@app.route('/api/ybb/export/participants', methods=['POST'])
def export_participants_fallback():
    """Temporary export endpoint that doesn't require pandas"""
    try:
        data = request.get_json()
        export_id = str(uuid.uuid4())
        
        # Create a simple CSV without pandas
        csv_content = "id,name,email\n"
        for item in data.get('data', []):
            csv_content += f"{item.get('id', '')},{item.get('name', '')},{item.get('email', '')}\n"
        
        # Store in memory (temporary solution)
        if not hasattr(app, 'exports_storage'):
            app.exports_storage = {}
            
        app.exports_storage[export_id] = {
            'content': csv_content.encode('utf-8'),
            'filename': data.get('filename', f'export_{export_id}.csv'),
            'created_at': datetime.now()
        }
        
        return jsonify({
            "status": "success",
            "message": "Export completed successfully (fallback mode)",
            "data": {
                "export_id": export_id,
                "file_name": data.get('filename', f'export_{export_id}.csv'),
                "file_size": len(csv_content),
                "record_count": len(data.get('data', [])),
                "download_url": f"/api/ybb/export/{export_id}/download"
            }
        })
        
    except Exception as e:
        logger.error(f"Export failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Export failed: {str(e)}"
        }), 500

# Download endpoint
@app.route('/api/ybb/export/<export_id>/download', methods=['GET'])
def download_export_fallback(export_id):
    """Download export file"""
    try:
        if not hasattr(app, 'exports_storage') or export_id not in app.exports_storage:
            return jsonify({
                "status": "error",
                "message": "Export file not found or expired"
            }), 404
            
        export_info = app.exports_storage[export_id]
        
        return send_file(
            BytesIO(export_info['content']),
            as_attachment=True,
            download_name=export_info['filename'],
            mimetype='text/csv'
        )
        
    except Exception as e:
        logger.error(f"Download failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Download failed: {str(e)}"
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "method": request.method,
        "url": request.url,
        "request_id": str(uuid.uuid4())[:8]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "request_id": str(uuid.uuid4())[:8]
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
