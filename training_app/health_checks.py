"""
Health check endpoints for the Toyota Virtual Training Session Admin application.
"""

from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def health_check(request):
    """
    Basic health check endpoint.
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'Toyota Virtual Training Session Admin',
        'version': '1.0.0'
    })


def detailed_health_check(request):
    """
    Detailed health check with database and cache status.
    """
    health_status = {
        'status': 'healthy',
        'service': 'Toyota Virtual Training Session Admin',
        'version': '1.0.0',
        'checks': {}
    }
    
    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        health_status['checks']['database'] = {
            'status': 'healthy',
            'message': 'Database connection successful'
        }
    except Exception as e:
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'message': f'Database connection failed: {str(e)}'
        }
        health_status['status'] = 'unhealthy'
    
    # Cache check
    try:
        cache.set('health_check', 'test', 10)
        cache.get('health_check')
        health_status['checks']['cache'] = {
            'status': 'healthy',
            'message': 'Cache connection successful'
        }
    except Exception as e:
        health_status['checks']['cache'] = {
            'status': 'unhealthy',
            'message': f'Cache connection failed: {str(e)}'
        }
        health_status['status'] = 'unhealthy'
    
    # Static files check
    try:
        import os
        static_dir = os.path.join(settings.BASE_DIR, 'staticfiles')
        if os.path.exists(static_dir):
            health_status['checks']['static_files'] = {
                'status': 'healthy',
                'message': 'Static files directory exists'
            }
        else:
            health_status['checks']['static_files'] = {
                'status': 'warning',
                'message': 'Static files directory not found'
            }
    except Exception as e:
        health_status['checks']['static_files'] = {
            'status': 'unhealthy',
            'message': f'Static files check failed: {str(e)}'
        }
    
    # Media files check
    try:
        import os
        media_dir = os.path.join(settings.BASE_DIR, 'media')
        if os.path.exists(media_dir):
            health_status['checks']['media_files'] = {
                'status': 'healthy',
                'message': 'Media files directory exists'
            }
        else:
            health_status['checks']['media_files'] = {
                'status': 'warning',
                'message': 'Media files directory not found'
            }
    except Exception as e:
        health_status['checks']['media_files'] = {
            'status': 'unhealthy',
            'message': f'Media files check failed: {str(e)}'
        }
    
    # Return appropriate status code
    status_code = 200 if health_status['status'] == 'healthy' else 503
    
    return JsonResponse(health_status, status=status_code)


def readiness_check(request):
    """
    Readiness check for Kubernetes/Docker deployments.
    """
    try:
        # Check if the application is ready to serve requests
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM django_migrations")
            cursor.fetchone()
        
        return JsonResponse({
            'status': 'ready',
            'message': 'Application is ready to serve requests'
        })
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return JsonResponse({
            'status': 'not_ready',
            'message': f'Application is not ready: {str(e)}'
        }, status=503)


def liveness_check(request):
    """
    Liveness check for Kubernetes/Docker deployments.
    """
    return JsonResponse({
        'status': 'alive',
        'message': 'Application is alive'
    })
