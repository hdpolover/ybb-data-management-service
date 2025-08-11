"""
YBB Data Management Service - Flask API
Production-ready version with proper error handling
"""
from flask import Flask, request, jsonify, send_file, g
from flask_cors import CORS
import pandas as pd
import json
import os
from datetime import datetime
import tempfile
from io import BytesIO
from werkzeug.utils import secure_filename
import logging
import uuid
import shutil
import time
import sys
from logging.handlers import RotatingFileHandler

# Import configuration
from config import get_config

# Import YBB routes
from api.ybb_routes import ybb_bp

# Import certificate routes
from api.certificate_routes import certificate_bp

def create_app():
    """Application factory pattern"""
    try:
        # Get configuration based on environment
        config = get_config()
        
        # Initialize Flask app
        app = Flask(__name__)
        app.config.from_object(config)
        
        # Setup CORS
        CORS(app, origins=config.CORS_ORIGINS)
        
        # Create necessary directories
        os.makedirs('logs', exist_ok=True)
        os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
        
        # Setup logging
        setup_logging(app, config)
        
        # Register blueprints
        app.register_blueprint(ybb_bp)
        app.register_blueprint(certificate_bp)
        
        # Setup middleware
        setup_middleware(app)
        
        # Setup error handlers
        setup_error_handlers(app)
        
        # Add basic routes
        setup_basic_routes(app)
        
        return app
        
    except Exception as e:
        print(f"ERROR: Failed to create Flask app: {e}")
        import traceback
        traceback.print_exc()
        raise

def setup_logging(app, config):
    """Setup comprehensive logging"""
    try:
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-15s | %(funcName)-20s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler for all logs (rotating)
        file_handler = RotatingFileHandler(
            config.LOG_FILE, 
            maxBytes=config.LOG_MAX_SIZE_MB*1024*1024,
            backupCount=config.LOG_BACKUP_COUNT
        )
        file_handler.setLevel(getattr(logging, config.LOG_LEVEL))
        file_handler.setFormatter(detailed_formatter)
        
        # File handler for API access logs (rotating)
        access_handler = RotatingFileHandler(
            config.ACCESS_LOG, 
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        access_handler.setLevel(logging.INFO)
        access_handler.setFormatter(simple_formatter)
        
        # Console handler for development
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, config.LOG_LEVEL))
        console_handler.setFormatter(simple_formatter)
        
        # Configure root logger
        logging.basicConfig(level=getattr(logging, config.LOG_LEVEL), handlers=[])
        
        # Create specific loggers
        app_logger = logging.getLogger('ybb_api')
        app_logger.setLevel(getattr(logging, config.LOG_LEVEL))
        app_logger.addHandler(file_handler)
        if config.DEBUG:
            app_logger.addHandler(console_handler)
        
        access_logger = logging.getLogger('ybb_api.access')
        access_logger.setLevel(logging.INFO)
        access_logger.addHandler(access_handler)
        if config.DEBUG:
            access_logger.addHandler(console_handler)
        
        # Prevent duplicate logs
        app_logger.propagate = False
        access_logger.propagate = False
        
        # Store loggers in app context
        app.logger_instance = app_logger
        app.access_logger = access_logger
        
    except Exception as e:
        print(f"WARNING: Failed to setup logging: {e}")
        # Use basic logging as fallback
        logging.basicConfig(level=logging.INFO)

def setup_middleware(app):
    """Setup request/response middleware"""
    
    @app.before_request
    def before_request():
        g.start_time = time.time()
        g.request_id = str(uuid.uuid4())[:8]
        
        # Log incoming request
        try:
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            user_agent = request.headers.get('User-Agent', 'Unknown')
            
            app.access_logger.info(
                f"REQUEST_START | ID: {g.request_id} | "
                f"Method: {request.method} | "
                f"URL: {request.url} | "
                f"IP: {client_ip} | "
                f"User-Agent: {user_agent[:100]}..."
            )
        except:
            pass  # Don't fail the request if logging fails
    
    @app.after_request
    def after_request(response):
        try:
            # Calculate processing time
            processing_time = round((time.time() - g.start_time) * 1000, 2)  # ms
            
            # Log response
            app.access_logger.info(
                f"REQUEST_END | ID: {g.request_id} | "
                f"Status: {response.status_code} | "
                f"Time: {processing_time}ms | "
                f"Size: {response.content_length or 0} bytes"
            )
        except:
            pass  # Don't fail the request if logging fails
        
        return response

def setup_error_handlers(app):
    """Setup error handlers"""
    
    @app.errorhandler(404)
    def not_found(error):
        request_id = getattr(g, 'request_id', 'unknown')
        try:
            app.logger_instance.warning(f"NOT_FOUND | ID: {request_id} | URL: {request.url} | Method: {request.method}")
        except:
            pass
        return jsonify({
            'error': 'Endpoint not found',
            'request_id': request_id,
            'url': request.url,
            'method': request.method
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        request_id = getattr(g, 'request_id', 'unknown')
        try:
            app.logger_instance.error(f"INTERNAL_ERROR | ID: {request_id} | URL: {request.url} | Method: {request.method}")
        except:
            pass
        return jsonify({
            'error': 'Internal server error',
            'request_id': request_id
        }), 500
    
    @app.errorhandler(Exception)
    def log_exception(error):
        request_id = getattr(g, 'request_id', 'unknown')
        try:
            app.logger_instance.error(
                f"EXCEPTION | ID: {request_id} | "
                f"Error: {str(error)} | "
                f"URL: {request.url} | "
                f"Method: {request.method}",
                exc_info=True
            )
        except:
            pass
        
        return jsonify({
            'error': 'Internal server error', 
            'request_id': request_id
        }), 500

def setup_basic_routes(app):
    """Setup basic application routes"""
    
    @app.route('/')
    def index():
        """Root endpoint"""
        return jsonify({
            'service': 'YBB Data Management Service',
            'version': '1.0.0',
            'status': 'running',
            'timestamp': datetime.now().isoformat(),
            'endpoints': [
                '/health',
                '/api/export/excel',
                '/api/data/process',
                '/api/ybb/export/participants',
                '/api/ybb/export/payments',
                '/api/ybb/export/ambassadors',
                '/api/ybb/certificates/generate',
                '/api/ybb/certificates/health'
            ]
        })
    
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        request_id = getattr(g, 'request_id', 'unknown')
        try:
            app.logger_instance.info(f"HEALTH_CHECK | ID: {request_id} | Health check requested")
        except:
            pass
        
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'YBB Data Processing Service',
            'version': '1.0.0',
            'request_id': request_id
        }
        
        return jsonify(health_data)

# Create the Flask app
app = create_app()

if __name__ == '__main__':
    try:
        config = get_config()
        print(f"Starting YBB Data Management Service...")
        print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
        print(f"Debug mode: {config.DEBUG}")
        print(f"Host: {config.API_HOST}")
        print(f"Port: {config.API_PORT}")
        
        app.run(
            debug=config.DEBUG, 
            host=config.API_HOST, 
            port=config.API_PORT
        )
    except Exception as e:
        print(f"FATAL ERROR: Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
