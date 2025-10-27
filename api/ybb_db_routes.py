"""
Enhanced YBB API Blueprint with Database Integration
Handles YBB-specific API endpoints with direct database connectivity
"""
from flask import Blueprint, request, jsonify, g, Response
from services.database_ybb_export_service import DatabaseYBBExportService
from services.ybb_export_service import YBBExportService
import logging
import json
import time

# Setup logging
logger = logging.getLogger('ybb_api.db_routes')

# Create blueprint
ybb_db_bp = Blueprint('ybb_db', __name__, url_prefix='/api/ybb')

def _as_bool(value):
    """Helper to interpret truthy string/boolean flags"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "on")
    return False

# Initialize services
try:
    db_export_service = DatabaseYBBExportService()
    logger.info("Database export service initialized successfully")
    # Use the same export service instance for downloads
    export_service = db_export_service.export_service
except Exception as e:
    logger.error(f"Failed to initialize database export service: {e}")
    # Fallback to regular export service
    db_export_service = None
    export_service = YBBExportService()

@ybb_db_bp.before_request
def log_ybb_db_request():
    """Log YBB database request details"""
    request_id = getattr(g, 'request_id', 'unknown')
    
    logger.info(
        f"YBB_DB_REQUEST | ID: {request_id} | "
        f"Endpoint: {request.endpoint} | "
        f"Method: {request.method} | "
        f"Path: {request.path}"
    )

@ybb_db_bp.route('/db/export/participants', methods=['POST'])
def export_participants_from_database():
    """
    Export participants data directly from database
    
    Frontend only needs to send:
    {
        "filters": {
            "program_id": 101,
            "status": "approved|pending|rejected|all",
            "country": "USA",
            "date_from": "2025-01-01",
            "date_to": "2025-12-31",
            "search": "search term",
            "limit": 1000
        },
        "options": {
            "template": "standard|detailed|summary|complete",
            "format": "excel|csv",
            "filename": "custom_filename.xlsx",
            "sheet_name": "Participants Data",
            "include_related": true,
            "sort_by": "created_at|name|email",
            "sort_order": "desc|asc"
        }
    }
    """
    request_id = getattr(g, 'request_id', 'unknown')
    start_time = time.time()
    
    try:
        logger.info(f"PARTICIPANTS_DB_EXPORT_START | ID: {request_id}")
        
        if not db_export_service:
            logger.error(f"PARTICIPANTS_DB_EXPORT_ERROR | ID: {request_id} | Database service not available")
            return jsonify({
                "status": "error",
                "message": "Database export service is not available. Please check database configuration.",
                "request_id": request_id
            }), 503
        
        request_data = request.get_json() or {}
        
        # Extract filters and options (copy to avoid mutating request payload)
        filters = dict(request_data.get('filters', {}) or {})
        options = dict(request_data.get('options', {}) or {})
        
        # Determine desired response mode (metadata/JSON by default for frontend compatibility)
        response_mode = request_data.get('response_mode') or request.args.get('response_mode')
        option_response_mode = options.pop('response_mode', None)
        if response_mode is None and option_response_mode is not None:
            response_mode = option_response_mode
        
        metadata_only_flag = request_data.get('metadata_only')
        option_metadata_flag = options.pop('metadata_only', None)
        if response_mode is None and (_as_bool(metadata_only_flag) or _as_bool(option_metadata_flag)):
            response_mode = 'metadata'
        
        # Default to metadata for frontend compatibility (PHP expects JSON with download URL)
        delivery_mode = (response_mode or 'metadata').lower()
        
        # Log export parameters
        logger.info(
            f"PARTICIPANTS_DB_EXPORT_PARAMS | ID: {request_id} | "
            f"Filters: {json.dumps(filters)} | Options: {json.dumps(options)}"
        )
        
        # Call database export service
        result = db_export_service.export_participants_from_db(filters, options)
        
        if result["status"] == "error":
            logger.error(f"PARTICIPANTS_DB_EXPORT_FAILED | ID: {request_id} | Error: {result.get('message', 'Unknown error')}")
            result["request_id"] = request_id
            return jsonify(result), 400
        
        processing_time = round((time.time() - start_time) * 1000, 2)
        export_id = result.get('data', {}).get('export_id', 'unknown')
        
        # Update metadata with actual processing time
        if result["status"] == "success" and "metadata" in result:
            result["metadata"]["processing_time"] = processing_time / 1000
        
        logger.info(
            f"PARTICIPANTS_DB_EXPORT_SUCCESS | ID: {request_id} | "
            f"Export ID: {export_id} | Time: {processing_time}ms | Mode: {delivery_mode}"
        )
        
        if delivery_mode in ('metadata', 'json'):
            result["request_id"] = request_id
            return jsonify(result), 200
        
        try:
            file_content, filename, content_type, export_metadata = db_export_service.prepare_export_file_response(
                result,
                filters=filters,
                options=options
            )
            
            # Validate file content exists
            if not file_content:
                logger.error(f"PARTICIPANTS_DB_EXPORT_NO_CONTENT | ID: {request_id} | Export ID: {export_id}")
                return jsonify({
                    "status": "error",
                    "message": "Export file content is not available",
                    "export_id": export_id,
                    "request_id": request_id
                }), 404
                
        except Exception as prep_error:
            logger.error(
                f"PARTICIPANTS_DB_EXPORT_DELIVERY_FAILED | ID: {request_id} | "
                f"Export ID: {export_id} | Error: {str(prep_error)}",
                exc_info=True
            )
            return jsonify({
                "status": "error",
                "message": f"Export was created but failed during delivery: {str(prep_error)}",
                "export_id": export_id,
                "request_id": request_id
            }), 500
        
        export_metadata["request_id"] = request_id
        export_metadata["processing_time"] = processing_time / 1000
        
        response = Response(file_content, mimetype=content_type)
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.headers['Content-Length'] = str(len(file_content))
        if export_metadata.get('export_id'):
            response.headers['X-Export-Id'] = export_metadata['export_id']
        response.headers['X-Export-Metadata'] = json.dumps(export_metadata, default=str)
        response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition,X-Export-Id,X-Export-Metadata'
        
        logger.info(
            f"PARTICIPANTS_DB_EXPORT_DELIVERED | ID: {request_id} | "
            f"Export ID: {export_id} | Filename: {filename} | Size: {len(file_content)} bytes"
        )
        
        return response
        
    except Exception as e:
        processing_time = round((time.time() - start_time) * 1000, 2)
        logger.error(
            f"PARTICIPANTS_DB_EXPORT_EXCEPTION | ID: {request_id} | "
            f"Error: {str(e)} | Time: {processing_time}ms", 
            exc_info=True
        )
        return jsonify({
            "status": "error",
            "message": f"Export failed: {str(e)}",
            "request_id": request_id
        }), 500

@ybb_db_bp.route('/db/export/payments', methods=['POST'])
def export_payments_from_database():
    """
    Export payments data directly from database
    
    Frontend sends:
    {
        "filters": {
            "participant_id": 123,
            "status": "success|pending|failed|all",
            "payment_method_id": 1,
            "date_from": "2025-01-01",
            "date_to": "2025-12-31",
            "amount_min": 100,
            "amount_max": 500
        },
        "options": {
            "template": "standard|detailed",
            "format": "excel|csv",
            "filename": "custom_filename.xlsx",
            "sheet_name": "Payments Data",
            "include_related": true
        }
    }
    """
    request_id = getattr(g, 'request_id', 'unknown')
    start_time = time.time()
    
    try:
        logger.info(f"PAYMENTS_DB_EXPORT_START | ID: {request_id}")
        
        if not db_export_service:
            return jsonify({
                "status": "error",
                "message": "Database export service is not available",
                "request_id": request_id
            }), 503
        
        request_data = request.get_json() or {}
        
        filters = dict(request_data.get('filters', {}) or {})
        options = dict(request_data.get('options', {}) or {})
        
        response_mode = request_data.get('response_mode') or request.args.get('response_mode')
        option_response_mode = options.pop('response_mode', None)
        if response_mode is None and option_response_mode is not None:
            response_mode = option_response_mode
        
        metadata_only_flag = request_data.get('metadata_only')
        option_metadata_flag = options.pop('metadata_only', None)
        if response_mode is None and (_as_bool(metadata_only_flag) or _as_bool(option_metadata_flag)):
            response_mode = 'metadata'
        
        # Default to metadata for frontend compatibility (PHP expects JSON with download URL)
        delivery_mode = (response_mode or 'metadata').lower()
        
        logger.info(
            f"PAYMENTS_DB_EXPORT_PARAMS | ID: {request_id} | "
            f"Filters: {json.dumps(filters)} | Options: {json.dumps(options)}"
        )
        
        result = db_export_service.export_payments_from_db(filters, options)
        
        if result["status"] == "error":
            logger.error(f"PAYMENTS_DB_EXPORT_FAILED | ID: {request_id} | Error: {result.get('message')}")
            result["request_id"] = request_id
            return jsonify(result), 400
        
        processing_time = round((time.time() - start_time) * 1000, 2)
        export_id = result.get('data', {}).get('export_id', 'unknown')
        
        if result["status"] == "success" and "metadata" in result:
            result["metadata"]["processing_time"] = processing_time / 1000
        
        logger.info(
            f"PAYMENTS_DB_EXPORT_SUCCESS | ID: {request_id} | "
            f"Export ID: {export_id} | Time: {processing_time}ms | Mode: {delivery_mode}"
        )
        
        if delivery_mode in ('metadata', 'json'):
            result["request_id"] = request_id
            return jsonify(result), 200
        
        try:
            file_content, filename, content_type, export_metadata = db_export_service.prepare_export_file_response(
                result,
                filters=filters,
                options=options
            )
            
            # Additional validation for file content
            if not file_content:
                logger.error(
                    f"PAYMENTS_DB_EXPORT_NO_CONTENT | ID: {request_id} | "
                    f"Export ID: {export_id} | File content is empty or None"
                )
                return jsonify({
                    "status": "error",
                    "message": "Export file is not available. The file may have expired or failed to generate.",
                    "export_id": export_id,
                    "request_id": request_id
                }), 404
                
            if not filename:
                logger.warning(f"PAYMENTS_DB_EXPORT_NO_FILENAME | ID: {request_id} | Using default filename")
                filename = f"YBB_Payments_Export_{export_id[:8]}.xlsx"
                
        except Exception as prep_error:
            logger.error(
                f"PAYMENTS_DB_EXPORT_DELIVERY_FAILED | ID: {request_id} | "
                f"Export ID: {export_id} | Error: {str(prep_error)}",
                exc_info=True
            )
            return jsonify({
                "status": "error",
                "message": f"Export was created but failed during delivery: {str(prep_error)}",
                "export_id": export_id,
                "request_id": request_id,
                "details": str(prep_error)
            }), 500
        
        export_metadata["request_id"] = request_id
        export_metadata["processing_time"] = processing_time / 1000
        
        response = Response(file_content, mimetype=content_type)
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.headers['Content-Length'] = str(len(file_content))
        if export_metadata.get('export_id'):
            response.headers['X-Export-Id'] = export_metadata['export_id']
        response.headers['X-Export-Metadata'] = json.dumps(export_metadata, default=str)
        response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition,X-Export-Id,X-Export-Metadata'
        
        logger.info(
            f"PAYMENTS_DB_EXPORT_DELIVERED | ID: {request_id} | "
            f"Export ID: {export_id} | Filename: {filename} | Size: {len(file_content)} bytes"
        )
        
        return response
        
    except Exception as e:
        processing_time = round((time.time() - start_time) * 1000, 2)
        logger.error(
            f"PAYMENTS_DB_EXPORT_EXCEPTION | ID: {request_id} | "
            f"Error: {str(e)} | Time: {processing_time}ms", 
            exc_info=True
        )
        return jsonify({
            "status": "error",
            "message": f"Export failed: {str(e)}",
            "request_id": request_id
        }), 500

@ybb_db_bp.route('/db/export/statistics', methods=['POST'])
def get_export_statistics():
    """
    Get export statistics before performing actual export
    
    Request:
    {
        "export_type": "participants|payments",
        "filters": {...}
    }
    """
    request_id = getattr(g, 'request_id', 'unknown')
    
    try:
        if not db_export_service:
            return jsonify({
                "status": "error",
                "message": "Database service not available",
                "request_id": request_id
            }), 503
        
        request_data = request.get_json() or {}
        export_type = request_data.get('export_type', 'participants')
        filters = request_data.get('filters', {})
        
        result = db_export_service.get_export_statistics(export_type, filters)
        result["request_id"] = request_id
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"EXPORT_STATISTICS_ERROR | ID: {request_id} | Error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Statistics failed: {str(e)}",
            "request_id": request_id
        }), 500

@ybb_db_bp.route('/db/test-connection', methods=['GET'])
def test_database_connection():
    """Test database connection"""
    request_id = getattr(g, 'request_id', 'unknown')
    
    try:
        if not db_export_service:
            return jsonify({
                "status": "error",
                "message": "Database service not initialized",
                "request_id": request_id
            }), 503
        
        result = db_export_service.test_database_connection()
        result["request_id"] = request_id
        
        return jsonify(result), 200 if result['status'] == 'success' else 500
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Connection test failed: {str(e)}",
            "request_id": request_id
        }), 500

# Use the same download endpoints from the original blueprint
@ybb_db_bp.route('/export/<export_id>/download', methods=['GET'])
def download_export(export_id):
    """Download exported file (reuse from original service)"""
    request_id = getattr(g, 'request_id', 'unknown')
    start_time = time.time()
    
    try:
        logger.info(f"DOWNLOAD_START | ID: {request_id} | Export ID: {export_id}")
        
        # Use shared export service for downloads
        file_content, filename = export_service.download_export(export_id, 'single')
        
        if file_content is None:
            logger.error(f"DOWNLOAD_NOT_FOUND | ID: {request_id} | Export ID: {export_id}")
            return jsonify({
                "status": "error",
                "message": "Export file not found or expired. The file may have been cleaned up or never existed.",
                "export_id": export_id,
                "request_id": request_id,
                "suggestion": "Please create a new export"
            }), 404
        
        if not filename:
            logger.warning(f"DOWNLOAD_NO_FILENAME | ID: {request_id} | Export ID: {export_id} | Using default filename")
            filename = f"export_{export_id[:8]}.xlsx"
        
        file_size = len(file_content)
        processing_time = round((time.time() - start_time) * 1000, 2)
        
        logger.info(
            f"DOWNLOAD_SUCCESS | ID: {request_id} | "
            f"Export ID: {export_id} | Filename: {filename} | "
            f"Size: {file_size} bytes | Time: {processing_time}ms"
        )
        
        # Determine content type
        if filename.endswith('.xlsx'):
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif filename.endswith('.csv'):
            content_type = 'text/csv'
        else:
            content_type = 'application/octet-stream'
        
        # Validate file content
        if len(file_content) < 100:
            logger.error(f"DOWNLOAD_FILE_TOO_SMALL | ID: {request_id} | Size: {len(file_content)} bytes")
            return jsonify({
                "status": "error",
                "message": "Generated file appears to be corrupted (too small)",
                "request_id": request_id
            }), 500
        
        if filename.endswith('.xlsx') and not file_content.startswith(b'PK'):
            logger.error(f"DOWNLOAD_INVALID_EXCEL | ID: {request_id} | Missing PK header")
            return jsonify({
                "status": "error",
                "message": "Generated Excel file appears to be corrupted (invalid header)",
                "request_id": request_id
            }), 500
        
        # Clean filename
        safe_filename = filename.replace(' ', '_').replace('(', '').replace(')', '')
        safe_filename = ''.join(c for c in safe_filename if c.isalnum() or c in '._-')
        
        response = Response(
            file_content,
            mimetype=content_type,
            headers={
                'Content-Disposition': f'attachment; filename="{safe_filename}"',
                'Content-Length': str(len(file_content)),
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        )
        
        return response
        
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

@ybb_db_bp.route('/export/<export_id>/status', methods=['GET'])
def get_export_status(export_id):
    """Get export status (reuse from original service)"""
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
