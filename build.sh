#!/bin/bash
# Build script for Render deployment

echo "Starting build process..."

# Install dependencies (already done by Render)
echo "Dependencies installed by Render"

# Collect static files
python manage.py collectstatic --noinput --settings=toyota_training.settings_production

echo "Build completed successfully!"
