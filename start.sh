#!/bin/bash
# Simple startup script for Render

echo "🚀 Starting Toyota Virtual Training Application..."

# Check if gunicorn is available
if ! command -v gunicorn &> /dev/null; then
    echo "Installing gunicorn..."
    pip install gunicorn==21.2.0
fi

# Create appgunicorn alias if it doesn't exist
if [ ! -f "./appgunicorn" ]; then
    echo "Creating appgunicorn alias..."
    cat > appgunicorn << 'EOF'
#!/bin/bash
exec gunicorn "$@"
EOF
    chmod +x appgunicorn
fi

# Add current directory to PATH
export PATH="$PWD:$PATH"

# Start the application
echo "Starting gunicorn server..."
exec gunicorn toyota_training.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 30