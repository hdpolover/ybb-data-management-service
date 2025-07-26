# Files to Add in Configuration Files Section

## 1. Procfile
```
web: gunicorn wsgi:application --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120 --preload
release: echo "Application ready for deployment"
```

## 2. runtime.txt
```
python-3.10.17
```

## 3. requirements.txt (already added)
```
Flask==3.0.3
Flask-CORS==4.0.1
pandas==2.2.2
openpyxl==3.1.5
python-dotenv==1.0.1
Werkzeug==3.0.3
gunicorn==22.0.0
psutil==5.9.8
requests==2.32.4
```

---

# Scripts for Execute Python Script Section

## Option 1: Use wsgi.py (Recommended)
```
wsgi.py
```

## Option 2: Use main.py (Simple alternative)
```
main.py
```

## Option 3: Use app.py (Direct Flask app)
```
app.py
```

---

# What Each Script Does:

**wsgi.py**: Production-ready WSGI server entry point with error handling
**main.py**: Simple startup script for hosting platforms  
**app.py**: Direct Flask application (works but less optimal for production)

Choose **wsgi.py** for best production performance!
