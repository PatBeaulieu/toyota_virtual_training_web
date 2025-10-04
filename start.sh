#!/bin/bash
# Start script for Render deployment

echo "🚀 Starting Toyota Training application..."

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
fi

# Install all dependencies to ensure they're available
echo "📦 Installing all dependencies..."
pip install -r requirements.txt

# Check if gunicorn is available
if ! command -v gunicorn &> /dev/null; then
    echo "❌ Gunicorn not found, trying to install..."
    pip install gunicorn==21.2.0
fi

# Verify installations
echo "🔍 Verifying installations..."
which gunicorn
pip show gunicorn
python -c "import django; print(f'Django {django.get_version()} installed')" || echo "❌ Django not found"

# Start the application
echo "🎯 Starting gunicorn server..."
exec gunicorn toyota_training.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 30