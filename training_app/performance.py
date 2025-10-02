"""
Performance optimization utilities for the Toyota Virtual Training Session Admin application.
"""

import logging
from django.db import connection
from django.core.cache import cache
from django.conf import settings
from functools import wraps
import time

logger = logging.getLogger(__name__)


def monitor_db_queries(func):
    """
    Decorator to monitor database queries in development.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not settings.DEBUG:
            return func(*args, **kwargs)
        
        initial_queries = len(connection.queries)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            
            final_queries = len(connection.queries)
            query_count = final_queries - initial_queries
            execution_time = time.time() - start_time
            
            if query_count > 10:  # Log if more than 10 queries
                logger.warning(
                    f"High query count in {func.__name__}: {query_count} queries in {execution_time:.2f}s"
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
    
    return wrapper


def cache_result(timeout=300):
    """
    Decorator to cache function results.
    
    Args:
        timeout: Cache timeout in seconds (default: 5 minutes)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            
            return result
        
        return wrapper
    return decorator


def optimize_queryset(queryset, select_related=None, prefetch_related=None):
    """
    Optimize a queryset with select_related and prefetch_related.
    
    Args:
        queryset: The queryset to optimize
        select_related: Fields for select_related
        prefetch_related: Fields for prefetch_related
    
    Returns:
        QuerySet: The optimized queryset
    """
    if select_related:
        queryset = queryset.select_related(*select_related)
    
    if prefetch_related:
        queryset = queryset.prefetch_related(*prefetch_related)
    
    return queryset


def get_optimized_training_sessions(user=None, region=None):
    """
    Get training sessions with optimized queries.
    
    Args:
        user: The user requesting the data
        region: Optional region filter
    
    Returns:
        QuerySet: Optimized training sessions queryset
    """
    from .models import TrainingSession
    
    queryset = TrainingSession.objects.select_related(
        'training_page',
        'training_program'
    ).prefetch_related(
        'training_program__trainingpage_set'
    )
    
    if region:
        queryset = queryset.filter(training_page__region=region)
    
    if user and user.user_type == 'admin':
        # Admin users can only see their assigned regions
        assigned_regions = user.assigned_regions.values_list('id', flat=True)
        queryset = queryset.filter(training_page__id__in=assigned_regions)
    
    return queryset.order_by('date', 'time_est')


def get_optimized_training_programs():
    """
    Get training programs with optimized queries.
    
    Returns:
        QuerySet: Optimized training programs queryset
    """
    from .models import TrainingProgram
    
    return TrainingProgram.objects.filter(
        is_active=True
    ).prefetch_related(
        'trainingpage_set'
    ).order_by('-created_at')


def get_optimized_training_pages():
    """
    Get training pages with optimized queries.
    
    Returns:
        QuerySet: Optimized training pages queryset
    """
    from .models import TrainingPage
    
    return TrainingPage.objects.filter(
        is_active=True
    ).select_related(
        'current_program'
    ).prefetch_related(
        'sessions',
        'sessions__training_program'
    ).order_by('region')


@cache_result(timeout=600)  # Cache for 10 minutes
def get_dashboard_stats(user):
    """
    Get dashboard statistics with caching.
    
    Args:
        user: The user requesting the stats
    
    Returns:
        dict: Dashboard statistics
    """
    from .models import TrainingSession, TrainingProgram, TrainingPage
    
    if user.user_type == 'master':
        # Master users see all data
        total_sessions = TrainingSession.objects.count()
        total_programs = TrainingProgram.objects.filter(is_active=True).count()
        total_users = user.__class__.objects.count()
        
        # Recent sessions
        recent_sessions = TrainingSession.objects.select_related(
            'training_page', 'training_program'
        ).order_by('-created_at')[:5]
        
    else:
        # Admin users see limited data
        assigned_regions = user.assigned_regions.values_list('id', flat=True)
        
        total_sessions = TrainingSession.objects.filter(
            training_page__id__in=assigned_regions
        ).count()
        
        total_programs = TrainingProgram.objects.filter(is_active=True).count()
        total_users = 0  # Admin users don't see user count
        
        # Recent sessions for assigned regions
        recent_sessions = TrainingSession.objects.filter(
            training_page__id__in=assigned_regions
        ).select_related(
            'training_page', 'training_program'
        ).order_by('-created_at')[:5]
    
    return {
        'total_sessions': total_sessions,
        'total_programs': total_programs,
        'total_users': total_users,
        'recent_sessions': list(recent_sessions),
    }


def batch_update_sessions(session_ids, updates):
    """
    Batch update multiple training sessions.
    
    Args:
        session_ids: List of session IDs to update
        updates: Dictionary of field updates
    
    Returns:
        int: Number of updated sessions
    """
    from .models import TrainingSession
    
    return TrainingSession.objects.filter(
        id__in=session_ids
    ).update(**updates)


def get_calendar_sessions(user, month=None, year=None):
    """
    Get calendar sessions with optimized queries.
    
    Args:
        user: The user requesting the data
        month: Optional month filter
        year: Optional year filter
    
    Returns:
        QuerySet: Optimized calendar sessions queryset
    """
    from django.utils import timezone
    from datetime import datetime, timedelta
    from .models import TrainingSession
    
    # Default to current month
    if not month or not year:
        now = timezone.now().date()
        month = month or now.month
        year = year or now.year
    
    # Calculate month boundaries
    first_day = datetime(year, month, 1).date()
    if month == 12:
        last_day = datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        last_day = datetime(year, month + 1, 1).date() - timedelta(days=1)
    
    queryset = TrainingSession.objects.filter(
        date__gte=first_day,
        date__lte=last_day
    ).select_related(
        'training_page',
        'training_program'
    )
    
    if user.user_type == 'admin':
        # Admin users can only see their assigned regions
        assigned_regions = user.assigned_regions.values_list('id', flat=True)
        queryset = queryset.filter(training_page__id__in=assigned_regions)
    
    return queryset.order_by('date', 'time_est')


class QueryOptimizer:
    """
    Context manager for optimizing database queries.
    """
    
    def __init__(self, queryset, select_related=None, prefetch_related=None):
        self.queryset = queryset
        self.select_related = select_related
        self.prefetch_related = prefetch_related
    
    def __enter__(self):
        if self.select_related:
            self.queryset = self.queryset.select_related(*self.select_related)
        
        if self.prefetch_related:
            self.queryset = self.queryset.prefetch_related(*self.prefetch_related)
        
        return self.queryset
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def log_slow_queries(threshold=1.0):
    """
    Log slow database queries.
    
    Args:
        threshold: Time threshold in seconds
    """
    if not settings.DEBUG:
        return
    
    for query in connection.queries:
        if float(query['time']) > threshold:
            logger.warning(
                f"Slow query ({query['time']}s): {query['sql'][:200]}..."
            )
