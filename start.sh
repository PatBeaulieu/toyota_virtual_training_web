#!/bin/bash
# Start script for Render deployment

echo "🚀 Starting Toyota Training application..."

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
fi

# Start the application
echo "🎯 Starting gunicorn server..."
exec gunicorn toyota_training.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 30