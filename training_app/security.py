"""
Security utilities for the Toyota Virtual Training Session Admin application.
"""

import logging
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta
import hashlib
import hmac
import time

logger = logging.getLogger(__name__)


def user_can_access_region(user, region):
    """
    Check if a user can access a specific region.
    
    Args:
        user: The user object
        region: The region string (quebec, central, etc.)
    
    Returns:
        bool: True if user can access the region, False otherwise
    """
    if user.user_type == 'master':
        return True
    
    if user.user_type == 'admin':
        return user.assigned_regions.filter(region=region).exists()
    
    return False


def require_master_user(view_func):
    """
    Decorator to require master user access.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Authentication required")
        
        if request.user.user_type != 'master':
            logger.warning(f"Non-master user {request.user.username} attempted to access master-only view")
            raise PermissionDenied("Master user access required")
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def require_admin_or_master(view_func):
    """
    Decorator to require admin or master user access.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Authentication required")
        
        if request.user.user_type not in ['admin', 'master']:
            logger.warning(f"Unauthorized user {request.user.username} attempted to access admin view")
            raise PermissionDenied("Admin or master user access required")
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def rate_limit_requests(max_requests=5, window_minutes=15):
    """
    Simple rate limiting decorator.
    
    Args:
        max_requests: Maximum number of requests allowed
        window_minutes: Time window in minutes
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            # Get client IP
            client_ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
            
            # Simple in-memory rate limiting (use Redis in production)
            cache_key = f"rate_limit_{client_ip}_{view_func.__name__}"
            
            # This is a simplified implementation
            # In production, use Redis or database-based rate limiting
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def secure_redirect(view_func):
    """
    Decorator to ensure secure redirects.
    """
    def wrapper(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        
        if hasattr(response, 'url') and response.url:
            # Ensure redirects are to safe URLs
            if not response.url.startswith('/') and not response.url.startswith('https://'):
                logger.warning(f"Potentially unsafe redirect attempted: {response.url}")
                response.url = '/'
        
        return response
    
    return wrapper


def generate_secure_token(data, secret_key):
    """
    Generate a secure token for data.
    
    Args:
        data: The data to tokenize
        secret_key: The secret key for signing
    
    Returns:
        str: The secure token
    """
    timestamp = str(int(time.time()))
    message = f"{data}:{timestamp}"
    
    signature = hmac.new(
        secret_key.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return f"{message}:{signature}"


def verify_secure_token(token, secret_key, max_age_seconds=3600):
    """
    Verify a secure token.
    
    Args:
        token: The token to verify
        secret_key: The secret key for verification
        max_age_seconds: Maximum age of the token in seconds
    
    Returns:
        tuple: (is_valid, data) or (False, None)
    """
    try:
        parts = token.split(':')
        if len(parts) != 3:
            return False, None
        
        data, timestamp, signature = parts
        
        # Check timestamp
        token_time = int(timestamp)
        current_time = int(time.time())
        if current_time - token_time > max_age_seconds:
            return False, None
        
        # Verify signature
        message = f"{data}:{timestamp}"
        expected_signature = hmac.new(
            secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            return False, None
        
        return True, data
    
    except (ValueError, TypeError):
        return False, None


def sanitize_input(data):
    """
    Sanitize user input to prevent XSS and other attacks.
    
    Args:
        data: The input data to sanitize
    
    Returns:
        str: The sanitized data
    """
    if not isinstance(data, str):
        return data
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
    for char in dangerous_chars:
        data = data.replace(char, '')
    
    # Limit length
    if len(data) > 1000:
        data = data[:1000]
    
    return data.strip()


def log_security_event(event_type, user, details=None):
    """
    Log security-related events.
    
    Args:
        event_type: Type of security event
        user: The user involved
        details: Additional details
    """
    log_message = f"Security Event: {event_type} - User: {user.username if user else 'Anonymous'}"
    if details:
        log_message += f" - Details: {details}"
    
    logger.warning(log_message)


class SecurityMiddleware:
    """
    Custom security middleware to add additional security headers.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        # Conservative CSP that works with current inline styles/scripts while avoiding risky sources
        # Note: When time permits, migrate inline styles to CSS and remove 'unsafe-inline'
        csp = (
            "default-src 'self'; "
            "img-src 'self' data: https:; "
            "style-src 'self' 'unsafe-inline'; "
            "script-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'"
        )
        if 'Content-Security-Policy' not in response:
            response['Content-Security-Policy'] = csp
        
        return response
