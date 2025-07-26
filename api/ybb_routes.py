"""
YBB API Blueprint - Handles YBB-specific API endpoints
"""
from flask import Blueprint, request, jsonify, send_file, g
from services.ybb_export_service import YBBExportService
from io import BytesIO
import logging
import json
import time

# Setup logging
logger = logging.getLogger('ybb_api.routes')

# Create blueprint
ybb_bp = Blueprint('ybb', __name__, url_prefix='/api/ybb')

# Initialize service
export_service = YBBExportService()

@ybb_bp.before_request
def log_ybb_request():
    """Log YBB-specific request details"""
    request_id = getattr(g, 'request_id', 'unknown')
    
    logger.info(
        f"YBB_REQUEST | ID: {request_id} | "
        f"Endpoint: {request.endpoint} | "
        f"Method: {request.method} | "
        f"Path: {request.path}"
    )
    
    # Log request data for POST requests
    if request.method == 'POST' and request.is_json:
        try:
            data = request.get_json()
            export_type = data.get('export_type', 'unknown')
            template = data.get('template', 'default')
            record_count = len(data.get('data', [])) if 'data' in data else 0
            
            logger.info(
                f"YBB_EXPORT_REQUEST | ID: {request_id} | "
                f"Type: {export_type} | "
                f"Template: {template} | "
                f"Records: {record_count}"
            )
        except Exception as e:
            logger.warning(f"YBB_REQUEST_LOG_ERROR | ID: {request_id} | Error: {str(e)}")

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
    request_id = getattr(g, 'request_id', 'unknown')
    start_time = time.time()
    
    try:
        logger.info(f"PARTICIPANTS_EXPORT_START | ID: {request_id} | Starting participants export")
        
        request_data = request.get_json()
        
        if not request_data:
            logger.error(f"PARTICIPANTS_EXPORT_ERROR | ID: {request_id} | No JSON data provided")
            return jsonify({
                "status": "error",
                "message": "No JSON data provided",
                "request_id": request_id
            }), 400
        
        # Add export type
        request_data["export_type"] = "participants"
        
        # Log export parameters
        template = request_data.get('template', 'standard')
        format_type = request_data.get('format', 'excel')
        record_count = len(request_data.get('data', []))
        
        logger.info(
            f"PARTICIPANTS_EXPORT_PARAMS | ID: {request_id} | "
            f"Template: {template} | Format: {format_type} | Records: {record_count}"
        )
        
        # Create export
        logger.info(f"PARTICIPANTS_EXPORT_PROCESSING | ID: {request_id} | Calling export service")
        result = export_service.create_export(request_data)
        
        if result["status"] == "error":
            logger.error(f"PARTICIPANTS_EXPORT_FAILED | ID: {request_id} | Error: {result.get('message', 'Unknown error')}")
            result["request_id"] = request_id
            return jsonify(result), 400
        
        processing_time = round((time.time() - start_time) * 1000, 2)
        export_id = result.get('data', {}).get('export_id', 'unknown')
        
        # Update metadata with actual processing time
        if result["status"] == "success" and "metadata" in result:
            result["metadata"]["processing_time"] = processing_time / 1000  # Convert to seconds
        
        logger.info(
            f"PARTICIPANTS_EXPORT_SUCCESS | ID: {request_id} | "
            f"Export ID: {export_id} | Time: {processing_time}ms"
        )
        
        result["request_id"] = request_id
        return jsonify(result), 200
        
    except Exception as e:
        processing_time = round((time.time() - start_time) * 1000, 2)
        logger.error(
            f"PARTICIPANTS_EXPORT_EXCEPTION | ID: {request_id} | "
            f"Error: {str(e)} | Time: {processing_time}ms", 
            exc_info=True
        )
        return jsonify({
            "status": "error",
            "message": f"Export failed: {str(e)}",
            "request_id": request_id
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
    request_id = getattr(g, 'request_id', 'unknown')
    start_time = time.time()
    
    try:
        logger.info(f"PAYMENTS_EXPORT_START | ID: {request_id} | Starting payments export")
        
        request_data = request.get_json()
        
        if not request_data:
            logger.error(f"PAYMENTS_EXPORT_ERROR | ID: {request_id} | No JSON data provided")
            return jsonify({
                "status": "error",
                "message": "No JSON data provided",
                "request_id": request_id
            }), 400
        
        # Add export type
        request_data["export_type"] = "payments"
        
        # Log export parameters
        template = request_data.get('template', 'standard')
        format_type = request_data.get('format', 'excel')
        record_count = len(request_data.get('data', []))
        
        logger.info(
            f"PAYMENTS_EXPORT_PARAMS | ID: {request_id} | "
            f"Template: {template} | Format: {format_type} | Records: {record_count}"
        )
        
        # Create export
        logger.info(f"PAYMENTS_EXPORT_PROCESSING | ID: {request_id} | Calling export service")
        result = export_service.create_export(request_data)
        
        if result["status"] == "error":
            logger.error(f"PAYMENTS_EXPORT_FAILED | ID: {request_id} | Error: {result.get('message', 'Unknown error')}")
            result["request_id"] = request_id
            return jsonify(result), 400
        
        processing_time = round((time.time() - start_time) * 1000, 2)
        export_id = result.get('data', {}).get('export_id', 'unknown')
        
        # Update metadata with actual processing time
        if result["status"] == "success" and "metadata" in result:
            result["metadata"]["processing_time"] = processing_time / 1000  # Convert to seconds
        
        logger.info(
            f"PAYMENTS_EXPORT_SUCCESS | ID: {request_id} | "
            f"Export ID: {export_id} | Time: {processing_time}ms"
        )
        
        result["request_id"] = request_id
        return jsonify(result), 200
        
    except Exception as e:
        processing_time = round((time.time() - start_time) * 1000, 2)
        logger.error(
            f"PAYMENTS_EXPORT_EXCEPTION | ID: {request_id} | "
            f"Error: {str(e)} | Time: {processing_time}ms", 
            exc_info=True
        )
        return jsonify({
            "status": "error",
            "message": f"Export failed: {str(e)}",
            "request_id": request_id
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
    request_id = getattr(g, 'request_id', 'unknown')
    start_time = time.time()
    
    try:
        logger.info(f"DOWNLOAD_START | ID: {request_id} | Export ID: {export_id}")
        
        file_type = request.args.get('type', 'single')
        logger.info(f"DOWNLOAD_TYPE | ID: {request_id} | Type: {file_type}")
        
        file_content, filename = export_service.download_export(export_id, file_type)
        
        if file_content is None:
            logger.error(f"DOWNLOAD_NOT_FOUND | ID: {request_id} | Export ID: {export_id}")
            return jsonify({
                "status": "error",
                "message": "Export file not found or expired",
                "request_id": request_id
            }), 404
        
        # Log file details
        file_size = len(file_content)
        processing_time = round((time.time() - start_time) * 1000, 2)
        
        logger.info(
            f"DOWNLOAD_SUCCESS | ID: {request_id} | "
            f"Export ID: {export_id} | Filename: {filename} | "
            f"Size: {file_size} bytes | Time: {processing_time}ms"
        )
        
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
        processing_time = round((time.time() - start_time) * 1000, 2)
        logger.error(
            f"DOWNLOAD_EXCEPTION | ID: {request_id} | "
            f"Export ID: {export_id} | Error: {str(e)} | Time: {processing_time}ms", 
            exc_info=True
        )
        return jsonify({
            "status": "error",
            "message": f"Download failed: {str(e)}",
            "request_id": request_id
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
        cleanup_type = request.json.get('type', 'expired') if request.is_json else 'expired'
        
        if cleanup_type == 'all':
            # Force cleanup all exports
            cleaned_count = export_service.force_cleanup_all_exports()
            message = f"Force cleaned up {cleaned_count} exports"
        else:
            # Clean up only expired exports
            cleaned_count = export_service.cleanup_expired_exports()
            message = f"Cleaned up {cleaned_count} expired exports"
        
        return jsonify({
            "status": "success",
            "message": message,
            "cleaned_count": cleaned_count
        }), 200
        
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Cleanup failed: {str(e)}"
        }), 500

@ybb_bp.route('/storage/info', methods=['GET'])
def get_storage_info():
    """Get storage usage information (admin endpoint)"""
    try:
        storage_info = export_service.get_storage_info()
        
        return jsonify({
            "status": "success",
            "data": storage_info
        }), 200
        
    except Exception as e:
        logger.error(f"Storage info retrieval failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Storage info retrieval failed: {str(e)}"
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
