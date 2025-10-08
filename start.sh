#!/bin/bash
# Start script for Railway deployment

# Get PORT from environment or default to 8000
PORT=${PORT:-8000}

echo "🔧 Running database migrations..."
python manage.py migrate --noinput

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "👤 Creating superuser (if configured)..."
if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
    python create_superuser.py
else
    echo "ℹ️  Skipping superuser creation (DJANGO_SUPERUSER_USERNAME not set)"
fi

echo "🚀 Starting gunicorn on port $PORT"

# Start gunicorn
exec gunicorn toyota_training.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --timeout 30 \
    --access-logfile - \
    --error-logfile -
