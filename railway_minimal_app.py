"""
Ultra-minimal Railway app that should always work
Handles missing dependencies gracefully with fallbacks
"""
import os
import sys
from datetime import datetime
import json
import uuid
import time

# Set production environment
os.environ.setdefault('FLASK_ENV', 'production')

def create_minimal_app():
    """Create a minimal Flask app with fallbacks for missing dependencies"""
    
    try:
        from flask import Flask, jsonify, request, Response
        from flask_cors import CORS
    except ImportError as e:
        print(f"CRITICAL: Flask not available: {e}")
        sys.exit(1)
    
    app = Flask(__name__)
    CORS(app, origins="*")
    
    # Global state for minimal functionality
    app.exports = {}
    
    @app.before_request
    def before_request():
        """Simple request tracking"""
        request.start_time = time.time()
        request.id = str(uuid.uuid4())[:8]
    
    @app.route('/health', methods=['GET'])
    def health():
        """Always-working health check"""
        return jsonify({
            "status": "healthy",
            "service": "YBB Data Management Service",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "mode": "minimal",
            "dependencies": {
                "pandas": _check_import('pandas'),
                "openpyxl": _check_import('openpyxl'),
                "numpy": _check_import('numpy')
            }
        })
    
    @app.route('/api/ybb/export/participants', methods=['POST'])
    def export_participants():
        """Minimal export endpoint with fallbacks"""
        try:
            data = request.get_json()
            if not data or 'data' not in data:
                return jsonify({
                    "status": "error",
                    "message": "Invalid request: missing 'data' field"
                }), 400
            
            # Try full export service first
            if _check_import('pandas') and _check_import('openpyxl'):
                try:
                    return _full_export(data)
                except Exception as e:
                    print(f"Full export failed: {e}")
            
            # Fallback to minimal CSV export
            return _minimal_csv_export(data)
            
        except Exception as e:
            return jsonify({
                "status": "error", 
                "message": f"Export failed: {str(e)}"
            }), 500
    
    @app.route('/api/ybb/export/payments', methods=['POST'])
    def export_payments():
        """Forward to participants export"""
        return export_participants()
    
    @app.route('/api/ybb/export/ambassadors', methods=['POST'])
    def export_ambassadors():
        """Forward to participants export"""
        return export_participants()
    
    @app.route('/api/ybb/export/<export_id>/download', methods=['GET'])
    def download_export(export_id):
        """Download endpoint"""
        if export_id not in app.exports:
            return jsonify({"status": "error", "message": "Export not found"}), 404
        
        export_data = app.exports[export_id]
        content = export_data['content']
        filename = export_data['filename']
        
        return Response(
            content,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename="{filename}"'}
        )
    
    @app.route('/api/ybb/export/<export_id>/status', methods=['GET'])
    def export_status(export_id):
        """Status endpoint"""
        if export_id not in app.exports:
            return jsonify({"status": "error", "message": "Export not found"}), 404
        
        export_data = app.exports[export_id]
        return jsonify({
            "status": "success",
            "export_id": export_id,
            "record_count": export_data.get('record_count', 0),
            "created_at": export_data.get('created_at', datetime.now().isoformat())
        })
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Endpoint not found"}), 404
    
    @app.errorhandler(500) 
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500
    
    return app

def _check_import(module_name):
    """Check if a module can be imported"""
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False

def _full_export(data):
    """Try to use full export service"""
    try:
        from services.ybb_export_service import YBBExportService
        service = YBBExportService()
        
        export_data = {
            "export_type": "participants",
            "data": data['data'],
            "template": data.get('template', 'standard'),
            "format": data.get('format', 'excel')
        }
        
        result = service.create_export(export_data)
        return result
        
    except Exception as e:
        print(f"Full export service failed: {e}")
        raise e

def _minimal_csv_export(data):
    """Minimal CSV export using only standard library"""
    from flask import current_app
    
    export_id = str(uuid.uuid4())
    records = data['data']
    
    # Create simple CSV
    if records and isinstance(records[0], dict):
        headers = list(records[0].keys())
        csv_lines = [','.join(f'"{h}"' for h in headers)]
        
        for record in records:
            row = []
            for header in headers:
                value = str(record.get(header, '')).replace('"', '""')
                row.append(f'"{value}"')
            csv_lines.append(','.join(row))
        
        csv_content = '\n'.join(csv_lines)
    else:
        csv_content = '"data"\n' + '\n'.join(f'"{str(r)}"' for r in records)
    
    filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # Store export
    current_app.exports[export_id] = {
        'content': csv_content.encode('utf-8'),
        'filename': filename,
        'record_count': len(records),
        'created_at': datetime.now().isoformat()
    }
    
    return {
        "status": "success",
        "message": "Export completed (minimal mode)",
        "data": {
            "export_id": export_id,
            "file_name": filename,
            "record_count": len(records),
            "download_url": f"/api/ybb/export/{export_id}/download"
        },
        "system_info": {
            "mode": "minimal_csv_fallback",
            "format": "csv"
        }
    }

def main():
    """Main startup function"""
    try:
        app = create_minimal_app()
        
        port = int(os.environ.get('PORT', 5000))
        host = '0.0.0.0'
        
        print("=" * 50)
        print("YBB Data Management Service - MINIMAL MODE")
        print("=" * 50)
        print(f"Host: {host}")
        print(f"Port: {port}")
        print(f"Environment: {os.environ.get('FLASK_ENV', 'unknown')}")
        print(f"Dependencies:")
        print(f"  - pandas: {'✓' if _check_import('pandas') else '✗ (using fallback)'}")
        print(f"  - openpyxl: {'✓' if _check_import('openpyxl') else '✗ (using CSV)'}")
        print(f"  - numpy: {'✓' if _check_import('numpy') else '✗ (not needed for minimal)'}")
        print("=" * 50)
        print("Starting server...")
        
        app.run(
            host=host,
            port=port,
            debug=False,
            threaded=True,
            use_reloader=False
        )
        
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
