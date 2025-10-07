#!/bin/bash
# Start Django with PostgreSQL
# This script loads PostgreSQL environment variables and starts the development server

echo "🚀 Starting Toyota Virtual Training with PostgreSQL..."
echo ""

# Load PostgreSQL environment variables
if [ -f .env.postgres ]; then
    export $(cat .env.postgres | grep -v '^#' | xargs)
    echo "✅ Loaded PostgreSQL configuration"
    echo "   Database: $DB_NAME"
    echo "   User: $DB_USER"
    echo "   Host: $DB_HOST:$DB_PORT"
    echo ""
else
    echo "❌ Error: .env.postgres file not found"
    echo "   Run: ./setup_postgres_test.sh"
    exit 1
fi

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Activated virtual environment"
    echo ""
else
    echo "⚠️ Warning: venv not found, using system Python"
    echo ""
fi

# Check if we need to run migrations
echo "Checking migrations..."
python manage.py migrate --check &> /dev/null
if [ $? -ne 0 ]; then
    echo "⚠️ Migrations need to be applied"
    read -p "Run migrations now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python manage.py migrate
        echo ""
    fi
fi

echo "========================================================"
echo "Starting Django development server with PostgreSQL..."
echo "========================================================"
echo ""
echo "To switch back to SQLite, just run: python manage.py runserver"
echo "To view this database: psql $DB_NAME"
echo ""

# Start the server
python manage.py runserver

