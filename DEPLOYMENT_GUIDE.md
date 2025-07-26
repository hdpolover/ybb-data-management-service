# YBB Data Management Service - Deployment Guide

## Overview

This guide covers the complete deployment process for the YBB Data Management Service, from local development to production hosting.

## Prerequisites

- Python 3.10 or higher
- pip package manager
- Virtual environment support
- Web hosting with Python support (for production)

## Local Development Setup

### 1. Environment Setup

```bash
# Clone or download the project
cd ybb-data-management-web-flask

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the project root:

```bash
# Development settings
FLASK_ENV=development
FLASK_DEBUG=True
API_HOST=127.0.0.1
API_PORT=5000

# Performance settings
MAX_CONTENT_LENGTH=104857600  # 100MB
MAX_CHUNK_SIZE=1000
MAX_MEMORY_MB=500

# Logging settings
LOG_LEVEL=INFO
LOG_RETENTION_DAYS=7
```

### 3. Start Development Server

```bash
# Method 1: Direct Python execution
python app.py

# Method 2: Using Flask CLI
flask run --host=127.0.0.1 --port=5000

# Method 3: Using VS Code task
# Use the "Start Flask API Server" task in VS Code
```

### 4. Verify Installation

```bash
# Run quick test
python quick_test.py

# Check health endpoint
curl http://localhost:5000/health

# Test basic export
python test_api.py
```

## Production Deployment

### Hosting Configuration (cPanel/Shared Hosting)

Based on your hosting setup for `files.ybbfoundation.com`:

#### 1. Python App Configuration

| Setting | Value |
|---------|-------|
| **Python Version** | 3.10.17 |
| **Application Root** | `public_html/ybb-api` |
| **Application URL** | `files.ybbfoundation.com` |
| **Application Startup File** | `app.py` |
| **Application Entry Point** | `app` |

#### 2. Environment Variables

Add these environment variables in your hosting control panel:

```bash
FLASK_ENV=production
FLASK_APP=app.py
PYTHONPATH=/home/yourusername/public_html/ybb-api
MAX_CONTENT_LENGTH=104857600
LOG_LEVEL=INFO
```

#### 3. File Structure

Upload these files to your `public_html/ybb-api` directory:

```
public_html/ybb-api/
├── app.py                          # Main application
├── requirements.txt                # Dependencies
├── config.py                       # Configuration (create if needed)
├── .htaccess                       # URL rewriting (create)
├── api/                           # API modules
│   ├── __init__.py
│   └── ybb_routes.py
├── config/                        # Configuration files
│   ├── __init__.py
│   └── ybb_export_config.py
├── services/                      # Service modules
│   ├── __init__.py
│   └── ybb_export_service.py
├── utils/                         # Utility modules
│   ├── __init__.py
│   ├── excel_exporter.py
│   ├── log_viewer.py
│   └── performance.py
├── logs/                          # Log directory (create)
├── temp/                          # Temporary files (create)
└── static/                        # Static files
    └── logs_dashboard.html
```

#### 4. Create .htaccess File

Create `.htaccess` in your application root:

```apache
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ app.py/$1 [QSA,L]

# Set maximum upload size
php_value upload_max_filesize 100M
php_value post_max_size 100M

# Enable compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/plain
    AddOutputFilterByType DEFLATE text/html
    AddOutputFilterByType DEFLATE text/xml
    AddOutputFilterByType DEFLATE text/css
    AddOutputFilterByType DEFLATE application/xml
    AddOutputFilterByType DEFLATE application/xhtml+xml
    AddOutputFilterByType DEFLATE application/rss+xml
    AddOutputFilterByType DEFLATE application/javascript
    AddOutputFilterByType DEFLATE application/x-javascript
    AddOutputFilterByType DEFLATE application/json
</IfModule>

# Security headers
Header always set X-Content-Type-Options nosniff
Header always set X-Frame-Options DENY
Header always set X-XSS-Protection "1; mode=block"
```

### VPS/Dedicated Server Deployment

#### 1. System Requirements

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10
sudo apt install python3.10 python3.10-venv python3-pip -y

# Install system dependencies
sudo apt install build-essential libssl-dev libffi-dev python3-dev -y

# Install web server (optional)
sudo apt install nginx -y
```

#### 2. Application Setup

```bash
# Create application directory
sudo mkdir -p /var/www/ybb-api
cd /var/www/ybb-api

# Clone/upload your application files
# Set proper permissions
sudo chown -R www-data:www-data /var/www/ybb-api
sudo chmod -R 755 /var/www/ybb-api

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn
```

#### 3. Create Production Configuration

Create `config.py`:

```python
import os
from datetime import timedelta

class ProductionConfig:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    DEBUG = False
    TESTING = False
    
    # API settings
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    
    # Performance settings
    MAX_CHUNK_SIZE = int(os.environ.get('MAX_CHUNK_SIZE', 1000))
    MAX_MEMORY_MB = int(os.environ.get('MAX_MEMORY_MB', 500))
    
    # File settings
    UPLOAD_FOLDER = '/tmp/ybb-uploads'
    EXPORT_RETENTION_HOURS = 24
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = '/var/log/ybb-api/app.log'
    ACCESS_LOG = '/var/log/ybb-api/access.log'

# Apply configuration
config = ProductionConfig()
```

#### 4. Create Systemd Service

Create `/etc/systemd/system/ybb-api.service`:

```ini
[Unit]
Description=YBB Data Management API
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/var/www/ybb-api
Environment="PATH=/var/www/ybb-api/venv/bin"
ExecStart=/var/www/ybb-api/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:5000 --timeout 300 --max-requests 1000 --max-requests-jitter 100 app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

#### 5. Start and Enable Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Start the service
sudo systemctl start ybb-api

# Enable auto-start
sudo systemctl enable ybb-api

# Check status
sudo systemctl status ybb-api
```

#### 6. Nginx Configuration

Create `/etc/nginx/sites-available/ybb-api`:

```nginx
server {
    listen 80;
    server_name files.ybbfoundation.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name files.ybbfoundation.com;

    # SSL configuration (add your certificates)
    ssl_certificate /path/to/your/certificate.pem;
    ssl_certificate_key /path/to/your/private.key;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # File upload limits
    client_max_body_size 100M;
    client_body_timeout 300s;
    client_header_timeout 300s;

    # Proxy to Flask application
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Static files (if any)
    location /static {
        alias /var/www/ybb-api/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:5000/health;
        access_log off;
    }

    # Logs
    access_log /var/log/nginx/ybb-api-access.log;
    error_log /var/log/nginx/ybb-api-error.log warn;
}
```

Enable the site:

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/ybb-api /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

## Docker Deployment

### 1. Create Dockerfile

```dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs temp

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')"

# Run application
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "--timeout", "300", "app:app"]
```

### 2. Create docker-compose.yml

```yaml
version: '3.8'

services:
  ybb-api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - MAX_CONTENT_LENGTH=104857600
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
      - ./temp:/app/temp
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - /path/to/ssl/certs:/etc/nginx/certs
    depends_on:
      - ybb-api
    restart: unless-stopped
```

### 3. Deploy with Docker

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f ybb-api

# Scale workers
docker-compose up -d --scale ybb-api=3
```

## Monitoring and Maintenance

### 1. Log Monitoring

Create log rotation configuration `/etc/logrotate.d/ybb-api`:

```
/var/log/ybb-api/*.log {
    daily
    missingok
    rotate 7
    compress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload ybb-api
    endscript
}
```

### 2. Health Monitoring Script

Create `monitor.sh`:

```bash
#!/bin/bash

API_URL="https://files.ybbfoundation.com/health"
EMAIL="admin@ybbfoundation.com"
LOG_FILE="/var/log/ybb-api/monitor.log"

# Check health endpoint
response=$(curl -s -o /dev/null -w "%{http_code}" $API_URL)

if [ $response -ne 200 ]; then
    echo "$(date): API health check failed - HTTP $response" >> $LOG_FILE
    echo "YBB API is down. HTTP response: $response" | mail -s "YBB API Alert" $EMAIL
    
    # Restart service
    sudo systemctl restart ybb-api
else
    echo "$(date): API health check passed" >> $LOG_FILE
fi
```

Add to crontab:

```bash
# Check every 5 minutes
*/5 * * * * /path/to/monitor.sh
```

### 3. Performance Monitoring

Create `performance_check.py`:

```python
#!/usr/bin/env python3

import requests
import json
import time
from datetime import datetime

def check_performance():
    """Check API performance metrics"""
    
    base_url = "https://files.ybbfoundation.com"
    
    # Test data
    test_data = [{"name": f"User{i}", "email": f"user{i}@test.com"} for i in range(100)]
    
    # Health check
    start_time = time.time()
    health_response = requests.get(f"{base_url}/health")
    health_time = (time.time() - start_time) * 1000
    
    # Excel export test
    start_time = time.time()
    export_response = requests.post(f"{base_url}/api/export/excel", 
                                   json={"data": test_data})
    export_time = (time.time() - start_time) * 1000
    
    # Log results
    results = {
        "timestamp": datetime.now().isoformat(),
        "health_check": {
            "response_time_ms": health_time,
            "status_code": health_response.status_code
        },
        "excel_export": {
            "response_time_ms": export_time,
            "status_code": export_response.status_code,
            "records_processed": len(test_data)
        }
    }
    
    print(json.dumps(results, indent=2))
    
    # Alert if performance is poor
    if health_time > 5000 or export_time > 10000:
        print("ALERT: Poor performance detected!")
        return False
    
    return True

if __name__ == "__main__":
    check_performance()
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Check Python path
   echo $PYTHONPATH
   
   # Verify virtual environment
   which python
   pip list
   ```

2. **Permission Errors**
   ```bash
   # Fix file permissions
   sudo chown -R www-data:www-data /var/www/ybb-api
   sudo chmod -R 755 /var/www/ybb-api
   ```

3. **Port Conflicts**
   ```bash
   # Check port usage
   sudo netstat -tlnp | grep :5000
   
   # Kill process if needed
   sudo kill -9 <process_id>
   ```

4. **Memory Issues**
   ```bash
   # Monitor memory usage
   free -h
   
   # Check application memory
   ps aux | grep gunicorn
   ```

### Debug Mode

For troubleshooting, temporarily enable debug mode:

```bash
export FLASK_DEBUG=True
export FLASK_ENV=development
python app.py
```

### Log Analysis

```bash
# View recent logs
tail -f /var/log/ybb-api/app.log

# Search for errors
grep -i error /var/log/ybb-api/app.log

# Performance analysis
grep "SLOW_REQUEST" /var/log/ybb-api/app.log
```

## Security Considerations

### 1. API Security

- Implement API key authentication
- Use HTTPS in production
- Validate all input data
- Implement rate limiting
- Regular security updates

### 2. File Security

- Sanitize uploaded filenames
- Validate file types
- Limit file sizes
- Regular cleanup of temporary files
- Secure file permissions

### 3. Network Security

- Use firewall rules
- Limit API access by IP (if needed)
- Monitor for unusual traffic patterns
- Keep SSL certificates updated

## Backup and Recovery

### 1. Backup Strategy

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/ybb-api"
APP_DIR="/var/www/ybb-api"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR/$DATE

# Backup application files
tar -czf $BACKUP_DIR/$DATE/app_files.tar.gz -C $APP_DIR .

# Backup logs
tar -czf $BACKUP_DIR/$DATE/logs.tar.gz -C /var/log/ybb-api .

# Cleanup old backups (keep 7 days)
find $BACKUP_DIR -type d -mtime +7 -exec rm -rf {} +

echo "Backup completed: $BACKUP_DIR/$DATE"
```

### 2. Recovery Procedure

```bash
#!/bin/bash
# restore.sh

BACKUP_DIR="/backups/ybb-api"
APP_DIR="/var/www/ybb-api"
RESTORE_DATE=$1

if [ -z "$RESTORE_DATE" ]; then
    echo "Usage: $0 <backup_date>"
    exit 1
fi

# Stop service
sudo systemctl stop ybb-api

# Restore application files
tar -xzf $BACKUP_DIR/$RESTORE_DATE/app_files.tar.gz -C $APP_DIR

# Set permissions
sudo chown -R www-data:www-data $APP_DIR

# Start service
sudo systemctl start ybb-api

echo "Restore completed from: $RESTORE_DATE"
```

This deployment guide covers all aspects of getting your YBB Data Management Service running in various environments, from local development to production hosting.
