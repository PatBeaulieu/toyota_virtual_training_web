#!/bin/bash
# Simple build script for Render deployment

echo "🚀 Starting Render build process..."

# Install dependencies
pip install -r requirements.txt

# Collect static files - this is the critical part
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --settings=toyota_training.settings_production

# Verify static files were collected
echo "✅ Verifying static file collection..."
if [ -d "staticfiles" ]; then
    echo "📂 staticfiles directory exists"
    ls -la staticfiles/
    
    if [ -d "staticfiles/training_images" ]; then
        echo "🖼️  Training images found:"
        ls -la staticfiles/training_images/
    else
        echo "❌ training_images directory missing"
    fi
    
    if [ -d "staticfiles/css" ]; then
        echo "🎨 CSS files found:"
        ls -la staticfiles/css/
    else
        echo "❌ css directory missing"
    fi
else
    echo "❌ staticfiles directory not created!"
fi

echo "🏁 Build process completed!"
