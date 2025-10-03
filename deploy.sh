#!/bin/bash
# Deployment script for Render

echo "Running database migrations..."
python manage.py migrate --settings=toyota_training.settings_production

echo "Starting application..."
exec gunicorn toyota_training.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 30