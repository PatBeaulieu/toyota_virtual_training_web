#!/bin/bash
# Build script for Render deployment

echo "Starting build process..."

# Ensure gunicorn is installed
pip install gunicorn==21.2.0

# Install all dependencies
pip install -r requirements.txt

# Create appgunicorn alias to handle Render's command
echo "Creating appgunicorn alias..."
cat > appgunicorn << 'EOF'
#!/bin/bash
exec gunicorn "$@"
EOF
chmod +x appgunicorn

# Collect static files
python manage.py collectstatic --noinput --settings=toyota_training.settings_production

echo "Build completed successfully!"
