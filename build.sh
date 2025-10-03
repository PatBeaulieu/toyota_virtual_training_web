#!/bin/bash
# Build script for Render deployment

echo "Starting build process..."

# Ensure gunicorn is installed
pip install gunicorn==21.2.0

# Install all dependencies
pip install -r requirements.txt

# Install psycopg2 only if PostgreSQL is explicitly enabled
if [ "$USE_POSTGRES" = "true" ]; then
    echo "Installing PostgreSQL support..."
    pip install psycopg2-binary==2.9.10
else
    echo "Using SQLite (PostgreSQL support skipped)"
fi

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

# Collect static files
python manage.py collectstatic --noinput --settings=toyota_training.settings_production

echo "Build completed successfully!"
