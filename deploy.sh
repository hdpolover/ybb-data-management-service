#!/bin/bash
# YBB Export API - Production Deployment Script

echo "=========================================="
echo "YBB Export API - Production Deployment"
echo "=========================================="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Set production environment variables
echo "Setting production environment variables..."
export FLASK_ENV=production
export FLASK_DEBUG=False

# Create necessary directories
echo "Creating directories..."
mkdir -p logs
mkdir -p temp
mkdir -p exports

# Install Gunicorn for production
echo "Installing Gunicorn..."
pip install gunicorn

# Create Gunicorn configuration
cat > gunicorn.conf.py << EOF
# Gunicorn configuration for YBB Export API
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 300
keepalive = 2
preload_app = True
user = "www-data"
group = "www-data"
tmp_upload_dir = None
logfile = "logs/gunicorn.log"
loglevel = "info"
access_logfile = "logs/access.log"
error_logfile = "logs/error.log"
capture_output = True
EOF

# Create systemd service file
echo "Creating systemd service..."
sudo tee /etc/systemd/system/ybb-export-api.service > /dev/null << EOF
[Unit]
Description=YBB Export API
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/.venv/bin
ExecStart=$(pwd)/.venv/bin/gunicorn --config gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Create Nginx configuration
echo "Creating Nginx configuration..."
sudo tee /etc/nginx/sites-available/ybb-export-api > /dev/null << EOF
server {
    listen 80;
    server_name api.ybb-exports.your-domain.com;
    
    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    
    # API endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Increase timeouts for large exports
        proxy_connect_timeout 60s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
        
        # Increase max body size for large datasets
        client_max_body_size 500M;
    }
    
    # Health check
    location /health {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Deny all other requests
    location / {
        return 404;
    }
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/ybb-export-api /etc/nginx/sites-enabled/

# Create SSL certificate (Let's Encrypt)
echo "Setting up SSL certificate..."
sudo certbot --nginx -d api.ybb-exports.your-domain.com

# Set permissions
echo "Setting permissions..."
sudo chown -R www-data:www-data .
sudo chmod -R 755 .

# Enable and start services
echo "Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable ybb-export-api
sudo systemctl start ybb-export-api
sudo systemctl reload nginx

# Create monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash
# YBB Export API - Monitoring Script

# Check if service is running
if ! systemctl is-active --quiet ybb-export-api; then
    echo "Service is down, restarting..."
    sudo systemctl restart ybb-export-api
    echo "Service restarted at $(date)" >> logs/restart.log
fi

# Check API health
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health)
if [ "$response" != "200" ]; then
    echo "API health check failed (HTTP $response)"
    sudo systemctl restart ybb-export-api
    echo "Service restarted due to health check failure at $(date)" >> logs/restart.log
fi

# Clean up old logs (keep last 7 days)
find logs/ -name "*.log" -mtime +7 -delete

# Clean up old temporary exports
find temp/ -name "export_*" -mtime +1 -delete
EOF

chmod +x monitor.sh

# Add monitoring to cron
echo "Adding monitoring to cron..."
(crontab -l 2>/dev/null; echo "*/5 * * * * $(pwd)/monitor.sh") | crontab -

echo "=========================================="
echo "Deployment completed!"
echo "=========================================="
echo "Service Status: $(systemctl is-active ybb-export-api)"
echo "Nginx Status: $(systemctl is-active nginx)"
echo "API URL: https://api.ybb-exports.your-domain.com"
echo "Health Check: curl https://api.ybb-exports.your-domain.com/health"
echo ""
echo "Next steps:"
echo "1. Update DNS to point api.ybb-exports.your-domain.com to this server"
echo "2. Update CodeIgniter .env with: YBB_EXPORT_API_URL=https://api.ybb-exports.your-domain.com"
echo "3. Test the API endpoints"
echo "4. Monitor logs: tail -f logs/gunicorn.log"
