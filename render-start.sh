#!/bin/bash
# Render-specific startup script

echo "🚀 Toyota Virtual Training - Render Startup Script"

# Add current directory to PATH
export PATH="$PWD:$PATH"

# Make sure appgunicorn is executable
if [ -f "./appgunicorn" ]; then
    chmod +x ./appgunicorn
    echo "✅ appgunicorn script is ready"
else
    echo "❌ appgunicorn script not found"
fi

# Install gunicorn if needed
if ! command -v gunicorn &> /dev/null; then
    echo "Installing gunicorn..."
    pip install gunicorn==21.2.0
fi

# Get port from environment
PORT=${PORT:-8000}

echo "🌐 Starting application on port $PORT"
echo "📁 Current directory: $PWD"
echo "🔍 PATH: $PATH"

# Try to run the exact command Render is trying to run
echo "🚀 Executing: appgunicorn toyota_training.wsgi:application --bind 0.0.0.0:$PORT"
exec ./appgunicorn toyota_training.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 30
