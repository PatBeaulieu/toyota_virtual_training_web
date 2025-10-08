"""
Production settings for Toyota Virtual Training Session Admin.

This file contains production-specific settings that override the base settings.
Never commit this file with real secrets to version control.
"""

import os
from pathlib import Path
import dj_database_url
from .settings import *

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
# Generate a new secret key for production using:
# python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-production-secret-key-here')

# Allowed hosts for production
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.herokuapp.com',  # Heroku domains
    '.onrender.com',   # Render domains - covers all Render subdomains
    '.render.com',     # Alternative Render domain format
    'render.com',      # Main Render domain
    '.railway.app',    # Railway domains
    'railway.app',     # Railway main domain
    'rtmtoyota.ca',    # Main domain
    '.rtmtoyota.ca',   # Wildcard - allows quebec.rtmtoyota.ca, central.rtmtoyota.ca, etc.
    '*.rtmtoyota.ca',  # Explicit wildcard notation
]

# Add Render's external hostname if available (this is automatically set by Render)
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Add Railway's domain if available (this is automatically set by Railway)
RAILWAY_STATIC_URL = os.environ.get('RAILWAY_STATIC_URL')
RAILWAY_PUBLIC_DOMAIN = os.environ.get('RAILWAY_PUBLIC_DOMAIN')
if RAILWAY_STATIC_URL:
    ALLOWED_HOSTS.append(RAILWAY_STATIC_URL)
if RAILWAY_PUBLIC_DOMAIN:
    ALLOWED_HOSTS.append(RAILWAY_PUBLIC_DOMAIN)

# For development/testing - allow all hosts if DEBUG is True
if DEBUG:
    ALLOWED_HOSTS = ['*']

# Application definition - ensure we have the right apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary_storage',  # For cloud file storage
    'cloudinary',  # Cloudinary integration
    'training_app',  # Our training app
    'whitenoise.runserver_nostatic',  # For serving static files
]

# Middleware configuration
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For static files
    'training_app.subdomain_middleware.SubdomainRoutingMiddleware',  # Subdomain routing
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Database configuration for production
# PostgreSQL is REQUIRED for production deployments

if os.environ.get('DATABASE_URL'):
    # Use DATABASE_URL if provided (format: postgres://user:password@host:port/dbname)
    # This is the preferred method for platforms like Heroku, Render, Railway
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,  # Connection pooling: keep connections alive for 10 minutes
            conn_health_checks=True,  # Check connection health before reusing
            ssl_require=False,  # Set based on your hosting provider's requirements
        )
    }
    # Override sslmode if needed (some providers require 'require', others use 'disable')
    if 'sslmode' not in DATABASES['default'].get('OPTIONS', {}):
        DATABASES['default'].setdefault('OPTIONS', {})['sslmode'] = 'prefer'
    
    print("✅ Using PostgreSQL database via DATABASE_URL")
    
elif os.environ.get('DB_NAME'):
    # Use individual environment variables for PostgreSQL
    # This method provides more granular control
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
            'CONN_MAX_AGE': 600,  # Connection pooling
            'OPTIONS': {
                'connect_timeout': 10,  # Timeout for initial connection
                'sslmode': os.environ.get('DB_SSLMODE', 'prefer'),  # SSL configuration
                # Performance optimizations
                'options': '-c statement_timeout=30000',  # 30 second statement timeout
            },
            # Additional pool configuration for production
            'ATOMIC_REQUESTS': True,  # Wrap each request in a transaction
            'AUTOCOMMIT': True,
        }
    }
    print("✅ Using PostgreSQL database")
    
else:
    # No database configuration found
    # Check if we're running a command that doesn't need database (like collectstatic during build)
    import sys
    RAILWAY_BUILD_COMMANDS = ['collectstatic', 'compress', 'compilemessages']
    is_build_command = any(cmd in sys.argv for cmd in RAILWAY_BUILD_COMMANDS)
    
    if not DEBUG and not is_build_command:
        # FAIL LOUDLY in production for runtime commands
        raise RuntimeError(
            "🚨 CRITICAL: No PostgreSQL configuration found!\n"
            "Production requires PostgreSQL. Please set DATABASE_URL or individual DB_* variables.\n"
            "See PRODUCTION_DEPLOYMENT_POSTGRESQL.md for configuration instructions."
        )
    else:
        # Use dummy database for build-time commands or development
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
        if is_build_command:
            print("⚠️ Using dummy database for build command (DATABASE_URL will be required at runtime)")
        else:
            print("⚠️ Using SQLite database (DEVELOPMENT MODE ONLY)")

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Session security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# CSRF security
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS = [
    'https://training.rtmtoyota.ca',  # Your custom domain
    'https://rtmtoyota.ca',
    'https://admin.rtmtoyota.ca',
    'https://*.rtmtoyota.ca',  # Allow all subdomains
    'https://*.onrender.com',  # Render domains
    'https://*.render.com',    # Alternative Render domain format
    'https://*.railway.app',   # Railway domains
]

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Static files directories - CRITICAL for finding app static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'training_app', 'static'),
]

# Media files configuration (use cloud storage in production)
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@rtmtoyota.ca')

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'training_app': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Cache configuration (use database cache for simplicity)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
}

# Session engine
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Password validation (stricter for production)
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Rate limiting disabled for now (would need django-ratelimit package)

# Admin URL for security
ADMIN_URL = os.environ.get('ADMIN_URL', 'django-admin/')

# Custom login URLs
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/simple-admin/'
LOGOUT_REDIRECT_URL = '/admin/login/'

# URL Configuration
ROOT_URLCONF = 'toyota_training.urls'

# Template configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI Application
WSGI_APPLICATION = 'toyota_training.wsgi.application'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Toronto'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images) - configured above

# Media files (user uploads) - Using Cloudinary for persistent storage
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Cloudinary configuration for persistent file storage
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', 'your_cloud_name'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY', 'your_api_key'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', 'your_api_secret'),
}

cloudinary.config(
    cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=CLOUDINARY_STORAGE['API_KEY'],
    api_secret=CLOUDINARY_STORAGE['API_SECRET'],
)

# Use Cloudinary for media file storage
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Fallback to local media for development
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'training_app.CustomUser'

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# Timezone
TIME_ZONE = 'America/Toronto'
USE_TZ = True
