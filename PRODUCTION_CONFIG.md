# YBB Data Management Service - Security & Performance Configuration

## Security Headers (for Nginx/Reverse Proxy)

```nginx
# Add these headers to your Nginx configuration
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
```

## Rate Limiting Configuration

```nginx
# Rate limiting for API endpoints
http {
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=upload:10m rate=2r/s;
    
    server {
        # General API rate limiting
        location /api/ {
            limit_req zone=api burst=20 nodelay;
        }
        
        # Stricter limits for upload endpoints
        location /api/upload/ {
            limit_req zone=upload burst=5 nodelay;
        }
        
        # No rate limiting for health checks
        location /health {
            limit_req off;
        }
    }
}
```

## Environment Variables for Production

```bash
# Core Flask settings
export FLASK_ENV=production
export FLASK_APP=app.py
export SECRET_KEY="your-super-secret-key-here"

# API Configuration
export API_HOST=0.0.0.0
export API_PORT=5000
export MAX_CONTENT_LENGTH=104857600  # 100MB

# Performance tuning
export MAX_CHUNK_SIZE=1000
export MAX_MEMORY_MB=500
export REQUEST_TIMEOUT=300

# Logging
export LOG_LEVEL=INFO
export LOG_RETENTION_DAYS=14

# Security
export RATE_LIMIT_PER_MINUTE=60
export CORS_ORIGINS="https://yourdomain.com,https://admin.yourdomain.com"
```

## Gunicorn Production Configuration

Create `gunicorn.conf.py`:

```python
# Gunicorn configuration file
import multiprocessing

# Server socket
bind = "127.0.0.1:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 300
keepalive = 2

# Logging
accesslog = "/var/log/ybb-api/gunicorn-access.log"
errorlog = "/var/log/ybb-api/gunicorn-error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "ybb-api"

# Server mechanics
daemon = False
pidfile = "/var/run/ybb-api.pid"
user = "www-data"
group = "www-data"
tmp_upload_dir = None

# SSL (if terminating SSL at Gunicorn level)
# keyfile = "/path/to/private.key"
# certfile = "/path/to/certificate.crt"
```

## SSL Certificate Setup (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d files.ybbfoundation.com

# Verify auto-renewal
sudo certbot renew --dry-run

# Set up auto-renewal cron job
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

## Database Connection Pool (if using database)

```python
# Add to your app configuration
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Database connection pooling
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=20,
        max_overflow=0,
        pool_pre_ping=True,
        pool_recycle=300
    )
```

## Monitoring & Alerting Setup

### 1. Service Monitoring Script

```bash
#!/bin/bash
# /usr/local/bin/ybb-monitor.sh

API_URL="https://files.ybbfoundation.com"
WEBHOOK_URL="https://hooks.slack.com/your-webhook-url"  # Optional
EMAIL="admin@ybbfoundation.com"

# Check service health
response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 30 "${API_URL}/health")

if [ "$response" -ne 200 ]; then
    message="🚨 YBB API Alert: Service health check failed (HTTP: $response)"
    
    # Log the issue
    echo "$(date): $message" >> /var/log/ybb-api/alerts.log
    
    # Send email alert
    echo "$message" | mail -s "YBB API Service Alert" "$EMAIL"
    
    # Send Slack notification (optional)
    if [ -n "$WEBHOOK_URL" ]; then
        curl -X POST -H 'Content-type: application/json' \
             --data "{\"text\":\"$message\"}" \
             "$WEBHOOK_URL"
    fi
    
    # Attempt service restart
    systemctl restart ybb-api
    
    # Wait and check again
    sleep 30
    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 30 "${API_URL}/health")
    
    if [ "$response" -eq 200 ]; then
        recovery_message="✅ YBB API: Service recovered after restart"
        echo "$(date): $recovery_message" >> /var/log/ybb-api/alerts.log
        echo "$recovery_message" | mail -s "YBB API Recovery" "$EMAIL"
    fi
fi
```

### 2. Performance Monitoring

```python
# performance_monitor.py
import time
import requests
import json
from datetime import datetime

class PerformanceMonitor:
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url
        self.thresholds = {
            'health_check_ms': 1000,
            'export_small_ms': 5000,
            'export_large_ms': 30000
        }
    
    def run_performance_tests(self):
        results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }
        
        # Test 1: Health check response time
        start = time.time()
        resp = requests.get(f"{self.api_base_url}/health")
        health_time = (time.time() - start) * 1000
        
        results['tests']['health_check'] = {
            'response_time_ms': round(health_time, 2),
            'status_ok': resp.status_code == 200,
            'threshold_met': health_time < self.thresholds['health_check_ms']
        }
        
        # Test 2: Small export performance
        test_data = [{'id': i, 'name': f'Test {i}'} for i in range(100)]
        
        start = time.time()
        resp = requests.post(f"{self.api_base_url}/api/export/excel", 
                           json={'data': test_data})
        export_time = (time.time() - start) * 1000
        
        results['tests']['small_export'] = {
            'response_time_ms': round(export_time, 2),
            'status_ok': resp.status_code == 200,
            'threshold_met': export_time < self.thresholds['export_small_ms'],
            'records': len(test_data)
        }
        
        return results
    
    def check_thresholds(self, results):
        """Check if any performance thresholds are exceeded"""
        alerts = []
        
        for test_name, test_result in results['tests'].items():
            if not test_result.get('threshold_met', True):
                alerts.append({
                    'test': test_name,
                    'response_time': test_result['response_time_ms'],
                    'message': f"{test_name} exceeded threshold"
                })
        
        return alerts

if __name__ == '__main__':
    monitor = PerformanceMonitor('https://files.ybbfoundation.com')
    results = monitor.run_performance_tests()
    alerts = monitor.check_thresholds(results)
    
    print(json.dumps(results, indent=2))
    
    if alerts:
        print("\n⚠️  Performance Alerts:")
        for alert in alerts:
            print(f"- {alert['message']}: {alert['response_time']}ms")
```

## Log Analysis & Rotation

### 1. Enhanced Log Rotation

```bash
# /etc/logrotate.d/ybb-api
/var/log/ybb-api/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    sharedscripts
    postrotate
        systemctl reload ybb-api
        systemctl reload nginx
    endscript
}

# Application logs
/var/www/ybb-api/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
}
```

### 2. Log Analysis Script

```bash
#!/bin/bash
# log_analyzer.sh - Analyze YBB API logs for issues

LOG_FILE="/var/log/ybb-api/gunicorn-access.log"
ERROR_LOG="/var/log/ybb-api/gunicorn-error.log"
APP_LOG="/var/www/ybb-api/logs/ybb_api.log"

echo "YBB API Log Analysis - $(date)"
echo "================================="

# Check for errors in the last hour
echo "🔍 Recent Errors (last hour):"
grep "$(date -d '1 hour ago' '+%Y-%m-%d %H')" "$ERROR_LOG" | grep -i error | tail -10

# Check slow requests (>5 seconds)
echo -e "\n⏱️  Slow Requests (>5000ms):"
grep "SLOW_REQUEST" "$APP_LOG" | tail -10

# Check high memory usage
echo -e "\n💾 Memory Warnings:"
grep "Memory" "$APP_LOG" | tail -5

# Request volume analysis
echo -e "\n📊 Request Volume (last hour):"
grep "$(date '+%Y-%m-%d %H')" "$LOG_FILE" | wc -l | xargs echo "Total requests:"

# Top endpoints
echo -e "\n🔝 Top Endpoints:"
grep "$(date '+%Y-%m-%d')" "$LOG_FILE" | awk '{print $7}' | sort | uniq -c | sort -nr | head -10

# Error rate analysis
echo -e "\n❌ HTTP Error Rates:"
grep "$(date '+%Y-%m-%d')" "$LOG_FILE" | awk '{print $9}' | grep -E '^[4-5]' | sort | uniq -c | sort -nr
```

## Backup Strategy

```bash
#!/bin/bash
# backup_ybb_service.sh

BACKUP_DIR="/backups/ybb-api"
APP_DIR="/var/www/ybb-api"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory
mkdir -p "$BACKUP_DIR/$DATE"

echo "🗄️  Starting YBB service backup..."

# Backup application files
tar -czf "$BACKUP_DIR/$DATE/app_files.tar.gz" -C "$APP_DIR" \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='venv' \
    --exclude='temp' \
    .

# Backup configuration files
cp /etc/systemd/system/ybb-api.service "$BACKUP_DIR/$DATE/"
cp /etc/nginx/sites-available/ybb-api "$BACKUP_DIR/$DATE/" 2>/dev/null || true

# Backup logs (compressed)
tar -czf "$BACKUP_DIR/$DATE/logs.tar.gz" -C /var/log ybb-api

# Create backup manifest
cat > "$BACKUP_DIR/$DATE/manifest.txt" << EOF
YBB API Service Backup
Created: $(date)
Application Directory: $APP_DIR
Includes:
- Application files (excluding cache and temp)
- System service configuration
- Log files
- This manifest

Backup Size: $(du -sh "$BACKUP_DIR/$DATE" | cut -f1)
EOF

# Cleanup old backups
find "$BACKUP_DIR" -type d -mtime +$RETENTION_DAYS -exec rm -rf {} + 2>/dev/null

echo "✅ Backup completed: $BACKUP_DIR/$DATE"
echo "📊 Backup size: $(du -sh "$BACKUP_DIR/$DATE" | cut -f1)"
```

## Health Dashboard HTML

```html
<!DOCTYPE html>
<html>
<head>
    <title>YBB API Service Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .status-healthy { color: #28a745; }
        .status-warning { color: #ffc107; }
        .status-error { color: #dc3545; }
        .metric { display: inline-block; margin: 10px 20px; }
        .metric-value { font-size: 24px; font-weight: bold; }
        .metric-label { font-size: 12px; color: #666; }
        .refresh-btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        .log-entry { font-family: monospace; font-size: 12px; padding: 5px; border-left: 3px solid #ddd; margin: 5px 0; }
        .log-error { border-left-color: #dc3545; }
        .log-warning { border-left-color: #ffc107; }
        .log-info { border-left-color: #28a745; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 YBB API Service Dashboard</h1>
        
        <div class="card">
            <h2>Service Status</h2>
            <div id="service-status">Loading...</div>
            <button class="refresh-btn" onclick="refreshDashboard()">Refresh</button>
        </div>
        
        <div class="card">
            <h2>Performance Metrics</h2>
            <div id="performance-metrics">Loading...</div>
        </div>
        
        <div class="card">
            <h2>Recent Logs</h2>
            <div id="recent-logs">Loading...</div>
        </div>
    </div>

    <script>
        const API_BASE = window.location.origin;
        
        async function checkServiceHealth() {
            try {
                const response = await fetch(`${API_BASE}/health`);
                const data = await response.json();
                
                return {
                    status: response.ok ? 'healthy' : 'error',
                    data: data,
                    responseTime: Date.now() - startTime
                };
            } catch (error) {
                return {
                    status: 'error',
                    error: error.message
                };
            }
        }
        
        async function getLogStats() {
            try {
                const response = await fetch(`${API_BASE}/api/logs/stats`);
                return await response.json();
            } catch (error) {
                return { error: error.message };
            }
        }
        
        async function getRecentLogs() {
            try {
                const response = await fetch(`${API_BASE}/api/logs/recent?lines=20`);
                return await response.json();
            } catch (error) {
                return { error: error.message };
            }
        }
        
        async function refreshDashboard() {
            const startTime = Date.now();
            
            // Update service status
            const health = await checkServiceHealth();
            const statusElement = document.getElementById('service-status');
            
            if (health.status === 'healthy') {
                statusElement.innerHTML = `
                    <div class="status-healthy">
                        ✅ Service is healthy
                        <div class="metric">
                            <div class="metric-value">${health.responseTime}ms</div>
                            <div class="metric-label">Response Time</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">${health.data?.service || 'YBB API'}</div>
                            <div class="metric-label">Service</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">${health.data?.version || '1.0.0'}</div>
                            <div class="metric-label">Version</div>
                        </div>
                    </div>
                `;
            } else {
                statusElement.innerHTML = `
                    <div class="status-error">
                        ❌ Service error: ${health.error || 'Unknown error'}
                    </div>
                `;
            }
            
            // Update performance metrics
            const logStats = await getLogStats();
            const metricsElement = document.getElementById('performance-metrics');
            
            if (logStats.data) {
                const stats = logStats.data;
                metricsElement.innerHTML = `
                    <div class="metric">
                        <div class="metric-value">${stats.performance?.total_requests || 0}</div>
                        <div class="metric-label">Total Requests (24h)</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">${stats.performance?.avg_response_time || 0}ms</div>
                        <div class="metric-label">Avg Response Time</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">${stats.errors?.total_errors || 0}</div>
                        <div class="metric-label">Errors (24h)</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">${stats.performance?.slow_requests || 0}</div>
                        <div class="metric-label">Slow Requests</div>
                    </div>
                `;
            } else {
                metricsElement.innerHTML = '<div class="status-warning">⚠️ Performance metrics unavailable</div>';
            }
            
            // Update recent logs
            const logs = await getRecentLogs();
            const logsElement = document.getElementById('recent-logs');
            
            if (logs.data && logs.data.logs) {
                logsElement.innerHTML = logs.data.logs.slice(0, 10).map(log => {
                    const level = log.level?.toLowerCase() || 'info';
                    return `<div class="log-entry log-${level}">${log.timestamp} | ${log.level} | ${log.message}</div>`;
                }).join('');
            } else {
                logsElement.innerHTML = '<div class="status-warning">⚠️ Logs unavailable</div>';
            }
            
            // Update last refresh time
            document.title = `YBB API Dashboard - ${new Date().toLocaleTimeString()}`;
        }
        
        // Initial load
        refreshDashboard();
        
        // Auto-refresh every 30 seconds
        setInterval(refreshDashboard, 30000);
    </script>
</body>
</html>
```

Save this as `/var/www/ybb-api/static/dashboard.html` and access it via `https://files.ybbfoundation.com/static/dashboard.html`
