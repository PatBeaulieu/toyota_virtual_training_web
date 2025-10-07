#!/bin/bash
# Production Deployment Script for Toyota Virtual Training
# This script handles production deployment with PostgreSQL

set -e  # Exit on error

echo "========================================================================"
echo "🚀 Toyota Virtual Training - Production Deployment"
echo "========================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running in production mode
if [ "$DEBUG" = "True" ]; then
    echo -e "${RED}⚠️  WARNING: DEBUG is set to True${NC}"
    echo -e "${RED}This should be False in production!${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# =================================================================
# Step 1: Verify Environment
# =================================================================
echo -e "${BLUE}Step 1: Verifying Environment...${NC}"

# Check for .env file or environment variables
if [ ! -f ".env" ] && [ -z "$DATABASE_URL" ] && [ -z "$DB_NAME" ]; then
    echo -e "${RED}❌ No environment configuration found!${NC}"
    echo ""
    echo "Please create a .env file or set environment variables."
    echo "See: env.production.template"
    exit 1
fi

# Check DATABASE_URL or DB_NAME
if [ -n "$DATABASE_URL" ]; then
    echo -e "${GREEN}✅ DATABASE_URL is configured${NC}"
elif [ -n "$DB_NAME" ]; then
    echo -e "${GREEN}✅ PostgreSQL variables are configured${NC}"
    echo "   DB_NAME: $DB_NAME"
    echo "   DB_HOST: ${DB_HOST:-localhost}"
else
    echo -e "${RED}❌ No database configuration found${NC}"
    echo "Set DATABASE_URL or DB_* environment variables"
    exit 1
fi

# Check SECRET_KEY
if [ -z "$SECRET_KEY" ]; then
    echo -e "${YELLOW}⚠️  SECRET_KEY not set, will use default (not recommended)${NC}"
fi

# Check ALLOWED_HOSTS
if [ -z "$ALLOWED_HOSTS" ]; then
    echo -e "${YELLOW}⚠️  ALLOWED_HOSTS not set${NC}"
fi

echo ""

# =================================================================
# Step 2: Install Dependencies
# =================================================================
echo -e "${BLUE}Step 2: Installing Dependencies...${NC}"

if [ -f "requirements_production.txt" ]; then
    pip install -r requirements_production.txt --quiet
    echo -e "${GREEN}✅ Production dependencies installed${NC}"
elif [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${RED}❌ No requirements file found${NC}"
    exit 1
fi

echo ""

# =================================================================
# Step 3: Database Migrations
# =================================================================
echo -e "${BLUE}Step 3: Running Database Migrations...${NC}"

# Check database connection first
python manage.py check --database default --settings=toyota_training.settings_production
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Database connection failed${NC}"
    exit 1
fi

# Run migrations
python manage.py migrate --settings=toyota_training.settings_production --noinput
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Migrations applied successfully${NC}"
else
    echo -e "${RED}❌ Migrations failed${NC}"
    exit 1
fi

echo ""

# =================================================================
# Step 4: Collect Static Files
# =================================================================
echo -e "${BLUE}Step 4: Collecting Static Files...${NC}"

python manage.py collectstatic --noinput --settings=toyota_training.settings_production
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Static files collected${NC}"
else
    echo -e "${YELLOW}⚠️  Static files collection had issues (continuing...)${NC}"
fi

echo ""

# =================================================================
# Step 5: Run Tests (Optional)
# =================================================================
if [ "$RUN_TESTS" = "true" ]; then
    echo -e "${BLUE}Step 5: Running Tests...${NC}"
    python manage.py test --settings=toyota_training.settings_production
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ All tests passed${NC}"
    else
        echo -e "${RED}❌ Tests failed${NC}"
        echo "Continue deployment anyway? (y/n)"
        read -r CONTINUE
        if [ "$CONTINUE" != "y" ]; then
            exit 1
        fi
    fi
    echo ""
fi

# =================================================================
# Step 6: Create Cache Table (if using database cache)
# =================================================================
echo -e "${BLUE}Step 6: Setting up Cache...${NC}"

python manage.py createcachetable --settings=toyota_training.settings_production 2>/dev/null || true
echo -e "${GREEN}✅ Cache table ready${NC}"

echo ""

# =================================================================
# Step 7: Security Check
# =================================================================
echo -e "${BLUE}Step 7: Running Security Check...${NC}"

python manage.py check --deploy --settings=toyota_training.settings_production
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Security check passed${NC}"
else
    echo -e "${YELLOW}⚠️  Security issues detected (review above)${NC}"
fi

echo ""

# =================================================================
# Step 8: Deployment Summary
# =================================================================
echo "========================================================================"
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo "========================================================================"
echo ""
echo "📊 Deployment Summary:"
echo "   • Dependencies: Installed"
echo "   • Database: Migrated"
echo "   • Static Files: Collected"
echo "   • Cache: Configured"
echo "   • Security: Checked"
echo ""
echo "🚀 Ready to start the application server!"
echo ""
echo "Start with:"
echo "   gunicorn toyota_training.wsgi:application --bind 0.0.0.0:8000"
echo ""
echo "Or using the provided script:"
echo "   ./start_production.sh"
echo ""
echo "========================================================================"

