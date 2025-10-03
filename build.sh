#!/bin/bash
# Build script for Render deployment

echo "Starting build process..."

# Ensure gunicorn is installed
pip install gunicorn==21.2.0

# Install all dependencies
pip install -r requirements.txt

echo "✅ All dependencies installed successfully"

# Make sure appgunicorn script exists and is executable
if [ -f "appgunicorn" ]; then
    echo "Making appgunicorn executable..."
    chmod +x appgunicorn
else
    echo "Creating appgunicorn script..."
    cat > appgunicorn << 'EOF'
#!/bin/bash
echo "🚀 Redirecting appgunicorn to gunicorn..."
if ! command -v gunicorn &> /dev/null; then
    echo "Installing gunicorn..."
    pip install gunicorn==21.2.0
fi
exec gunicorn "$@"
EOF
    chmod +x appgunicorn
fi

# Try to install to system PATH (may not work on Render)
echo "Attempting to install appgunicorn to system PATH..."
cp appgunicorn /usr/local/bin/appgunicorn 2>/dev/null || echo "Could not install to /usr/local/bin"
chmod +x /usr/local/bin/appgunicorn 2>/dev/null || echo "Could not make /usr/local/bin/appgunicorn executable"

# Add current directory to PATH for this session
export PATH="$PWD:$PATH"
echo "Added $PWD to PATH"

# Verify the script exists and is executable
ls -la appgunicorn

# Create media directories
echo "Creating media directories..."
mkdir -p media/training_programs
mkdir -p media/training_images

# Copy existing images to media directory for production
echo "Copying existing images to media directory..."
if [ -d "training_app/static/training_images" ]; then
    cp training_app/static/training_images/* media/training_programs/ 2>/dev/null || echo "No static images to copy"
fi

# Copy any uploaded images from media to static directory (for persistence)
echo "Copying uploaded images to static directory..."
if [ -d "media/training_programs" ]; then
    mkdir -p training_app/static/training_images
    cp media/training_programs/* training_app/static/training_images/ 2>/dev/null || echo "No uploaded images to copy"
fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=toyota_training.settings_production

# List collected static files to verify
echo "Checking collected static files..."
ls -la staticfiles/
if [ -d "staticfiles/training_images" ]; then
    echo "Training images in staticfiles:"
    ls -la staticfiles/training_images/
else
    echo "No training_images directory in staticfiles"
fi

echo "Build completed successfully!"
