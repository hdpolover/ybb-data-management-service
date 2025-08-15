#!/usr/bin/env python3
"""
Emergency Railway app - Ultra-minimal with zero external dependencies
Use this if the main minimal app still fails
"""
import os
import json
from datetime import datetime

def create_emergency_app():
    """Create ultra-minimal Flask app"""
    try:
        from flask import Flask, jsonify, request
    except ImportError:
        print("CRITICAL: Flask not available - cannot start emergency app")
        exit(1)
    
    app = Flask(__name__)
    
    @app.route('/health', methods=['GET'])
    def health():
        """Ultra-simple health check"""
        return jsonify({
            "status": "healthy",
            "service": "YBB Emergency Mode",
            "timestamp": datetime.now().isoformat(),
            "message": "Service running in emergency mode with limited functionality"
        })
    
    @app.route('/api/ybb/export/participants', methods=['POST'])
    def export_participants():
        """Emergency mode response"""
        return jsonify({
            "status": "error",
            "message": "Service in emergency mode - full export functionality temporarily unavailable",
            "recommendation": "Please try again later or contact support"
        }), 503
    
    @app.route('/api/ybb/export/payments', methods=['POST'])
    def export_payments():
        return export_participants()
    
    @app.route('/api/ybb/export/ambassadors', methods=['POST']) 
    def export_ambassadors():
        return export_participants()
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Endpoint not found", "mode": "emergency"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error", "mode": "emergency"}), 500
    
    return app

def main():
    """Emergency startup function"""
    print("!" * 60)
    print("YBB DATA MANAGEMENT SERVICE - EMERGENCY MODE")  
    print("!" * 60)
    print("This is a minimal fallback service.")
    print("Full export functionality is not available.")
    print("!" * 60)
    
    try:
        app = create_emergency_app()
        
        port = int(os.environ.get('PORT', 5000))
        host = '0.0.0.0'
        
        print(f"Host: {host}")
        print(f"Port: {port}")
        print("Starting emergency server...")
        
        app.run(
            host=host,
            port=port,
            debug=False,
            threaded=True
        )
        
    except Exception as e:
        print(f"EMERGENCY STARTUP FAILED: {e}")
        exit(1)

if __name__ == '__main__':
    main()
