"""
Database-Direct YBB Routes - High Performance Export Endpoints
Eliminates JSON payload limitations by querying database directly
"""
from flask import Blueprint, request, jsonify, g
from services.db_export_service import DatabaseExportService
import logging
import json
import time

# Setup logging
logger = logging.getLogger('ybb_api.db_routes')

# Create blueprint for database-direct endpoints
ybb_db_bp = Blueprint('ybb_db', __name__, url_prefix='/api/ybb/db')

# Initialize database export service
db_export_service = DatabaseExportService()

# Initialize participant export service
from services.participant_export_service import participant_export_service

@ybb_db_bp.before_request
def log_db_request():
    """Log database-direct request details"""
    request_id = getattr(g, 'request_id', 'unknown')
    
    logger.info(
        f"DB_DIRECT_REQUEST | ID: {request_id} | "
        f"Endpoint: {request.endpoint} | "
        f"Method: {request.method} | "
        f"Path: {request.path}"
    )

@ybb_db_bp.route('/export/participants', methods=['POST'])
def export_participants_direct():
    """
    Export participants directly from database with complex filters
    
    Expected payload:
    {
        "program_id": 123,  // Required
        "template": "standard",  // basic, standard, detailed, complete
        "filters": {
            "category": ["self_funded", "fully_funded"],
            "form_status": [0, 1, 2],  // 0=not started, 1=in_progress, 2=submitted
            "payment_done": [1, 2, 3],  // array of program payment ids
            "with_essay": true,  // boolean
            "created_at": {
                "min": "2024-01-01",
                "max": "2024-12-31"
            }
        },
        "filename": "participants_2024_export",
        "chunk_size": 4000,
        "force_chunking": false
    }
    """
    request_id = getattr(g, 'request_id', 'unknown')
    start_time = time.time()
    
    try:
        logger.info(f"PARTICIPANT_EXPORT_START | ID: {request_id}")
        
        request_data = request.get_json()
        
        if not request_data:
            logger.error(f"PARTICIPANT_EXPORT_ERROR | ID: {request_id} | No JSON data provided")
            return jsonify({
                "status": "error",
                "message": "No JSON data provided",
                "request_id": request_id
            }), 400
        
        # Extract parameters - program_id is required
        program_id = request_data.get('program_id')
        if not program_id:
            logger.error(f"PARTICIPANT_EXPORT_ERROR | ID: {request_id} | Missing program_id")
            return jsonify({
                "status": "error",
                "message": "program_id is required for participant export",
                "request_id": request_id
            }), 400
        
        # Always use detailed export - no template needed
        filters = request_data.get('filters', {})
        filename = request_data.get('filename', f'participants_program_{program_id}_export')
        chunk_size = request_data.get('chunk_size')
        force_chunking = request_data.get('force_chunking', False)
        
        # Log export parameters
        logger.info(
            f"PARTICIPANT_EXPORT_PARAMS | ID: {request_id} | Program: {program_id} | "
            f"Filters: {len(filters)} | Force chunking: {force_chunking} | Chunk size: {chunk_size}"
        )
        
        # Create export using specialized participant service
        export_config = {
            "program_id": program_id,
            "filters": filters,
            "filename": filename,
            "chunk_size": chunk_size,
            "force_chunking": force_chunking
        }
        
        logger.info(f"PARTICIPANT_EXPORT_PROCESSING | ID: {request_id} | Calling participant export service")
        result = participant_export_service.create_participant_export(
            program_id=program_id,
            filters=filters,
            force_chunking=force_chunking,
            chunk_size=chunk_size
        )
        
        if result["status"] == "error":
            logger.error(f"PARTICIPANT_EXPORT_FAILED | ID: {request_id} | Error: {result.get('message')}")
            result["request_id"] = request_id
            return jsonify(result), 400
        
        processing_time = round((time.time() - start_time) * 1000, 2)
        export_id = result.get('data', {}).get('export_id', 'unknown')
        record_count = result.get('data', {}).get('record_count') or result.get('data', {}).get('total_records', 0)
        
        # Check if we have direct file content to download
        export_data = participant_export_service.exports_storage.get(export_id)
        if export_data and 'content' in export_data:
            # Return Excel file directly for download
            filename = export_data.get('filename', f'participants_{export_id}.xlsx')
            
            logger.info(
                f"PARTICIPANT_EXPORT_DOWNLOAD | ID: {request_id} | "
                f"Export ID: {export_id} | Records: {record_count} | Time: {processing_time}ms"
            )
            
            from flask import Response
            return Response(
                export_data['content'],
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                headers={
                    'Content-Disposition': f'attachment; filename={filename}',
                    'Content-Length': str(len(export_data['content']))
                }
            )
        else:
            # Return JSON metadata (for chunked exports or errors)
            if "performance_metrics" in result:
                result["performance_metrics"]["api_response_time_ms"] = processing_time
            
            logger.info(
                f"PARTICIPANT_EXPORT_SUCCESS | ID: {request_id} | "
                f"Export ID: {export_id} | Records: {record_count} | Time: {processing_time}ms"
            )
            
            result["request_id"] = request_id
            return jsonify(result), 200
        
    except Exception as e:
        processing_time = round((time.time() - start_time) * 1000, 2)
        logger.error(
            f"DB_PARTICIPANTS_EXPORT_EXCEPTION | ID: {request_id} | "
            f"Error: {str(e)} | Time: {processing_time}ms", 
            exc_info=True
        )
        return jsonify({
            "status": "error",
            "message": f"Database export failed: {str(e)}",
            "request_id": request_id
        }), 500

@ybb_db_bp.route('/export/payments', methods=['POST'])
def export_payments_direct():
    """Export payments directly from database"""
    request_id = getattr(g, 'request_id', 'unknown')
    start_time = time.time()
    
    try:
        logger.info(f"DB_PAYMENTS_EXPORT_START | ID: {request_id}")
        
        request_data = request.get_json()
        if not request_data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided",
                "request_id": request_id
            }), 400
        
        # Get estimated record count
        filters = request_data.get('filters', {})
        total_records = db_export_service.get_export_record_count('payments', filters)
        
        if total_records == 0:
            return jsonify({
                "status": "error",
                "message": "No payment records found matching filters",
                "request_id": request_id
            }), 400
        
        # Process export
        export_config = {
            "export_type": "payments",
            "template": request_data.get('template', 'standard'),
            "filters": filters,
            "filename": request_data.get('filename', 'payments_export'),
            "chunk_size": request_data.get('chunk_size'),
            "force_chunking": request_data.get('force_chunking', False),
            "processing_mode": "database_direct",
            "total_records": total_records
        }
        
        result = db_export_service.create_database_export(export_config)
        
        processing_time = round((time.time() - start_time) * 1000, 2)
        if result["status"] == "success":
            logger.info(f"DB_PAYMENTS_EXPORT_SUCCESS | ID: {request_id} | Time: {processing_time}ms")
        
        result["request_id"] = request_id
        return jsonify(result), 200 if result["status"] == "success" else 400
        
    except Exception as e:
        logger.error(f"DB_PAYMENTS_EXPORT_EXCEPTION | ID: {request_id} | Error: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": f"Database export failed: {str(e)}",
            "request_id": request_id
        }), 500

@ybb_db_bp.route('/export/ambassadors', methods=['POST'])
def export_ambassadors_direct():
    """Export ambassadors directly from database"""
    try:
        request_data = request.get_json()
        if not request_data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
        
        # Get record count and process
        filters = request_data.get('filters', {})
        total_records = db_export_service.get_export_record_count('ambassadors', filters)
        
        export_config = {
            "export_type": "ambassadors",
            "template": request_data.get('template', 'standard'),
            "filters": filters,
            "filename": request_data.get('filename', 'ambassadors_export'),
            "processing_mode": "database_direct",
            "total_records": total_records
        }
        
        result = db_export_service.create_database_export(export_config)
        return jsonify(result), 200 if result["status"] == "success" else 400
        
    except Exception as e:
        logger.error(f"Ambassadors database export failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Database export failed: {str(e)}"
        }), 500

@ybb_db_bp.route('/export/preview', methods=['POST'])
def preview_export():
    """
    Preview export without creating full export - shows first 100 records
    Useful for validating filters and seeing data structure
    """
    try:
        request_data = request.get_json()
        if not request_data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
        
        export_type = request_data.get('export_type', 'participants')
        template = request_data.get('template', 'standard')
        filters = request_data.get('filters', {})
        
        # Get preview data (limited to 100 records)
        preview_data = db_export_service.get_export_preview(
            export_type, template, filters, limit=100
        )
        
        return jsonify({
            "status": "success",
            "preview_data": preview_data,
            "message": f"Preview showing up to 100 records"
        }), 200
        
    except Exception as e:
        logger.error(f"Export preview failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Preview failed: {str(e)}"
        }), 500

@ybb_db_bp.route('/export/count', methods=['POST'])
def get_export_count():
    """
    Get record count for export without processing
    Useful for estimating export size before processing
    """
    try:
        request_data = request.get_json()
        if not request_data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
        
        export_type = request_data.get('export_type', 'participants')
        filters = request_data.get('filters', {})
        
        # Get record count
        total_records = db_export_service.get_export_record_count(export_type, filters)
        
        # Estimate processing time and file size
        estimates = db_export_service.estimate_export_metrics(export_type, total_records)
        
        return jsonify({
            "status": "success",
            "export_type": export_type,
            "filters": filters,
            "total_records": total_records,
            "estimates": estimates
        }), 200
        
    except Exception as e:
        logger.error(f"Export count failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Count failed: {str(e)}"
        }), 500

@ybb_db_bp.route('/tables/info', methods=['GET'])
def get_table_info():
    """Get information about available tables and fields"""
    try:
        table_info = db_export_service.get_available_tables_info()
        
        return jsonify({
            "status": "success",
            "tables": table_info
        }), 200
        
    except Exception as e:
        logger.error(f"Table info retrieval failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Table info failed: {str(e)}"
        }), 500

# Error handlers for database routes
@ybb_db_bp.errorhandler(400)
def db_bad_request(error):
    return jsonify({
        "status": "error",
        "message": "Bad request - invalid parameters or filters"
    }), 400

@ybb_db_bp.errorhandler(404)
def db_not_found(error):
    return jsonify({
        "status": "error",
        "message": "Database resource not found"
    }), 404

@ybb_db_bp.errorhandler(500)
def db_internal_error(error):
    return jsonify({
        "status": "error",
        "message": "Database operation failed"
    }), 500