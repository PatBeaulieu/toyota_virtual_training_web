#!/bin/bash
# Start script for Render deployment

echo "Starting Toyota Virtual Training application..."

# Run database migrations
python manage.py migrate --settings=toyota_training.settings_production

# Start the application
exec gunicorn toyota_training.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 30
