"""
YBB API Blueprint - Handles YBB-specific API endpoints
"""
from flask import Blueprint, request, jsonify, send_file
from services.ybb_export_service import YBBExportService
from io import BytesIO
import logging
import json

logger = logging.getLogger(__name__)

# Create blueprint
ybb_bp = Blueprint('ybb', __name__, url_prefix='/api/ybb')

# Initialize service
export_service = YBBExportService()

@ybb_bp.route('/export/participants', methods=['POST'])
def export_participants():
    """
    Export participants data
    
    Expected payload:
    {
        "data": [...],
        "template": "standard|detailed|summary|complete",
        "format": "excel|csv",
        "filters": {...},
        "filename": "optional_custom_filename.xlsx",
        "sheet_name": "Participants"
    }
    """
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
        
        # Add export type
        request_data["export_type"] = "participants"
        
        # Create export
        result = export_service.create_export(request_data)
        
        if result["status"] == "error":
            return jsonify(result), 400
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Participants export failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Export failed: {str(e)}"
        }), 500

@ybb_bp.route('/export/payments', methods=['POST'])
def export_payments():
    """
    Export payments data
    
    Expected payload:
    {
        "data": [...],
        "template": "standard|detailed",
        "format": "excel|csv",
        "filters": {...},
        "filename": "optional_custom_filename.xlsx",
        "sheet_name": "Payments"
    }
    """
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
        
        # Add export type
        request_data["export_type"] = "payments"
        
        # Create export
        result = export_service.create_export(request_data)
        
        if result["status"] == "error":
            return jsonify(result), 400
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Payments export failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Export failed: {str(e)}"
        }), 500

@ybb_bp.route('/export/ambassadors', methods=['POST'])
def export_ambassadors():
    """
    Export ambassadors data
    
    Expected payload:
    {
        "data": [...],
        "template": "standard|detailed",
        "format": "excel|csv",
        "filters": {...},
        "filename": "optional_custom_filename.xlsx",
        "sheet_name": "Ambassadors"
    }
    """
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
        
        # Add export type
        request_data["export_type"] = "ambassadors"
        
        # Create export
        result = export_service.create_export(request_data)
        
        if result["status"] == "error":
            return jsonify(result), 400
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Ambassadors export failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Export failed: {str(e)}"
        }), 500

@ybb_bp.route('/export/<export_id>/status', methods=['GET'])
def get_export_status(export_id):
    """Get export status and details"""
    try:
        result = export_service.get_export_status(export_id)
        
        if result["status"] == "error":
            return jsonify(result), 404
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Export status check failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Status check failed: {str(e)}"
        }), 500

@ybb_bp.route('/export/<export_id>/download', methods=['GET'])
def download_export(export_id):
    """Download complete export file (single file or ZIP archive)"""
    try:
        file_type = request.args.get('type', 'single')
        
        file_content, filename = export_service.download_export(export_id, file_type)
        
        if file_content is None:
            return jsonify({
                "status": "error",
                "message": "Export file not found or expired"
            }), 404
        
        # Determine content type
        if filename.endswith('.zip'):
            content_type = 'application/zip'
        elif filename.endswith('.xlsx'):
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif filename.endswith('.csv'):
            content_type = 'text/csv'
        else:
            content_type = 'application/octet-stream'
        
        return send_file(
            BytesIO(file_content),
            as_attachment=True,
            download_name=filename,
            mimetype=content_type
        )
        
    except Exception as e:
        logger.error(f"Export download failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Download failed: {str(e)}"
        }), 500

@ybb_bp.route('/export/<export_id>/download/zip', methods=['GET'])
def download_export_zip(export_id):
    """Download ZIP archive of multi-file export"""
    try:
        file_content, filename = export_service.download_export(export_id, "zip")
        
        if file_content is None:
            return jsonify({
                "status": "error",
                "message": "ZIP archive not found or expired"
            }), 404
        
        return send_file(
            BytesIO(file_content),
            as_attachment=True,
            download_name=filename,
            mimetype='application/zip'
        )
        
    except Exception as e:
        logger.error(f"ZIP download failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"ZIP download failed: {str(e)}"
        }), 500

@ybb_bp.route('/export/<export_id>/download/batch/<int:batch_number>', methods=['GET'])
def download_batch_file(export_id, batch_number):
    """Download specific batch file from multi-file export"""
    try:
        file_content, filename = export_service.download_batch_file(export_id, batch_number)
        
        if file_content is None:
            return jsonify({
                "status": "error",
                "message": f"Batch file {batch_number} not found or expired"
            }), 404
        
        return send_file(
            BytesIO(file_content),
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        logger.error(f"Batch download failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Batch download failed: {str(e)}"
        }), 500

@ybb_bp.route('/templates', methods=['GET'])
def get_templates():
    """Get available export templates"""
    try:
        from config.ybb_export_config import EXPORT_TEMPLATES
        
        templates = {}
        for export_type, type_templates in EXPORT_TEMPLATES.items():
            templates[export_type] = {}
            for template_name, template_config in type_templates.items():
                templates[export_type][template_name] = {
                    "name": template_name,
                    "description": template_config.get("description", ""),
                    "fields": template_config.get("fields", []),
                    "headers": template_config.get("headers", []),
                    "includes_sensitive_data": template_config.get("includes_sensitive_data", False)
                }
        
        return jsonify({
            "status": "success",
            "data": templates
        }), 200
        
    except Exception as e:
        logger.error(f"Templates retrieval failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Templates retrieval failed: {str(e)}"
        }), 500

@ybb_bp.route('/templates/<export_type>', methods=['GET'])
def get_export_type_templates(export_type):
    """Get templates for specific export type"""
    try:
        from config.ybb_export_config import EXPORT_TEMPLATES
        
        if export_type not in EXPORT_TEMPLATES:
            return jsonify({
                "status": "error",
                "message": f"Export type '{export_type}' not found"
            }), 404
        
        templates = {}
        for template_name, template_config in EXPORT_TEMPLATES[export_type].items():
            templates[template_name] = {
                "name": template_name,
                "description": template_config.get("description", ""),
                "fields": template_config.get("fields", []),
                "headers": template_config.get("headers", []),
                "includes_sensitive_data": template_config.get("includes_sensitive_data", False)
            }
        
        return jsonify({
            "status": "success",
            "export_type": export_type,
            "data": templates
        }), 200
        
    except Exception as e:
        logger.error(f"Export type templates retrieval failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Templates retrieval failed: {str(e)}"
        }), 500

@ybb_bp.route('/status-mappings', methods=['GET'])
def get_status_mappings():
    """Get status mappings for data transformation"""
    try:
        from config.ybb_export_config import STATUS_MAPPINGS
        
        return jsonify({
            "status": "success",
            "data": STATUS_MAPPINGS
        }), 200
        
    except Exception as e:
        logger.error(f"Status mappings retrieval failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Status mappings retrieval failed: {str(e)}"
        }), 500

@ybb_bp.route('/system-config', methods=['GET'])
def get_system_config():
    """Get system configuration limits"""
    try:
        from config.ybb_export_config import SYSTEM_CONFIG
        
        # Return safe subset of config (no sensitive data)
        safe_config = {
            "limits": SYSTEM_CONFIG["limits"],
            "chunk_sizes": SYSTEM_CONFIG["chunk_sizes"],
            "performance": SYSTEM_CONFIG["performance"]
        }
        
        return jsonify({
            "status": "success",
            "data": safe_config
        }), 200
        
    except Exception as e:
        logger.error(f"System config retrieval failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"System config retrieval failed: {str(e)}"
        }), 500

@ybb_bp.route('/cleanup', methods=['POST'])
def cleanup_exports():
    """Clean up expired exports (admin endpoint)"""
    try:
        # In production, add authentication/authorization here
        cleaned_count = export_service.cleanup_expired_exports()
        
        return jsonify({
            "status": "success",
            "message": f"Cleaned up {cleaned_count} expired exports"
        }), 200
        
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Cleanup failed: {str(e)}"
        }), 500

# Error handlers for the blueprint
@ybb_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        "status": "error",
        "message": "Bad request - invalid data format"
    }), 400

@ybb_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": "error",
        "message": "Resource not found"
    }), 404

@ybb_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        "status": "error",
        "message": "Internal server error"
    }), 500
