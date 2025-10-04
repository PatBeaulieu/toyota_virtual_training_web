#!/bin/bash
# Robust start script for Render deployment

echo "🚀 Starting Toyota Training application..."

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
fi

# Quick dependency check and install if needed
echo "🔍 Quick dependency verification..."
if ! python -c "import django" 2>/dev/null; then
    echo "📦 Django missing, installing dependencies..."
    pip install -r requirements.txt --quiet
fi

# Verify all critical components
echo "✅ Verifying all components..."
python -c "import django; print(f'✅ Django {django.get_version()}')" || { echo "❌ Django failed"; exit 1; }
python -c "import psycopg; print('✅ psycopg')" || { echo "❌ psycopg failed"; exit 1; }
python -c "import cloudinary; print('✅ Cloudinary')" || { echo "❌ Cloudinary failed"; exit 1; }

# Start the application
echo "🎯 Starting gunicorn server..."
exec gunicorn toyota_training.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 30