#!/bin/bash

# Deployment script for Toyota Virtual Training Session Admin
# This script handles the deployment process for production

set -e  # Exit on any error

echo "🚀 Starting deployment of Toyota Virtual Training Session Admin..."

# Configuration
PROJECT_DIR="/var/www/toyota_training"
VENV_DIR="/var/www/toyota_training/venv"
BACKUP_DIR="/var/backups/toyota_training"
LOG_FILE="/var/log/toyota_training/deploy.log"

# Create log directory if it doesn't exist
mkdir -p $(dirname $LOG_FILE)

# Log function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

# Error handling
error_exit() {
    log "ERROR: $1"
    exit 1
}

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    error_exit "This script must be run as root or with sudo"
fi

log "Starting deployment process..."

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup current database
log "Creating database backup..."
cd $PROJECT_DIR
if [ -f "db.sqlite3" ]; then
    cp db.sqlite3 $BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).sqlite3
    log "Database backup created"
fi

# Backup current code
log "Creating code backup..."
tar -czf $BACKUP_DIR/code_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
    --exclude=venv \
    --exclude=__pycache__ \
    --exclude=*.pyc \
    --exclude=.git \
    .

# Activate virtual environment
log "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Update dependencies
log "Updating dependencies..."
pip install -r requirements_production.txt

# Run database migrations
log "Running database migrations..."
python manage.py migrate --settings=toyota_training.settings_production

# Collect static files
log "Collecting static files..."
python manage.py collectstatic --noinput --settings=toyota_training.settings_production

# Create logs directory
log "Creating logs directory..."
mkdir -p logs

# Set proper permissions
log "Setting file permissions..."
chown -R www-data:www-data $PROJECT_DIR
chmod -R 755 $PROJECT_DIR
chmod -R 777 logs media

# Restart services
log "Restarting services..."
systemctl restart gunicorn
systemctl restart nginx

# Run health checks
log "Running health checks..."
sleep 5

# Check if services are running
if systemctl is-active --quiet gunicorn; then
    log "✅ Gunicorn is running"
else
    error_exit "❌ Gunicorn failed to start"
fi

if systemctl is-active --quiet nginx; then
    log "✅ Nginx is running"
else
    error_exit "❌ Nginx failed to start"
fi

# Test the application
log "Testing application..."
if curl -f -s http://localhost/ > /dev/null; then
    log "✅ Application is responding"
else
    error_exit "❌ Application is not responding"
fi

log "🎉 Deployment completed successfully!"
log "Application is now running at: https://yourdomain.com"

# Cleanup old backups (keep last 7 days)
log "Cleaning up old backups..."
find $BACKUP_DIR -name "*.sqlite3" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

log "Deployment process finished"
