#!/bin/bash

# Quick deployment status check
# Usage: ./check-deployment.sh [production|staging]

ENVIRONMENT=${1:-production}

if [ "$ENVIRONMENT" = "production" ]; then
    SERVICE_NAME="ybb-data-service"
    PORT="5000"
    DEPLOY_PATH="/var/www/ybb-data-service"
elif [ "$ENVIRONMENT" = "staging" ]; then
    SERVICE_NAME="ybb-data-service-staging"
    PORT="5001"
    DEPLOY_PATH="/var/www/ybb-data-service-staging"
else
    echo "Usage: $0 [production|staging]"
    exit 1
fi

echo "🔍 Checking $ENVIRONMENT deployment status..."
echo "=============================================="

# Check if service is running
if systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ Service Status: Running"
else
    echo "❌ Service Status: Not Running"
    echo "📋 Service logs (last 10 lines):"
    sudo journalctl -u $SERVICE_NAME -n 10 --no-pager
    exit 1
fi

# Check health endpoint
if curl -f -s http://localhost:$PORT/health > /dev/null; then
    echo "✅ Health Check: Passed"
    
    # Get health details
    echo "📊 Health Details:"
    curl -s http://localhost:$PORT/health | jq . 2>/dev/null || curl -s http://localhost:$PORT/health
else
    echo "❌ Health Check: Failed"
    exit 1
fi

# Check deployment info
if [ -d "$DEPLOY_PATH/current" ]; then
    echo "📁 Deployment Path: $DEPLOY_PATH/current"
    
    # Check git info
    cd $DEPLOY_PATH/current
    if [ -d ".git" ]; then
        echo "🌿 Current Branch: $(git branch --show-current)"
        echo "📝 Last Commit: $(git log -1 --pretty=format:'%h - %s (%cr)' 2>/dev/null)"
    fi
    
    # Check virtual environment
    if [ -f "venv/bin/python" ]; then
        echo "🐍 Python Version: $(venv/bin/python --version)"
    fi
    
    # Check recent logs
    if [ -f "logs/ybb_api.log" ]; then
        echo "📋 Recent Logs (last 3 lines):"
        tail -n 3 logs/ybb_api.log
    fi
else
    echo "❌ Deployment directory not found: $DEPLOY_PATH/current"
    exit 1
fi

echo ""
echo "✅ Deployment check completed successfully!"