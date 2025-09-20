# VPS Deployment Guide for YBB Data Management Service

This guide will help you set up automatic deployment from GitHub to your VPS using GitHub Actions.

## Prerequisites

- A VPS with Ubuntu 20.04+ or similar Linux distribution
- Root or sudo access to the VPS
- A domain name (optional but recommended)
- SSH access to your VPS

## 1. VPS Setup

### Initial Server Setup

1. **Run the setup script on your VPS:**
   ```bash
   # Download and run the setup script
   wget https://raw.githubusercontent.com/hdpolover/ybb-data-management-service/main/deployment/setup-vps.sh
   chmod +x setup-vps.sh
   sudo ./setup-vps.sh
   ```

2. **Generate SSH key for GitHub Actions:**
   ```bash
   # Generate a new SSH key pair
   ssh-keygen -t ed25519 -f ~/.ssh/github_actions -N ""
   
   # Add the public key to authorized_keys
   cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys
   
   # Display the private key (copy this for GitHub secrets)
   cat ~/.ssh/github_actions
   ```

### Configure Environment Variables

1. **Edit production environment file:**
   ```bash
   sudo nano /etc/ybb-data-service/.env.production
   ```

2. **Edit staging environment file:**
   ```bash
   sudo nano /etc/ybb-data-service/.env.staging
   ```

### Configure Nginx (Optional)

1. **Update domain names in Nginx configs:**
   ```bash
   sudo nano /etc/nginx/sites-available/ybb-data-service
   sudo nano /etc/nginx/sites-available/ybb-data-service-staging
   ```

2. **Enable the sites:**
   ```bash
   sudo ln -sf /etc/nginx/sites-available/ybb-data-service /etc/nginx/sites-enabled/
   sudo ln -sf /etc/nginx/sites-available/ybb-data-service-staging /etc/nginx/sites-enabled/
   sudo systemctl reload nginx
   ```

3. **Set up SSL with Let's Encrypt (recommended):**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com -d www.your-domain.com
   sudo certbot --nginx -d staging.your-domain.com
   ```

## 2. GitHub Repository Setup

### Configure Repository Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add the following secrets:

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `VPS_HOST` | Your VPS IP address or hostname | `203.0.113.1` or `your-server.com` |
| `VPS_USERNAME` | SSH username | `deploy` |
| `VPS_SSH_KEY` | Private SSH key content | Contents of `~/.ssh/github_actions` |
| `VPS_PORT` | SSH port (optional) | `22` |

### Repository Branches

The deployment workflow is configured for:
- **main branch** → Production environment (port 5000)
- **develop branch** → Staging environment (port 5001)

## 3. Deployment Process

### Automatic Deployment

Every push to `main` or `develop` branches will trigger automatic deployment:

1. **Code is tested** in GitHub Actions runner
2. **Application is deployed** to the appropriate environment
3. **Service is restarted** and health-checked
4. **Deployment status** is reported

### Manual Deployment

You can also deploy manually on your VPS:

```bash
# Deploy production from main branch
sudo /usr/local/bin/deploy-ybb-service.sh production main

# Deploy staging from develop branch
sudo /usr/local/bin/deploy-ybb-service.sh staging develop
```

## 4. Monitoring and Maintenance

### Service Management

```bash
# Check service status
sudo systemctl status ybb-data-service
sudo systemctl status ybb-data-service-staging

# View service logs
sudo journalctl -u ybb-data-service -f
sudo journalctl -u ybb-data-service-staging -f

# Restart services
sudo systemctl restart ybb-data-service
sudo systemctl restart ybb-data-service-staging
```

### Health Monitoring

```bash
# Run health check script
/usr/local/bin/ybb-service-monitor.sh

# Check application logs
tail -f /var/www/ybb-data-service/current/logs/ybb_api.log
tail -f /var/www/ybb-data-service-staging/current/logs/ybb_api.log
```

### Application URLs

- **Production**: `https://your-domain.com`
- **Staging**: `https://staging.your-domain.com`
- **Health Check Production**: `https://your-domain.com/health`
- **Health Check Staging**: `https://staging.your-domain.com/health`

## 5. Security Considerations

### Firewall Configuration

```bash
# Install UFW if not already installed
sudo apt install ufw

# Basic firewall rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'

# Enable firewall
sudo ufw enable
```

### SSL/TLS Configuration

The Nginx configuration includes security headers and SSL best practices. Make sure to:

1. Use strong SSL certificates (Let's Encrypt recommended)
2. Keep certificates updated
3. Monitor SSL certificate expiration

### Application Security

1. **Keep dependencies updated**
2. **Monitor security vulnerabilities**
3. **Use strong secret keys**
4. **Implement proper rate limiting**
5. **Monitor application logs**

## 6. Troubleshooting

### Common Issues

1. **Deployment fails with SSH connection error:**
   - Check VPS_HOST, VPS_USERNAME, and VPS_SSH_KEY secrets
   - Verify SSH key permissions on the server

2. **Service fails to start:**
   - Check service logs: `sudo journalctl -u ybb-data-service -f`
   - Verify Python dependencies: `source venv/bin/activate && pip list`
   - Check environment file: `cat /etc/ybb-data-service/.env.production`

3. **Health check fails:**
   - Verify service is running: `sudo systemctl status ybb-data-service`
   - Check application logs: `tail -f /var/www/ybb-data-service/current/logs/ybb_api.log`
   - Test manually: `curl http://localhost:5000/health`

4. **Nginx configuration issues:**
   - Test configuration: `sudo nginx -t`
   - Check Nginx logs: `tail -f /var/log/nginx/error.log`

### Log Locations

- **Application logs**: `/var/www/ybb-data-service/current/logs/`
- **Nginx logs**: `/var/log/nginx/`
- **System logs**: `/var/log/syslog`
- **Service logs**: `journalctl -u ybb-data-service`

## 7. Backup and Recovery

### Automatic Backups

The deployment process automatically creates backups:
- Previous deployment is moved to `backup` directory
- Old backups are automatically cleaned up (keeps last 3)

### Manual Backup

```bash
# Create manual backup
sudo cp -r /var/www/ybb-data-service/current /var/www/ybb-data-service/backup-$(date +%Y%m%d-%H%M%S)

# Restore from backup
sudo systemctl stop ybb-data-service
sudo mv /var/www/ybb-data-service/current /var/www/ybb-data-service/broken
sudo cp -r /var/www/ybb-data-service/backup /var/www/ybb-data-service/current
sudo systemctl start ybb-data-service
```

## 8. Performance Optimization

### Resource Monitoring

```bash
# Monitor system resources
htop
iostat
df -h

# Monitor application performance
curl -s http://localhost:5000/health | jq .
```

### Gunicorn Configuration

The systemd service files include optimized Gunicorn settings:
- **Production**: 4 workers, 1000 max requests
- **Staging**: 2 workers, 500 max requests

Adjust based on your server resources in the service files.

## Support

For issues specific to your deployment:
1. Check the logs first
2. Run the health check script
3. Verify all configuration files
4. Test manual deployment

The deployment is designed to be robust and self-healing, with comprehensive logging and monitoring.