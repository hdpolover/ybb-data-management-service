#!/bin/bash

# VPS Setup Script for YBB Data Management Service
# Run this script on your VPS to set up the deployment environment

set -e

echo "🚀 Setting up VPS for YBB Data Management Service deployment..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install required system packages
echo "🔧 Installing system dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    nginx \
    curl \
    wget \
    unzip \
    build-essential \
    pkg-config \
    libssl-dev \
    libffi-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    libxft-dev \
    supervisor

# Create deployment user if it doesn't exist
if ! id "deploy" &>/dev/null; then
    echo "👤 Creating deployment user..."
    sudo useradd -m -s /bin/bash deploy
    sudo usermod -aG www-data deploy
    sudo usermod -aG sudo deploy
fi

# Create application directories
echo "📁 Creating application directories..."
sudo mkdir -p /var/www/ybb-data-service
sudo mkdir -p /var/www/ybb-data-service-staging
sudo mkdir -p /etc/ybb-data-service

# Set proper ownership
sudo chown -R deploy:www-data /var/www/ybb-data-service
sudo chown -R deploy:www-data /var/www/ybb-data-service-staging
sudo chown -R deploy:www-data /etc/ybb-data-service

# Set proper permissions
sudo chmod -R 755 /var/www/ybb-data-service
sudo chmod -R 755 /var/www/ybb-data-service-staging
sudo chmod -R 755 /etc/ybb-data-service

# Install systemd service files
echo "⚙️ Installing systemd service files..."
sudo cp deployment/ybb-data-service.service /etc/systemd/system/
sudo cp deployment/ybb-data-service-staging.service /etc/systemd/system/

# Reload systemd and enable services
sudo systemctl daemon-reload
sudo systemctl enable ybb-data-service
sudo systemctl enable ybb-data-service-staging

# Create environment files template
echo "📋 Creating environment file templates..."

# Production environment
sudo tee /etc/ybb-data-service/.env.production > /dev/null <<EOF
# Production Environment Configuration
FLASK_ENV=production
SECRET_KEY=your-super-secret-production-key-change-this
API_HOST=0.0.0.0
API_PORT=5000
PORT=5000

# Performance settings
MAX_CONTENT_LENGTH=104857600
MAX_CHUNK_SIZE=500
MAX_MEMORY_MB=1000
REQUEST_TIMEOUT=180

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/ybb_api.log
ACCESS_LOG=logs/ybb_api_access.log

# CORS (adjust as needed)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Rate limiting
RATE_LIMIT_PER_MINUTE=120
EOF

# Staging environment
sudo tee /etc/ybb-data-service/.env.staging > /dev/null <<EOF
# Staging Environment Configuration
FLASK_ENV=development
SECRET_KEY=your-staging-secret-key-change-this
API_HOST=0.0.0.0
API_PORT=5001
PORT=5001

# Performance settings
MAX_CONTENT_LENGTH=52428800
MAX_CHUNK_SIZE=1000
MAX_MEMORY_MB=500
REQUEST_TIMEOUT=300

# Logging
LOG_LEVEL=DEBUG
LOG_FILE=logs/ybb_api.log
ACCESS_LOG=logs/ybb_api_access.log

# CORS (more permissive for staging)
CORS_ORIGINS=*

# Rate limiting
RATE_LIMIT_PER_MINUTE=60
EOF

# Set proper permissions for environment files
sudo chown deploy:www-data /etc/ybb-data-service/.env.*
sudo chmod 640 /etc/ybb-data-service/.env.*

# Create nginx configuration
echo "🌐 Setting up Nginx configuration..."

# Production site
sudo tee /etc/nginx/sites-available/ybb-data-service > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL configuration (you'll need to set up certificates)
    # ssl_certificate /path/to/your/certificate.crt;
    # ssl_certificate_key /path/to/your/private.key;
    
    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;
    
    # Proxy settings
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
    proxy_read_timeout 300s;
    proxy_connect_timeout 75s;
    
    # Main API location
    location / {
        proxy_pass http://127.0.0.1:5000;
    }
    
    # Health check endpoint (bypass rate limiting)
    location /health {
        proxy_pass http://127.0.0.1:5000;
        limit_req off;
    }
    
    # Static files (if any)
    location /static/ {
        alias /var/www/ybb-data-service/current/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Logs
    access_log /var/log/nginx/ybb-data-service_access.log;
    error_log /var/log/nginx/ybb-data-service_error.log;
}
EOF

# Staging site
sudo tee /etc/nginx/sites-available/ybb-data-service-staging > /dev/null <<EOF
server {
    listen 80;
    server_name staging.your-domain.com;
    
    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    
    # Rate limiting (more permissive for staging)
    limit_req_zone \$binary_remote_addr zone=staging_api:10m rate=5r/s;
    limit_req zone=staging_api burst=10 nodelay;
    
    # Proxy settings
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
    proxy_read_timeout 300s;
    proxy_connect_timeout 75s;
    
    # Main API location
    location / {
        proxy_pass http://127.0.0.1:5001;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:5001;
        limit_req off;
    }
    
    # Logs
    access_log /var/log/nginx/ybb-data-service-staging_access.log;
    error_log /var/log/nginx/ybb-data-service-staging_error.log;
}
EOF

# Enable sites (commented out by default - you'll need to configure domains first)
# sudo ln -sf /etc/nginx/sites-available/ybb-data-service /etc/nginx/sites-enabled/
# sudo ln -sf /etc/nginx/sites-available/ybb-data-service-staging /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# Create log rotation configuration
echo "📋 Setting up log rotation..."
sudo tee /etc/logrotate.d/ybb-data-service > /dev/null <<EOF
/var/www/ybb-data-service/current/logs/*.log
/var/www/ybb-data-service-staging/current/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    copytruncate
    create 0644 deploy www-data
}
EOF

# Create monitoring script
echo "📊 Creating monitoring script..."
sudo tee /usr/local/bin/ybb-service-monitor.sh > /dev/null <<'EOF'
#!/bin/bash

# Simple monitoring script for YBB Data Management Service

check_service() {
    local service_name=$1
    local port=$2
    
    echo "Checking $service_name..."
    
    # Check if service is running
    if systemctl is-active --quiet $service_name; then
        echo "✅ $service_name is running"
        
        # Check if port is responding
        if curl -f -s http://localhost:$port/health > /dev/null; then
            echo "✅ $service_name health check passed"
        else
            echo "❌ $service_name health check failed"
            return 1
        fi
    else
        echo "❌ $service_name is not running"
        return 1
    fi
}

echo "🏥 YBB Data Management Service Health Check"
echo "==========================================="

# Check production service
check_service "ybb-data-service" "5000"
prod_status=$?

echo ""

# Check staging service
check_service "ybb-data-service-staging" "5001"
staging_status=$?

echo ""
echo "Summary:"
if [ $prod_status -eq 0 ]; then
    echo "Production: ✅"
else
    echo "Production: ❌"
fi

if [ $staging_status -eq 0 ]; then
    echo "Staging: ✅"
else
    echo "Staging: ❌"
fi

# Exit with error if any service failed
if [ $prod_status -ne 0 ] || [ $staging_status -ne 0 ]; then
    exit 1
fi
EOF

sudo chmod +x /usr/local/bin/ybb-service-monitor.sh

# Create cron job for monitoring (optional)
echo "⏰ Setting up monitoring cron job..."
echo "*/5 * * * * /usr/local/bin/ybb-service-monitor.sh >> /var/log/ybb-service-monitor.log 2>&1" | sudo crontab -

# Create deployment script for manual deployments
echo "🚀 Creating manual deployment script..."
sudo tee /usr/local/bin/deploy-ybb-service.sh > /dev/null <<'EOF'
#!/bin/bash

# Manual deployment script for YBB Data Management Service

set -e

ENVIRONMENT=${1:-production}
BRANCH=${2:-main}

if [ "$ENVIRONMENT" = "production" ]; then
    DEPLOY_PATH="/var/www/ybb-data-service"
    SERVICE_NAME="ybb-data-service"
    PORT="5000"
elif [ "$ENVIRONMENT" = "staging" ]; then
    DEPLOY_PATH="/var/www/ybb-data-service-staging"
    SERVICE_NAME="ybb-data-service-staging"
    PORT="5001"
    BRANCH=${2:-develop}
else
    echo "❌ Invalid environment. Use 'production' or 'staging'"
    exit 1
fi

echo "🚀 Deploying $ENVIRONMENT environment from branch '$BRANCH'..."

# Navigate to deployment directory
cd $DEPLOY_PATH

# Backup current deployment
if [ -d "current" ]; then
    echo "📦 Creating backup..."
    rm -rf backup || true
    mv current backup || true
fi

# Clone repository
echo "📥 Downloading latest code..."
git clone -b $BRANCH https://github.com/hdpolover/ybb-data-management-service.git current
cd current

# Set up virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
mkdir -p logs temp uploads

# Copy environment file
if [ -f "/etc/ybb-data-service/.env.$ENVIRONMENT" ]; then
    cp "/etc/ybb-data-service/.env.$ENVIRONMENT" .env
fi

# Set permissions
sudo chown -R deploy:www-data $DEPLOY_PATH/current
sudo chmod -R 755 $DEPLOY_PATH/current
sudo chmod -R 775 $DEPLOY_PATH/current/logs
sudo chmod -R 775 $DEPLOY_PATH/current/temp
sudo chmod -R 775 $DEPLOY_PATH/current/uploads

# Restart service
echo "🔄 Restarting service..."
sudo systemctl restart $SERVICE_NAME

# Wait and check
sleep 5
if systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ Service restarted successfully"
    
    # Health check
    sleep 5
    if curl -f -s "http://localhost:$PORT/health" > /dev/null; then
        echo "✅ Health check passed"
        echo "🎉 Deployment completed successfully!"
    else
        echo "❌ Health check failed"
        exit 1
    fi
else
    echo "❌ Service failed to start"
    sudo systemctl status $SERVICE_NAME
    exit 1
fi
EOF

sudo chmod +x /usr/local/bin/deploy-ybb-service.sh

echo ""
echo "🎉 VPS setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Configure your domain names in the Nginx configuration files"
echo "2. Set up SSL certificates (recommended: Let's Encrypt with Certbot)"
echo "3. Update the environment files in /etc/ybb-data-service/ with your specific values"
echo "4. Set up GitHub repository secrets for deployment:"
echo "   - VPS_HOST: Your server's IP address or hostname"
echo "   - VPS_USERNAME: deploy"
echo "   - VPS_SSH_KEY: Your private SSH key"
echo "   - VPS_PORT: SSH port (default: 22)"
echo "5. Enable Nginx sites when ready:"
echo "   sudo ln -sf /etc/nginx/sites-available/ybb-data-service /etc/nginx/sites-enabled/"
echo "   sudo systemctl reload nginx"
echo ""
echo "Available commands:"
echo "- sudo systemctl status ybb-data-service"
echo "- sudo systemctl status ybb-data-service-staging"
echo "- /usr/local/bin/ybb-service-monitor.sh"
echo "- /usr/local/bin/deploy-ybb-service.sh [production|staging] [branch]"
echo ""
echo "Log files:"
echo "- /var/www/ybb-data-service/current/logs/"
echo "- /var/www/ybb-data-service-staging/current/logs/"
echo "- /var/log/nginx/"
EOF