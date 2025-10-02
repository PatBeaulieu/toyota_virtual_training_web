"""
Custom validators for the Toyota Virtual Training Session Admin application.
"""

import re
import logging
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import URLValidator
from django.conf import settings
import requests
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def validate_teams_link(value):
    """
    Validate Microsoft Teams meeting links.
    
    Args:
        value: The Teams link to validate
    
    Returns:
        str: The validated link
    
    Raises:
        ValidationError: If the link is invalid
    """
    if not value:
        return value
    
    # Basic URL validation
    url_validator = URLValidator()
    try:
        url_validator(value)
    except ValidationError:
        raise ValidationError(_('Please enter a valid URL.'))
    
    # Check if it's a Teams link
    parsed_url = urlparse(value)
    
    # Valid Teams domains
    valid_domains = [
        'teams.microsoft.com',
        'teams.live.com',
        'teams.microsoft.us',
        'teams.microsoft.de',
        'teams.microsoft.cn'
    ]
    
    if parsed_url.netloc.lower() not in valid_domains:
        raise ValidationError(_('Please enter a valid Microsoft Teams meeting link.'))
    
    # Check for required Teams patterns
    teams_patterns = [
        'meetup-join',
        'meet',
        'l/meetup-join',
        'l/meet'
    ]
    
    if not any(pattern in value.lower() for pattern in teams_patterns):
        raise ValidationError(_('This does not appear to be a valid Teams meeting link.'))
    
    return value


def validate_region(value):
    """
    Validate region values.
    
    Args:
        value: The region to validate
    
    Returns:
        str: The validated region
    
    Raises:
        ValidationError: If the region is invalid
    """
    valid_regions = ['quebec', 'central', 'pacific', 'prairie', 'atlantic']
    
    if value.lower() not in valid_regions:
        raise ValidationError(_('Invalid region. Must be one of: %(regions)s') % {
            'regions': ', '.join(valid_regions)
        })
    
    return value.lower()


def validate_timezone(value):
    """
    Validate timezone values.
    
    Args:
        value: The timezone to validate
    
    Returns:
        str: The validated timezone
    
    Raises:
        ValidationError: If the timezone is invalid
    """
    import pytz
    
    try:
        pytz.timezone(value)
    except pytz.exceptions.UnknownTimeZoneError:
        raise ValidationError(_('Invalid timezone. Please use a valid timezone identifier (e.g., America/Toronto).'))
    
    return value


def validate_password_strength(value):
    """
    Validate password strength.
    
    Args:
        value: The password to validate
    
    Returns:
        str: The validated password
    
    Raises:
        ValidationError: If the password is too weak
    """
    if len(value) < 12:
        raise ValidationError(_('Password must be at least 12 characters long.'))
    
    if not re.search(r'[A-Z]', value):
        raise ValidationError(_('Password must contain at least one uppercase letter.'))
    
    if not re.search(r'[a-z]', value):
        raise ValidationError(_('Password must contain at least one lowercase letter.'))
    
    if not re.search(r'\d', value):
        raise ValidationError(_('Password must contain at least one digit.'))
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError(_('Password must contain at least one special character.'))
    
    # Check for common patterns
    common_patterns = [
        r'123',
        r'abc',
        r'password',
        r'qwerty',
        r'admin'
    ]
    
    for pattern in common_patterns:
        if re.search(pattern, value.lower()):
            raise ValidationError(_('Password contains common patterns and is not secure.'))
    
    return value


def validate_username(value):
    """
    Validate username format.
    
    Args:
        value: The username to validate
    
    Returns:
        str: The validated username
    
    Raises:
        ValidationError: If the username is invalid
    """
    if len(value) < 3:
        raise ValidationError(_('Username must be at least 3 characters long.'))
    
    if len(value) > 30:
        raise ValidationError(_('Username must be no more than 30 characters long.'))
    
    if not re.match(r'^[a-zA-Z0-9._-]+$', value):
        raise ValidationError(_('Username can only contain letters, numbers, dots, underscores, and hyphens.'))
    
    if value.startswith('.') or value.endswith('.'):
        raise ValidationError(_('Username cannot start or end with a dot.'))
    
    if '..' in value:
        raise ValidationError(_('Username cannot contain consecutive dots.'))
    
    return value.lower()


def validate_email_domain(value):
    """
    Validate email domain against allowed domains.
    
    Args:
        value: The email to validate
    
    Returns:
        str: The validated email
    
    Raises:
        ValidationError: If the email domain is not allowed
    """
    if not value:
        return value
    
    # Check if email domain is allowed (if configured)
    allowed_domains = getattr(settings, 'ALLOWED_EMAIL_DOMAINS', [])
    
    if allowed_domains:
        domain = value.split('@')[1].lower()
        if domain not in allowed_domains:
            raise ValidationError(_('Email domain is not allowed. Please use a company email address.'))
    
    return value


def validate_file_size(file):
    """
    Validate uploaded file size.
    
    Args:
        file: The uploaded file
    
    Returns:
        file: The validated file
    
    Raises:
        ValidationError: If the file is too large
    """
    max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 5 * 1024 * 1024)  # 5MB default
    
    if file.size > max_size:
        raise ValidationError(_('File size cannot exceed %(size)s MB.') % {
            'size': max_size // (1024 * 1024)
        })
    
    return file


def validate_image_format(file):
    """
    Validate uploaded image format.
    
    Args:
        file: The uploaded image file
    
    Returns:
        file: The validated file
    
    Raises:
        ValidationError: If the image format is not allowed
    """
    allowed_formats = ['JPEG', 'JPG', 'PNG', 'GIF', 'WEBP']
    
    if hasattr(file, 'content_type'):
        content_type = file.content_type
        if not any(fmt.lower() in content_type.lower() for fmt in allowed_formats):
            raise ValidationError(_('Only JPEG, PNG, GIF, and WEBP images are allowed.'))
    
    return file


def validate_training_session_date(value):
    """
    Validate training session date.
    
    Args:
        value: The date to validate
    
    Returns:
        date: The validated date
    
    Raises:
        ValidationError: If the date is invalid
    """
    from datetime import date, timedelta
    
    today = date.today()
    max_future_date = today + timedelta(days=365)  # 1 year in the future
    min_past_date = today - timedelta(days=30)  # 30 days in the past
    
    if value > max_future_date:
        raise ValidationError(_('Training session cannot be scheduled more than 1 year in the future.'))
    
    if value < min_past_date:
        raise ValidationError(_('Training session cannot be scheduled more than 30 days in the past.'))
    
    return value


def validate_training_session_time(value):
    """
    Validate training session time.
    
    Args:
        value: The time to validate
    
    Returns:
        time: The validated time
    
    Raises:
        ValidationError: If the time is invalid
    """
    from datetime import time
    
    # Business hours: 8:00 AM to 6:00 PM
    business_start = time(8, 0)
    business_end = time(18, 0)
    
    if value < business_start or value > business_end:
        raise ValidationError(_('Training sessions can only be scheduled during business hours (8:00 AM - 6:00 PM).'))
    
    return value


def sanitize_html(value):
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Args:
        value: The HTML content to sanitize
    
    Returns:
        str: The sanitized content
    """
    if not isinstance(value, str):
        return value
    
    # Remove script tags and event handlers
    import re
    
    # Remove script tags
    value = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', value, flags=re.IGNORECASE)
    
    # Remove event handlers
    event_handlers = [
        'onload', 'onerror', 'onclick', 'onmouseover', 'onmouseout',
        'onfocus', 'onblur', 'onchange', 'onsubmit', 'onreset'
    ]
    
    for handler in event_handlers:
        pattern = rf'{handler}\s*=\s*["\'][^"\']*["\']'
        value = re.sub(pattern, '', value, flags=re.IGNORECASE)
    
    return value


def validate_csrf_token(request):
    """
    Validate CSRF token for additional security.
    
    Args:
        request: The HTTP request
    
    Returns:
        bool: True if token is valid, False otherwise
    """
    from django.middleware.csrf import get_token
    
    token = request.POST.get('csrfmiddlewaretoken')
    if not token:
        return False
    
    expected_token = get_token(request)
    return token == expected_token
