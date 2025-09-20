# Quick Setup Guide - VPS Auto-Deployment

## 🚀 Overview

This setup enables automatic deployment of your YBB Data Management Service to your VPS whenever you push to GitHub. It includes:

- **Production environment** (main branch → port 5000)
- **Staging environment** (develop branch → port 5001)
- **Automated testing** before deployment
- **Health checks** and monitoring
- **Nginx reverse proxy** with SSL support
- **Systemd service** management

## ⚡ Quick Start (15 minutes)

### 1. Prepare Your VPS

```bash
# SSH into your VPS
ssh root@your-vps-ip

# Download and run the setup script
wget https://raw.githubusercontent.com/hdpolover/ybb-data-management-service/main/deployment/setup-vps.sh
chmod +x setup-vps.sh
sudo ./setup-vps.sh
```

### 2. Configure SSH Key for GitHub Actions

```bash
# Generate SSH key for GitHub Actions
ssh-keygen -t ed25519 -f ~/.ssh/github_actions -N ""

# Add to authorized keys
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys

# Copy private key (you'll need this for GitHub)
cat ~/.ssh/github_actions
```

### 3. Set GitHub Repository Secrets

Go to: **GitHub Repository → Settings → Secrets and variables → Actions**

Add these secrets:

| Secret | Value |
|--------|-------|
| `VPS_HOST` | Your VPS IP address |
| `VPS_USERNAME` | `deploy` |
| `VPS_SSH_KEY` | Contents of `~/.ssh/github_actions` (private key) |
| `VPS_PORT` | `22` (or your custom SSH port) |

### 4. Configure Environment Variables

```bash
# Edit production settings
sudo nano /etc/ybb-data-service/.env.production

# Edit staging settings  
sudo nano /etc/ybb-data-service/.env.staging
```

**Important settings to update:**
```bash
SECRET_KEY=your-unique-secret-key-here
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 5. Test Deployment

Push to your repository:

```bash
# Push to staging (develop branch)
git checkout develop
git push origin develop

# Push to production (main branch)  
git checkout main
git push origin main
```

## 🎯 What Happens When You Push

1. **GitHub Actions triggers** automatically
2. **Tests run** (imports, health checks)
3. **Code is deployed** to VPS via SSH
4. **Virtual environment** is set up
5. **Dependencies** are installed
6. **Service restarts** with new code
7. **Health check** verifies deployment
8. **Notification** of success/failure

## 🔧 Post-Setup Configuration

### Domain Setup (Optional but Recommended)

1. **Point your domain to VPS IP**
2. **Update Nginx configuration:**
   ```bash
   sudo nano /etc/nginx/sites-available/ybb-data-service
   # Replace 'your-domain.com' with your actual domain
   ```
3. **Enable sites:**
   ```bash
   sudo ln -sf /etc/nginx/sites-available/ybb-data-service /etc/nginx/sites-enabled/
   sudo systemctl reload nginx
   ```
4. **Set up SSL:**
   ```bash
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

### Access Your API

- **Production**: `http://your-vps-ip:80` or `https://yourdomain.com`
- **Staging**: `http://your-vps-ip:80` (staging subdomain)
- **Health Checks**: 
  - Production: `http://your-vps-ip:5000/health`
  - Staging: `http://your-vps-ip:5001/health`

## 🛠️ Management Commands

```bash
# Check deployment status
/usr/local/bin/ybb-service-monitor.sh

# Check specific environment
./deployment/check-deployment.sh production
./deployment/check-deployment.sh staging

# Manual deployment
sudo /usr/local/bin/deploy-ybb-service.sh production main
sudo /usr/local/bin/deploy-ybb-service.sh staging develop

# Service management
sudo systemctl status ybb-data-service
sudo systemctl restart ybb-data-service
sudo journalctl -u ybb-data-service -f

# View logs
tail -f /var/www/ybb-data-service/current/logs/ybb_api.log
```

## 🆘 Troubleshooting

### Deployment Fails

1. **Check GitHub Actions logs** in your repository
2. **Verify secrets** are correctly set
3. **Check SSH connection:**
   ```bash
   ssh -i ~/.ssh/github_actions deploy@your-vps-ip
   ```

### Service Won't Start

1. **Check service logs:**
   ```bash
   sudo journalctl -u ybb-data-service -n 50
   ```
2. **Check application logs:**
   ```bash
   tail -f /var/www/ybb-data-service/current/logs/ybb_api.log
   ```
3. **Test manually:**
   ```bash
   cd /var/www/ybb-data-service/current
   source venv/bin/activate
   python app.py
   ```

### Health Check Fails

1. **Check if service is running:**
   ```bash
   sudo systemctl status ybb-data-service
   ```
2. **Test health endpoint directly:**
   ```bash
   curl -v http://localhost:5000/health
   ```

## 🔐 Security Notes

- SSH keys are used for secure deployment
- Services run with limited privileges (`www-data` user)
- Nginx provides reverse proxy and rate limiting
- Environment variables keep secrets secure
- Log rotation prevents disk space issues

## 📊 Monitoring

The setup includes:
- **Automatic health checks** every 5 minutes
- **Log rotation** to prevent disk space issues
- **Service auto-restart** on failure
- **Deployment backups** (last 3 versions kept)

## 🎉 You're Done!

Your Flask app will now automatically deploy whenever you:
- Push to `main` branch → Production deployment
- Push to `develop` branch → Staging deployment

The deployment includes testing, health checks, and automatic rollback on failure.