#!/bin/bash
# YBB Export API - Production Deployment Script#!/bin/bash

# YBB Data Management Service - Production Deployment Script
# This script handles the deployment of the YBB API service to production

set -e  # Exit on any error

echo "🚀 Starting YBB Data Management Service Deployment"
echo "=================================================="

# Configuration
SERVICE_NAME="ybb-api"
APP_DIR="/var/www/ybb-api"
BACKUP_DIR="/backups/ybb-api"
SYSTEMD_SERVICE="/etc/systemd/system/${SERVICE_NAME}.service"
NGINX_CONFIG="/etc/nginx/sites-available/${SERVICE_NAME}"
PYTHON_VERSION="python3.10"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root. Please run as a regular user with sudo privileges."
    fi
}

# Check system requirements
check_requirements() {
    log "Checking system requirements..."
    
    # Check Python version
    if ! command -v $PYTHON_VERSION &> /dev/null; then
        error "Python 3.10 is not installed. Please install it first."
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        error "pip3 is not installed. Please install python3-pip."
    fi
    
    # Check systemctl
    if ! command -v systemctl &> /dev/null; then
        error "systemctl is not available. This script requires systemd."
    fi
    
    log "✅ System requirements check passed"
}

# Create backup of current deployment
create_backup() {
    if [ -d "$APP_DIR" ]; then
        log "Creating backup of current deployment..."
        
        BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
        BACKUP_PATH="$BACKUP_DIR/$BACKUP_DATE"
        
        sudo mkdir -p "$BACKUP_PATH"
        sudo cp -r "$APP_DIR" "$BACKUP_PATH/"
        
        # Keep only last 5 backups
        sudo find "$BACKUP_DIR" -maxdepth 1 -type d -name "20*" | sort -r | tail -n +6 | sudo xargs rm -rf
        
        log "✅ Backup created at $BACKUP_PATH"
    else
        log "No existing deployment found, skipping backup"
    fi
}

# Stop existing service
stop_service() {
    if sudo systemctl is-active --quiet $SERVICE_NAME; then
        log "Stopping existing service..."
        sudo systemctl stop $SERVICE_NAME
        log "✅ Service stopped"
    else
        log "Service is not running"
    fi
}

# Create application directory and set permissions
setup_directories() {
    log "Setting up application directories..."
    
    sudo mkdir -p "$APP_DIR"
    sudo mkdir -p "$APP_DIR/logs"
    sudo mkdir -p "$APP_DIR/temp"
    sudo mkdir -p "/var/log/ybb-api"
    
    # Set ownership
    sudo chown -R $USER:www-data "$APP_DIR"
    sudo chown -R www-data:www-data "/var/log/ybb-api"
    
    # Set permissions
    sudo chmod -R 755 "$APP_DIR"
    sudo chmod -R 755 "/var/log/ybb-api"
    
    log "✅ Directories setup complete"
}

# Install application files
install_application() {
    log "Installing application files..."
    
    # Copy application files
    cp -r ./* "$APP_DIR/"
    
    # Set proper permissions
    sudo chown -R $USER:www-data "$APP_DIR"
    sudo chmod +x "$APP_DIR/app.py"
    
    log "✅ Application files installed"
}

# Setup Python virtual environment
setup_virtualenv() {
    log "Setting up Python virtual environment..."
    
    cd "$APP_DIR"
    
    # Remove existing venv if present
    if [ -d "venv" ]; then
        rm -rf venv
    fi
    
    # Create new virtual environment
    $PYTHON_VERSION -m venv venv
    
    # Activate and install dependencies
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install gunicorn
    deactivate
    
    # Set permissions
    sudo chown -R $USER:www-data venv
    
    log "✅ Virtual environment setup complete"
}

# Create systemd service file
create_systemd_service() {
    log "Creating systemd service file..."
    
    sudo tee "$SYSTEMD_SERVICE" > /dev/null <<EOF
[Unit]
Description=YBB Data Management API Service
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
Environment="FLASK_ENV=production"
Environment="PYTHONPATH=$APP_DIR"
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:5000 --timeout 300 --max-requests 1000 --max-requests-jitter 100 --access-logfile /var/log/ybb-api/access.log --error-logfile /var/log/ybb-api/error.log app:app
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    log "✅ Systemd service created"
}

# Start services
start_services() {
    log "Starting services..."
    
    # Start and enable YBB API service
    sudo systemctl start $SERVICE_NAME
    sudo systemctl enable $SERVICE_NAME
    
    # Wait a moment for services to start
    sleep 3
    
    # Check service status
    if sudo systemctl is-active --quiet $SERVICE_NAME; then
        log "✅ YBB API service is running"
    else
        error "Failed to start YBB API service"
    fi
}

# Verify deployment
verify_deployment() {
    log "Verifying deployment..."
    
    # Check local health endpoint
    if curl -f -s http://127.0.0.1:5000/health > /dev/null; then
        log "✅ Local API endpoint is responding"
    else
        warn "Local API endpoint is not responding"
    fi
    
    # Check logs for any immediate errors
    if sudo journalctl -u $SERVICE_NAME --since "1 minute ago" | grep -i error; then
        warn "Errors found in service logs, please review"
    else
        log "✅ No errors in service logs"
    fi
}

# Main deployment function
main() {
    log "Starting YBB Data Management Service deployment..."
    
    check_root
    check_requirements
    create_backup
    stop_service
    setup_directories
    install_application
    setup_virtualenv
    create_systemd_service
    start_services
    verify_deployment
    
    echo ""
    echo "🎉 Deployment completed successfully!"
    echo "==============================================="
    echo "Service Status: $(sudo systemctl is-active $SERVICE_NAME)"
    echo "Service URL: http://localhost:5000"
    echo "Health Check: http://localhost:5000/health"
    echo ""
    echo "Useful commands:"
    echo "  sudo systemctl status $SERVICE_NAME    # Check service status"
    echo "  sudo journalctl -u $SERVICE_NAME -f    # Follow service logs"
    echo "  sudo systemctl restart $SERVICE_NAME   # Restart service"
    echo "  curl http://localhost:5000/health       # Test API"
}

# Handle script arguments
case "${1:-deploy}" in
    deploy)
        main
        ;;
    stop)
        log "Stopping YBB API service..."
        sudo systemctl stop $SERVICE_NAME
        ;;
    start)
        log "Starting YBB API service..."
        sudo systemctl start $SERVICE_NAME
        ;;
    restart)
        log "Restarting YBB API service..."
        sudo systemctl restart $SERVICE_NAME
        ;;
    status)
        sudo systemctl status $SERVICE_NAME
        ;;
    logs)
        sudo journalctl -u $SERVICE_NAME -f
        ;;
    health)
        curl -s http://localhost:5000/health | python3 -m json.tool
        ;;
    backup)
        create_backup
        ;;
    *)
        echo "Usage: $0 {deploy|stop|start|restart|status|logs|health|backup}"
        echo ""
        echo "Commands:"
        echo "  deploy   - Full deployment (default)"
        echo "  stop     - Stop the service"
        echo "  start    - Start the service"
        echo "  restart  - Restart the service"
        echo "  status   - Show service status"
        echo "  logs     - Show service logs"
        echo "  health   - Check API health"
        echo "  backup   - Create backup only"
        exit 1
        ;;
esac=============================="
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
