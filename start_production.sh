#!/bin/bash
# Production Startup Script for Toyota Virtual Training
# Starts the application with Gunicorn and proper PostgreSQL configuration

set -e  # Exit on error

echo "========================================================================"
echo "🚀 Starting Toyota Virtual Training (Production Mode)"
echo "========================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# =================================================================
# Configuration
# =================================================================

# Port (default 8000, or use environment variable)
PORT=${PORT:-8000}

# Number of workers (default: 2, or use environment variable)
WORKERS=${WEB_CONCURRENCY:-2}

# Timeout (default: 30 seconds)
TIMEOUT=${GUNICORN_TIMEOUT:-30}

# Django settings module
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-toyota_training.settings_production}

# =================================================================
# Pre-flight Checks
# =================================================================

echo -e "${BLUE}Pre-flight Checks...${NC}"
echo ""

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo -e "${RED}❌ Gunicorn not found${NC}"
    echo "Installing gunicorn..."
    pip install gunicorn==21.2.0
fi

# Check database configuration
if [ -z "$DATABASE_URL" ] && [ -z "$DB_NAME" ]; then
    echo -e "${RED}❌ No database configuration found!${NC}"
    echo ""
    echo "Please set either:"
    echo "  - DATABASE_URL (recommended)"
    echo "  - DB_NAME, DB_USER, DB_PASSWORD, DB_HOST"
    echo ""
    exit 1
fi

# Verify database connection
echo -e "${BLUE}Testing database connection...${NC}"
python manage.py check --database default 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database connection OK${NC}"
else
    echo -e "${RED}❌ Database connection failed${NC}"
    echo "Please check your database configuration"
    exit 1
fi

# Check for pending migrations
echo -e "${BLUE}Checking migrations...${NC}"
python manage.py migrate --check --noinput 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Pending migrations detected${NC}"
    read -p "Run migrations now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python manage.py migrate --noinput
        echo -e "${GREEN}✅ Migrations applied${NC}"
    else
        echo -e "${YELLOW}⚠️  Starting without migrating (may cause errors)${NC}"
    fi
else
    echo -e "${GREEN}✅ Migrations up to date${NC}"
fi

echo ""

# =================================================================
# Application Info
# =================================================================

echo "========================================================================"
echo "📋 Application Configuration"
echo "========================================================================"
echo ""
echo "  Settings Module: $DJANGO_SETTINGS_MODULE"
echo "  Port: $PORT"
echo "  Workers: $WORKERS"
echo "  Timeout: ${TIMEOUT}s"
echo "  Database: PostgreSQL"

if [ -n "$DATABASE_URL" ]; then
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\).*/\1/p')
    echo "  DB Host: $DB_HOST"
elif [ -n "$DB_HOST" ]; then
    echo "  DB Host: $DB_HOST"
fi

echo ""
echo "========================================================================"
echo ""

# =================================================================
# Start Gunicorn
# =================================================================

echo -e "${GREEN}🚀 Starting Gunicorn...${NC}"
echo ""

# Gunicorn configuration
exec gunicorn toyota_training.wsgi:application \
    --bind "0.0.0.0:$PORT" \
    --workers "$WORKERS" \
    --timeout "$TIMEOUT" \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --worker-class sync \
    --worker-tmp-dir /dev/shm \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --graceful-timeout 30 \
    --keep-alive 5

# Note: This script replaces itself with gunicorn (exec),
# so any commands after this line won't execute

