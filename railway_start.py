#!/usr/bin/env python3
"""
Alternative startup script for Railway deployment
Uses built-in Flask development server as fallback
"""
import os
import sys

# Ensure we can import our modules
sys.path.insert(0, '/app')

def main():
    # Set production environment
    os.environ.setdefault('FLASK_ENV', 'production')
    os.environ.setdefault('FLASK_APP', 'app.py')
    
    try:
        # Try to use gunicorn first
        import gunicorn.app.wsgiapp as wsgi
        from wsgi import application
        
        # Configure gunicorn
        sys.argv = [
            'gunicorn',
            'wsgi:application',
            '--bind', f"0.0.0.0:{os.environ.get('PORT', 5000)}",
            '--workers', '2',
            '--timeout', '120',
            '--preload'
        ]
        
        wsgi.run()
        
    except ImportError:
        # Fallback to Flask development server
        print("⚠️  Gunicorn not available, using Flask development server")
        from app import app
        
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main()
