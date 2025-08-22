#!/usr/bin/env python3
"""
YBB Data Management Service - Fallback Application
Minimal Flask app that works with basic dependencies only
"""

import os
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_minimal_app():
    """Create minimal Flask app with only essential features"""
    try:
        from flask import Flask, jsonify, request
        
        app = Flask(__name__)
        
        # Try to import CORS, but continue without it if not available
        try:
            from flask_cors import CORS
            CORS(app)
            logger.info("✅ CORS enabled")
        except ImportError:
            logger.warning("⚠️ flask_cors not available, continuing without CORS")
        
        @app.route('/')
        def index():
            return jsonify({
                'service': 'YBB Data Management API',
                'status': 'running',
                'version': '1.0.0-minimal',
                'timestamp': datetime.now().isoformat(),
                'dependencies': {
                    'pandas': check_dependency('pandas'),
                    'numpy': check_dependency('numpy'),
                    'openpyxl': check_dependency('openpyxl'),
                    'reportlab': check_dependency('reportlab'),
                    'Pillow': check_dependency('PIL'),
                    'flask_cors': check_dependency('flask_cors')
                }
            })
        
        @app.route('/health')
        def health():
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'python_version': sys.version,
                'working_directory': os.getcwd()
            })
        
        @app.route('/api/test')
        def api_test():
            """Test basic pandas functionality"""
            try:
                import pandas as pd
                import numpy as np
                
                # Create test data
                data = {
                    'name': ['Alice', 'Bob', 'Charlie'],
                    'age': [25, 30, 35],
                    'score': [95.5, 87.3, 92.1]
                }
                df = pd.DataFrame(data)
                
                return jsonify({
                    'status': 'success',
                    'message': 'Pandas is working!',
                    'test_data': df.to_dict('records'),
                    'summary': {
                        'rows': len(df),
                        'avg_age': float(df['age'].mean()),
                        'avg_score': float(df['score'].mean())
                    }
                })
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': f'Pandas test failed: {str(e)}'
                }), 500
        
        @app.route('/api/export/simple', methods=['POST'])
        def simple_export():
            """Simple data export without advanced formatting"""
            try:
                import pandas as pd
                from io import BytesIO
                from flask import send_file
                
                # Get JSON data from request
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No data provided'}), 400
                
                # Create DataFrame
                df = pd.DataFrame(data)
                
                # Create Excel file in memory
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Data', index=False)
                
                output.seek(0)
                
                return send_file(
                    output,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    as_attachment=True,
                    download_name=f'export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
                )
                
            except Exception as e:
                logger.error(f"Export failed: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'message': f'Export failed: {str(e)}'
                }), 500
        
        return app
        
    except ImportError as e:
        logger.error(f"Failed to create Flask app: {str(e)}")
        raise

def check_dependency(module_name):
    """Check if a dependency is available"""
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False

def main():
    """Main application entry point"""
    logger.info("🚀 Starting YBB Data Management Service (Minimal Mode)")
    
    try:
        # Create the Flask app
        app = create_minimal_app()
        
        # Get port from environment
        port = int(os.environ.get('PORT', 8080))
        
        logger.info(f"✅ Starting server on port {port}")
        logger.info("🌐 Available endpoints:")
        logger.info("   GET  / - Service info")
        logger.info("   GET  /health - Health check")
        logger.info("   GET  /api/test - Test pandas functionality")
        logger.info("   POST /api/export/simple - Simple data export")
        
        # Start the server
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        logger.error(f"💥 Failed to start application: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()