#!/bin/bash
# Comprehensive build script for Render deployment

echo "🚀 Starting comprehensive Render build process..."

# Ensure we're using the right Python version
echo "🐍 Python version: $(python --version)"

# Install dependencies with verbose output
echo "📦 Installing all dependencies..."
pip install -r requirements.txt --verbose

# Verify critical packages
echo "🔍 Verifying critical package installations..."
python -c "import django; print(f'✅ Django {django.get_version()}')" || echo "❌ Django missing"
python -c "import psycopg; print('✅ psycopg available')" || echo "❌ psycopg missing"
python -c "import cloudinary; print('✅ Cloudinary available')" || echo "❌ Cloudinary missing"
which gunicorn && echo "✅ Gunicorn in PATH" || echo "❌ Gunicorn not in PATH"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p media/training_programs
mkdir -p staticfiles

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate --settings=toyota_training.settings_production

# Seed the database with initial data
echo "🌱 Seeding database with initial data..."
python manage.py seed_database --settings=toyota_training.settings_production

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --settings=toyota_training.settings_production

# Final verification
echo "✅ Build completed successfully!"
echo "📊 Final verification:"
ls -la staticfiles/ || echo "No staticfiles directory"
ls -la media/ || echo "No media directory"

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

# Verify media files exist
echo "📁 Verifying media files..."
if [ -d "media" ]; then
    echo "📂 media directory exists"
    ls -la media/
    
    if [ -d "media/training_programs" ]; then
        echo "🖼️  Training program images found:"
        ls -la media/training_programs/
    else
        echo "❌ media/training_programs directory missing"
    fi
else
    echo "❌ media directory not created!"
fi

echo "🏁 Build process completed!"
