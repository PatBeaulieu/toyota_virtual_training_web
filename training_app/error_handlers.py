"""
Custom error handlers for the Toyota Virtual Training Session Admin application.
"""

import logging
from django.http import HttpResponseServerError, HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import render
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


@never_cache
def custom_400_handler(request, exception=None):
    """
    Custom 400 Bad Request handler.
    """
    logger.warning(f"400 Bad Request: {request.path} - {request.method}")
    return render(request, 'training_app/errors/400.html', status=400)


@never_cache
def custom_403_handler(request, exception=None):
    """
    Custom 403 Forbidden handler.
    """
    logger.warning(f"403 Forbidden: {request.path} - User: {request.user if hasattr(request, 'user') else 'Anonymous'}")
    return render(request, 'training_app/errors/403.html', status=403)


@never_cache
def custom_404_handler(request, exception=None):
    """
    Custom 404 Not Found handler.
    """
    logger.warning(f"404 Not Found: {request.path}")
    return render(request, 'training_app/errors/404.html', status=404)


@never_cache
def custom_500_handler(request, exception=None):
    """
    Custom 500 Internal Server Error handler.
    """
    logger.error(f"500 Internal Server Error: {request.path} - Exception: {str(exception)}", exc_info=True)
    return render(request, 'training_app/errors/500.html', status=500)


class ErrorLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log errors and exceptions.
    """
    
    def process_exception(self, request, exception):
        """
        Log exceptions that occur during request processing.
        """
        logger.error(
            f"Unhandled exception in {request.path}: {str(exception)}",
            exc_info=True,
            extra={
                'request_path': request.path,
                'request_method': request.method,
                'user': getattr(request, 'user', None),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'remote_addr': request.META.get('REMOTE_ADDR', ''),
            }
        )
        return None


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to all responses.
    """
    
    def process_response(self, request, response):
        """
        Add security headers to the response.
        """
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        
        # Other security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = (
            'geolocation=(), '
            'microphone=(), '
            'camera=(), '
            'payment=(), '
            'usb=(), '
            'magnetometer=(), '
            'accelerometer=(), '
            'gyroscope=(), '
            'speaker=()'
        )
        
        # Strict Transport Security (only for HTTPS)
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        return response


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all requests for security monitoring.
    """
    
    def process_request(self, request):
        """
        Log incoming requests.
        """
        # Only log in production or when explicitly enabled
        if settings.DEBUG and not getattr(settings, 'LOG_ALL_REQUESTS', False):
            return
        
        # Skip logging for static files and common paths
        skip_paths = ['/static/', '/media/', '/favicon.ico']
        if any(request.path.startswith(path) for path in skip_paths):
            return
        
        logger.info(
            f"Request: {request.method} {request.path}",
            extra={
                'request_path': request.path,
                'request_method': request.method,
                'user': getattr(request, 'user', None),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'remote_addr': request.META.get('REMOTE_ADDR', ''),
                'referer': request.META.get('HTTP_REFERER', ''),
            }
        )


def safe_get_client_ip(request):
    """
    Safely get the client IP address from the request.
    """
    # Check for forwarded IP first (for load balancers/proxies)
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        # Take the first IP in the chain
        return forwarded_for.split(',')[0].strip()
    
    # Fall back to remote address
    return request.META.get('REMOTE_ADDR', 'unknown')


def log_security_event(event_type, request, details=None, user=None):
    """
    Log security-related events.
    
    Args:
        event_type: Type of security event
        request: The HTTP request
        details: Additional details
        user: The user involved
    """
    client_ip = safe_get_client_ip(request)
    user_info = user.username if user and user.is_authenticated else 'Anonymous'
    
    log_message = (
        f"Security Event: {event_type} - "
        f"User: {user_info} - "
        f"IP: {client_ip} - "
        f"Path: {request.path}"
    )
    
    if details:
        log_message += f" - Details: {details}"
    
    logger.warning(log_message, extra={
        'event_type': event_type,
        'user': user_info,
        'client_ip': client_ip,
        'request_path': request.path,
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'details': details,
    })


def handle_database_error(request, exception, operation):
    """
    Handle database errors gracefully.
    
    Args:
        request: The HTTP request
        exception: The database exception
        operation: Description of the operation that failed
    
    Returns:
        HttpResponse: Error response
    """
    logger.error(
        f"Database error during {operation}: {str(exception)}",
        exc_info=True,
        extra={
            'operation': operation,
            'user': getattr(request, 'user', None),
            'request_path': request.path,
        }
    )
    
    return render(
        request,
        'training_app/errors/database_error.html',
        {'operation': operation},
        status=500
    )


def handle_permission_error(request, exception, resource):
    """
    Handle permission errors gracefully.
    
    Args:
        request: The HTTP request
        exception: The permission exception
        resource: Description of the resource that was accessed
    
    Returns:
        HttpResponse: Error response
    """
    user = getattr(request, 'user', None)
    user_info = user.username if user and user.is_authenticated else 'Anonymous'
    
    logger.warning(
        f"Permission denied for {user_info} accessing {resource}: {str(exception)}",
        extra={
            'user': user_info,
            'resource': resource,
            'request_path': request.path,
        }
    )
    
    return render(
        request,
        'training_app/errors/permission_denied.html',
        {'resource': resource},
        status=403
    )
