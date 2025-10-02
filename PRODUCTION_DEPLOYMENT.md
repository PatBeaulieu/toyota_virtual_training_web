# Production Deployment Guide

This guide provides step-by-step instructions for deploying the Toyota Virtual Training Session Admin application to production.

## Prerequisites

- Ubuntu 20.04+ or similar Linux distribution
- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- Nginx
- SSL certificate
- Domain name configured

## Security Checklist

### ✅ Completed Security Measures

1. **Settings Security**
   - Production settings with DEBUG=False
   - Secure SECRET_KEY configuration
   - HTTPS enforcement
   - Security headers middleware
   - CSRF protection
   - Session security

2. **Input Validation**
   - Custom validators for all user inputs
   - Teams link validation
   - Password strength validation
   - SQL injection prevention
   - XSS protection

3. **Authentication & Authorization**
   - Rate limiting on login attempts
   - User type-based access control
   - Region-based permissions
   - Security event logging

4. **Error Handling**
   - Custom error pages
   - Comprehensive logging
   - Security event monitoring
   - Graceful error recovery

## Deployment Options

### Option 1: Traditional VPS Deployment

#### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.9 python3.9-venv python3-pip postgresql postgresql-contrib redis-server nginx git

# Create project directory
sudo mkdir -p /var/www/toyota_training
sudo chown $USER:$USER /var/www/toyota_training
```

#### 2. Database Setup

```bash
# Create database and user
sudo -u postgres psql
CREATE DATABASE toyota_training;
CREATE USER toyota_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE toyota_training TO toyota_user;
\q
```

#### 3. Application Deployment

```bash
# Clone repository
cd /var/www/toyota_training
git clone <your-repo-url> .

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements_production.txt

# Copy environment file
cp env.example .env
# Edit .env with your production values

# Run migrations
python manage.py migrate --settings=toyota_training.settings_production

# Create superuser
python manage.py createsuperuser --settings=toyota_training.settings_production

# Collect static files
python manage.py collectstatic --noinput --settings=toyota_training.settings_production
```

#### 4. Nginx Configuration

```bash
# Copy nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/toyota_training
sudo ln -s /etc/nginx/sites-available/toyota_training /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

#### 5. Gunicorn Setup

```bash
# Create gunicorn service file
sudo nano /etc/systemd/system/toyota_training.service
```

Add the following content:

```ini
[Unit]
Description=Toyota Virtual Training Session Admin
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/toyota_training
Environment="PATH=/var/www/toyota_training/venv/bin"
ExecStart=/var/www/toyota_training/venv/bin/gunicorn --workers 3 --bind unix:/var/www/toyota_training/toyota_training.sock toyota_training.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
# Start services
sudo systemctl start toyota_training
sudo systemctl enable toyota_training
```

### Option 2: Docker Deployment

#### 1. Docker Setup

```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. Environment Configuration

```bash
# Copy environment file
cp env.example .env

# Edit .env with your production values
nano .env
```

#### 3. Deploy with Docker Compose

```bash
# Build and start services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate --settings=toyota_training.settings_production

# Create superuser
docker-compose exec web python manage.py createsuperuser --settings=toyota_training.settings_production

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput --settings=toyota_training.settings_production
```

### Option 3: Cloud Platform Deployment

#### Heroku Deployment

```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login to Heroku
heroku login

# Create Heroku app
heroku create toyota-training-admin

# Set environment variables
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set DEBUG=False
heroku config:set DATABASE_URL="postgres://..."

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate
```

#### AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize EB application
eb init

# Create environment
eb create production

# Deploy
eb deploy
```

## SSL Certificate Setup

### Let's Encrypt (Free)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Commercial SSL Certificate

1. Purchase SSL certificate from a trusted CA
2. Upload certificate files to `/etc/nginx/ssl/`
3. Update nginx configuration with certificate paths

## Monitoring and Maintenance

### Log Monitoring

```bash
# Application logs
tail -f /var/log/toyota_training/deploy.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# System logs
journalctl -u toyota_training -f
```

### Database Backups

```bash
# Create backup script
nano /usr/local/bin/backup_toyota_training.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/toyota_training"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
pg_dump -h localhost -U toyota_user toyota_training > $BACKUP_DIR/db_backup_$DATE.sql

# Media files backup
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz /var/www/toyota_training/media/

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

```bash
# Make executable
chmod +x /usr/local/bin/backup_toyota_training.sh

# Add to crontab for daily backups
crontab -e
# Add: 0 2 * * * /usr/local/bin/backup_toyota_training.sh
```

### Health Checks

```bash
# Basic health check
curl https://yourdomain.com/health/

# Detailed health check
curl https://yourdomain.com/health/detailed/

# Kubernetes/Docker health checks
curl https://yourdomain.com/health/ready/
curl https://yourdomain.com/health/live/
```

## Security Maintenance

### Regular Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Python packages
pip install --upgrade -r requirements_production.txt

# Update Django
pip install --upgrade Django
```

### Security Monitoring

1. **Review logs regularly** for suspicious activity
2. **Monitor failed login attempts**
3. **Check for security vulnerabilities** in dependencies
4. **Update SSL certificates** before expiration
5. **Review user permissions** periodically

### Performance Monitoring

1. **Monitor database performance**
2. **Check memory usage**
3. **Monitor disk space**
4. **Review slow queries**
5. **Optimize as needed**

## Troubleshooting

### Common Issues

1. **502 Bad Gateway**
   - Check if Gunicorn is running
   - Verify socket file permissions
   - Check nginx error logs

2. **Database Connection Errors**
   - Verify database credentials
   - Check PostgreSQL status
   - Verify network connectivity

3. **Static Files Not Loading**
   - Run `collectstatic` command
   - Check nginx configuration
   - Verify file permissions

4. **SSL Certificate Issues**
   - Check certificate expiration
   - Verify nginx SSL configuration
   - Test SSL configuration

### Emergency Procedures

1. **Application Down**
   ```bash
   sudo systemctl restart toyota_training
   sudo systemctl restart nginx
   ```

2. **Database Issues**
   ```bash
   sudo systemctl restart postgresql
   # Restore from backup if needed
   ```

3. **Security Incident**
   - Review logs immediately
   - Block suspicious IPs
   - Change passwords if compromised
   - Update security measures

## Support

For technical support or questions about this deployment:

1. Check the application logs first
2. Review this documentation
3. Contact your system administrator
4. Create an issue in the project repository

## Version History

- v1.0.0 - Initial production deployment guide
- v1.1.0 - Added Docker deployment option
- v1.2.0 - Added cloud platform deployment options
- v1.3.0 - Enhanced security measures and monitoring
