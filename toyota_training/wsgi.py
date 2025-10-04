"""
WSGI config for toyota_training project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toyota_training.settings_production')

application = get_wsgi_application()

# Configure WhiteNoise to serve static and media files
from django.conf import settings
from whitenoise.storage import CompressedManifestStaticFilesStorage

# Serve both static files and media files
application = WhiteNoise(application, root=settings.STATIC_ROOT)
application.add_files(settings.MEDIA_ROOT, prefix=settings.MEDIA_URL.strip('/'))
