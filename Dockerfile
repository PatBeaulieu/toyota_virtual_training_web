# Dockerfile for Toyota Virtual Training Session Admin
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        gettext \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements_production.txt /app/
RUN pip install --no-cache-dir -r requirements_production.txt

# Copy project
COPY . /app/

# Create directories for logs and media
RUN mkdir -p logs media staticfiles

# Set proper permissions
RUN chmod -R 755 /app
RUN chmod +x /app/start.sh

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port (Railway will provide PORT env var)
EXPOSE 8000

# Run the application using start.sh which handles PORT properly
CMD ["bash", "start.sh"]
