"""
Certificate API Routes
Handles certificate generation endpoints
"""
from flask import Blueprint, request, jsonify, g
from services.certificate_service import CertificateService
import logging
import time
import json

# Setup logging
logger = logging.getLogger('ybb_api.certificate_routes')

# Create blueprint
certificate_bp = Blueprint('certificates', __name__, url_prefix='/api/ybb/certificates')

# Initialize service
try:
    certificate_service = CertificateService()
    service_available = True
except Exception as e:
    logger.error(f"Certificate service initialization failed: {e}")
    certificate_service = None
    service_available = False

@certificate_bp.before_request
def log_certificate_request():
    """Log certificate-specific request details"""
    request_id = getattr(g, 'request_id', 'unknown')
    
    logger.info(
        f"CERTIFICATE_REQUEST | ID: {request_id} | "
        f"Endpoint: {request.endpoint} | "
        f"Method: {request.method} | "
        f"Path: {request.path}"
    )

@certificate_bp.route('/generate', methods=['POST'])
def generate_certificate():
    """
    Generate a certificate from template and content blocks
    
    Expected payload structure as defined in CERTIFICATE_GENERATION_API_SPEC.md:
    {
        "participant": {...},
        "program": {...},
        "award": {...},
        "certificate_template": {...},
        "content_blocks": [...],
        "assignment_info": {...}
    }
    """
    request_id = getattr(g, 'request_id', 'unknown')
    start_time = time.time()
    
    try:
        logger.info(f"CERTIFICATE_GENERATION_START | ID: {request_id}")
        
        # Check if service is available
        if not service_available or certificate_service is None:
            logger.error(f"CERTIFICATE_SERVICE_UNAVAILABLE | ID: {request_id}")
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SERVICE_UNAVAILABLE',
                    'message': 'Certificate generation service is not available. Please check server configuration.',
                    'request_id': request_id
                }
            }), 503
        
        # Get request data
        request_data = request.get_json()
        
        if not request_data:
            logger.error(f"CERTIFICATE_NO_DATA | ID: {request_id}")
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'No JSON data provided',
                    'request_id': request_id
                }
            }), 400
        
        # Log certificate request details
        participant_name = request_data.get('participant', {}).get('full_name', 'Unknown')
        program_name = request_data.get('program', {}).get('name', 'Unknown')
        award_title = request_data.get('award', {}).get('title', 'Unknown')
        
        logger.info(
            f"CERTIFICATE_REQUEST_DETAILS | ID: {request_id} | "
            f"Participant: {participant_name} | "
            f"Program: {program_name} | "
            f"Award: {award_title}"
        )
        
        # Generate certificate
        result = certificate_service.generate_certificate(request_data)
        
        processing_time = round((time.time() - start_time) * 1000, 2)
        
        if result['success']:
            logger.info(
                f"CERTIFICATE_GENERATION_SUCCESS | ID: {request_id} | "
                f"Certificate ID: {result['data']['certificate_id']} | "
                f"Time: {processing_time}ms"
            )
            return jsonify(result), 200
        else:
            logger.error(
                f"CERTIFICATE_GENERATION_FAILED | ID: {request_id} | "
                f"Error: {result.get('error', {}).get('message', 'Unknown error')} | "
                f"Time: {processing_time}ms"
            )
            
            # Return appropriate status code based on error type
            error_code = result.get('error', {}).get('code', 'UNKNOWN_ERROR')
            if error_code == 'VALIDATION_ERROR':
                return jsonify(result), 400
            elif error_code == 'TEMPLATE_NOT_FOUND':
                return jsonify(result), 404
            else:
                return jsonify(result), 500
        
    except Exception as e:
        processing_time = round((time.time() - start_time) * 1000, 2)
        logger.error(
            f"CERTIFICATE_GENERATION_EXCEPTION | ID: {request_id} | "
            f"Error: {str(e)} | Time: {processing_time}ms",
            exc_info=True
        )
        
        return jsonify({
            'success': False,
            'error': {
                'code': 'GENERATION_FAILED',
                'message': f'Certificate generation failed: {str(e)}',
                'request_id': request_id
            }
        }), 500

@certificate_bp.route('/health', methods=['GET'])
def certificate_health():
    """Health check for certificate service"""
    request_id = getattr(g, 'request_id', 'unknown')
    
    try:
        health_status = {
            'service': 'Certificate Generation Service',
            'status': 'healthy' if service_available else 'unavailable',
            'timestamp': time.time(),
            'request_id': request_id
        }
        
        if service_available:
            health_status['dependencies'] = {
                'reportlab': True,
                'pillow': True,
                'pypdf2': True
            }
        else:
            health_status['error'] = 'Service initialization failed'
        
        logger.info(f"CERTIFICATE_HEALTH_CHECK | ID: {request_id} | Status: {health_status['status']}")
        
        return jsonify(health_status), 200 if service_available else 503
        
    except Exception as e:
        logger.error(f"CERTIFICATE_HEALTH_CHECK_FAILED | ID: {request_id} | Error: {str(e)}")
        return jsonify({
            'service': 'Certificate Generation Service',
            'status': 'error',
            'error': str(e),
            'request_id': request_id
        }), 500

@certificate_bp.route('/templates/validate', methods=['POST'])
def validate_template():
    """
    Validate a certificate template URL and structure
    
    Expected payload:
    {
        "template_url": "https://example.com/template.pdf",
        "template_type": "pdf"
    }
    """
    request_id = getattr(g, 'request_id', 'unknown')
    
    try:
        logger.info(f"CERTIFICATE_TEMPLATE_VALIDATION | ID: {request_id}")
        
        if not service_available:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SERVICE_UNAVAILABLE',
                    'message': 'Certificate service is not available'
                }
            }), 503
        
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'No JSON data provided'
                }
            }), 400
        
        template_url = request_data.get('template_url')
        template_type = request_data.get('template_type', 'pdf')
        
        if not template_url:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Template URL is required'
                }
            }), 400
        
        # Validate template by attempting to download it
        template_info = {
            'template_url': template_url,
            'template_type': template_type
        }
        
        result = certificate_service._download_template(template_info)
        
        if result['success']:
            logger.info(f"CERTIFICATE_TEMPLATE_VALID | ID: {request_id} | URL: {template_url}")
            
            # Clean up downloaded file
            try:
                import os
                os.remove(result['template_path'])
            except:
                pass
            
            return jsonify({
                'success': True,
                'data': {
                    'template_url': template_url,
                    'template_type': template_type,
                    'file_size': result.get('file_size', 0),
                    'status': 'valid'
                },
                'message': 'Template is valid and accessible'
            }), 200
        else:
            logger.error(f"CERTIFICATE_TEMPLATE_INVALID | ID: {request_id} | URL: {template_url} | Error: {result['error']}")
            return jsonify({
                'success': False,
                'error': {
                    'code': 'TEMPLATE_NOT_FOUND',
                    'message': 'Template is not accessible or invalid',
                    'template_url': template_url,
                    'details': result['error']
                }
            }), 404
        
    except Exception as e:
        logger.error(f"CERTIFICATE_TEMPLATE_VALIDATION_EXCEPTION | ID: {request_id} | Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_FAILED',
                'message': f'Template validation failed: {str(e)}'
            }
        }), 500

@certificate_bp.route('/content-blocks/validate', methods=['POST'])
def validate_content_blocks():
    """
    Validate content blocks structure and positioning
    
    Expected payload:
    {
        "content_blocks": [...],
        "template_dimensions": {"width": 595, "height": 842}
    }
    """
    request_id = getattr(g, 'request_id', 'unknown')
    
    try:
        logger.info(f"CERTIFICATE_CONTENT_BLOCKS_VALIDATION | ID: {request_id}")
        
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'No JSON data provided'
                }
            }), 400
        
        content_blocks = request_data.get('content_blocks', [])
        template_dimensions = request_data.get('template_dimensions', {'width': 595, 'height': 842})
        
        validation_result = {
            'success': True,
            'data': {
                'total_blocks': len(content_blocks),
                'valid_blocks': 0,
                'invalid_blocks': 0,
                'warnings': [],
                'errors': []
            }
        }
        
        for i, block in enumerate(content_blocks):
            block_valid = True
            
            # Required fields validation
            if not block.get('type') or block['type'] not in ['text', 'placeholder']:
                validation_result['data']['errors'].append(f"Block {i}: Invalid or missing type")
                block_valid = False
            
            if not block.get('value'):
                validation_result['data']['errors'].append(f"Block {i}: Missing value")
                block_valid = False
            
            # Position validation
            x = block.get('x')
            y = block.get('y')
            
            if not isinstance(x, int) or x < 0:
                validation_result['data']['errors'].append(f"Block {i}: Invalid x coordinate")
                block_valid = False
            
            if not isinstance(y, int) or y < 0:
                validation_result['data']['errors'].append(f"Block {i}: Invalid y coordinate")
                block_valid = False
            
            # Bounds checking
            if isinstance(x, int) and isinstance(y, int):
                if x > template_dimensions['width']:
                    validation_result['data']['warnings'].append(f"Block {i}: X coordinate exceeds template width")
                
                if y > template_dimensions['height']:
                    validation_result['data']['warnings'].append(f"Block {i}: Y coordinate exceeds template height")
            
            # Font size validation
            font_size = block.get('font_size', 12)
            if not isinstance(font_size, int) or font_size < 1 or font_size > 200:
                validation_result['data']['warnings'].append(f"Block {i}: Unusual font size ({font_size})")
            
            if block_valid:
                validation_result['data']['valid_blocks'] += 1
            else:
                validation_result['data']['invalid_blocks'] += 1
        
        # Overall validation status
        if validation_result['data']['invalid_blocks'] > 0:
            validation_result['success'] = False
        
        logger.info(
            f"CERTIFICATE_CONTENT_BLOCKS_VALIDATED | ID: {request_id} | "
            f"Valid: {validation_result['data']['valid_blocks']} | "
            f"Invalid: {validation_result['data']['invalid_blocks']}"
        )
        
        return jsonify(validation_result), 200 if validation_result['success'] else 400
        
    except Exception as e:
        logger.error(f"CERTIFICATE_CONTENT_BLOCKS_VALIDATION_EXCEPTION | ID: {request_id} | Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_FAILED',
                'message': f'Content blocks validation failed: {str(e)}'
            }
        }), 500

@certificate_bp.route('/placeholders', methods=['GET'])
def get_available_placeholders():
    """Get list of available placeholders for certificate content"""
    try:
        placeholders = {
            'participant': [
                {'placeholder': '{{participant_name}}', 'description': 'Participant full name'},
                {'placeholder': '{{participant_institution}}', 'description': 'Participant institution'},
                {'placeholder': '{{participant_category}}', 'description': 'Participant category (fully_funded/self_funded)'},
                {'placeholder': '{{participant_nationality}}', 'description': 'Participant nationality'},
                {'placeholder': '{{participant_education_level}}', 'description': 'Education level'},
                {'placeholder': '{{participant_major}}', 'description': 'Major/field of study'},
                {'placeholder': '{{participant_occupation}}', 'description': 'Participant occupation'}
            ],
            'program': [
                {'placeholder': '{{program_name}}', 'description': 'Program name'},
                {'placeholder': '{{program_theme}}', 'description': 'Program theme'},
                {'placeholder': '{{program_dates}}', 'description': 'Program date range (start to end)'}
            ],
            'award': [
                {'placeholder': '{{award_title}}', 'description': 'Award title'},
                {'placeholder': '{{award_description}}', 'description': 'Award description'},
                {'placeholder': '{{award_type}}', 'description': 'Award type (winner/runner_up/mention/other)'}
            ],
            'general': [
                {'placeholder': '{{date}}', 'description': 'Issue date or current date'}
            ]
        }
        
        return jsonify({
            'success': True,
            'data': placeholders,
            'message': 'Available certificate placeholders'
        }), 200
        
    except Exception as e:
        logger.error(f"CERTIFICATE_PLACEHOLDERS_EXCEPTION | Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'PLACEHOLDERS_FAILED',
                'message': f'Failed to retrieve placeholders: {str(e)}'
            }
        }), 500

# Error handlers for the certificate blueprint
@certificate_bp.errorhandler(400)
def certificate_bad_request(error):
    request_id = getattr(g, 'request_id', 'unknown')
    return jsonify({
        'success': False,
        'error': {
            'code': 'BAD_REQUEST',
            'message': 'Bad request - invalid data format',
            'request_id': request_id
        }
    }), 400

@certificate_bp.errorhandler(404)
def certificate_not_found(error):
    request_id = getattr(g, 'request_id', 'unknown')
    return jsonify({
        'success': False,
        'error': {
            'code': 'NOT_FOUND',
            'message': 'Certificate endpoint not found',
            'request_id': request_id
        }
    }), 404

@certificate_bp.errorhandler(500)
def certificate_internal_error(error):
    request_id = getattr(g, 'request_id', 'unknown')
    return jsonify({
        'success': False,
        'error': {
            'code': 'INTERNAL_ERROR',
            'message': 'Certificate service internal error',
            'request_id': request_id
        }
    }), 500
