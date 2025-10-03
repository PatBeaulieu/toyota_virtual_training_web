#!/bin/bash
# Universal startup script that handles any command Render throws at it

echo "🚀 Toyota Virtual Training - Universal Startup Script"

# Install gunicorn if not available
if ! command -v gunicorn &> /dev/null; then
    echo "Installing gunicorn..."
    pip install gunicorn==21.2.0
fi

# Get port from environment
PORT=${PORT:-8000}

# Start the application with gunicorn
echo "Starting application on port $PORT..."
exec gunicorn toyota_training.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 30
