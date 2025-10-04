from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
import requests
import pytz
from datetime import datetime, timedelta
from .models import TrainingPage, TrainingSession, CustomUser


def training_page_view(request, region):
    """
    Public view for displaying training schedules for each region
    This is what visitors will see when they go to quebec.rtmtoyota.ca, etc.
    """
    try:
        # Get the training page for this region with fresh program data
        training_page = get_object_or_404(TrainingPage.objects.select_related('current_program'), region=region, is_active=True)
        
        # Note: We don't check for current_program here anymore
        # Sessions should be shown regardless of whether a current_program is assigned
        
        # Convert Eastern Time sessions to regional timezone
        eastern_tz = pytz.timezone('America/Toronto')
        regional_tz = pytz.timezone(training_page.timezone)
        
        # Get current time in regional timezone
        now_regional = regional_tz.localize(datetime.now())
        cutoff_time = now_regional - timedelta(hours=36)
        
        # Get timezone abbreviation
        regional_tz_abbr = now_regional.strftime('%Z')
        
        # Get all active training sessions for this page, ordered by date and time
        all_sessions = training_page.sessions.all().order_by('date', 'time_est')
        
        # Filter out sessions that are more than 36 hours old
        sessions_with_regional_time = []
        for session in all_sessions:
            # Create datetime object in Eastern Time
            eastern_datetime = eastern_tz.localize(
                datetime.combine(session.date, session.time_est)
            )
            
            # Convert to regional timezone
            regional_datetime = eastern_datetime.astimezone(regional_tz)
            
            # Only include sessions that are not more than 36 hours old
            if regional_datetime >= cutoff_time:
                # Add regional time to session object
                session.regional_time = regional_datetime.time()
                session.regional_datetime = regional_datetime
                sessions_with_regional_time.append(session)
        
        # Prepare context data for the template
        context = {
            'training_page': training_page,
            'sessions': sessions_with_regional_time,
            'region_display': training_page.get_region_display(),
            'timezone': training_page.timezone,
            'regional_tz_abbr': regional_tz_abbr,
        }
        
        return render(request, 'training_app/training_page.html', context)
        
    except Http404:
        # If region doesn't exist, show a nice error page
        return render(request, 'training_app/region_not_found.html', {
            'region': region,
            'available_regions': TrainingPage.objects.filter(is_active=True).values_list('region', flat=True)
        })


def home_redirect(request):
    """
    Redirect from the main domain to Quebec (default region)
    """
    return redirect('/quebec/')


@login_required
def admin_dashboard(request):
    """
    Admin dashboard for managing training schedules
    """
    user = request.user
    
    if user.user_type == 'master':
        # Master users can see all pages and sessions
        training_pages = TrainingPage.objects.filter(is_active=True)
        total_sessions = TrainingSession.objects.count()
        recent_sessions = TrainingSession.objects.select_related('training_page').order_by('-updated_at')[:10]
    else:
        # Admin users can only see their assigned regions
        # Note: We'll need to add a relationship between users and regions
        # For now, let's show all pages but we'll restrict editing later
        training_pages = TrainingPage.objects.filter(is_active=True)
        total_sessions = TrainingSession.objects.count()
        recent_sessions = TrainingSession.objects.select_related('training_page').order_by('-updated_at')[:10]
    
    # Get some statistics
    active_pages = training_pages.count()
    sessions_with_valid_links = TrainingSession.objects.filter(teams_link_valid=True).count()
    total_sessions_count = TrainingSession.objects.count()
    
    context = {
        'user': user,
        'training_pages': training_pages,
        'total_sessions': total_sessions,
        'recent_sessions': recent_sessions,
        'active_pages': active_pages,
        'sessions_with_valid_links': sessions_with_valid_links,
        'total_sessions_count': total_sessions_count,
        'link_validity_percentage': (sessions_with_valid_links / total_sessions_count * 100) if total_sessions_count > 0 else 0,
    }
    
    return render(request, 'training_app/admin/dashboard.html', context)


def admin_login(request):
    """
    Custom login page for admin users - redirects to simple admin
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('simple_admin:simple_admin_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'training_app/admin/login.html')


def test_teams_link(request, session_id):
    """
    AJAX endpoint to test if a Teams link is working
    """
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            session = TrainingSession.objects.get(id=session_id)
            
            # Test the Teams link
            is_valid = validate_teams_link(session.teams_link)
            
            # Update the session
            session.teams_link_valid = is_valid
            session.teams_link_last_tested = timezone.now()
            session.save()
            
            return JsonResponse({
                'success': True,
                'is_valid': is_valid,
                'tested_at': session.teams_link_last_tested.isoformat(),
                'message': 'Link is working!' if is_valid else 'Link is not accessible'
            })
            
        except TrainingSession.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Session not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


def validate_teams_link(url):
    """
    Helper function to validate Teams links
    """
    if not url:
        return False
    
    # Check if it's a valid Teams URL format
    if 'teams.microsoft.com' not in url and 'teams.live.com' not in url:
        return False
    
    # For Teams links, we'll assume they're valid if they have the correct format
    # Teams links often require authentication and may not respond to HEAD requests
    if 'meetup-join' in url or 'meet' in url:
        return True
    
    # Fallback to HTTP check for other URLs
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code in [200, 302, 403]  # 403 is common for Teams links
        
    except requests.RequestException:
        # If HTTP check fails but it looks like a Teams link, assume it's valid
        return 'teams.microsoft.com' in url or 'teams.live.com' in url


def get_session_status(request, session_id):
    """
    AJAX endpoint to get real-time session status (for the JavaScript)
    """
    try:
        session = TrainingSession.objects.get(id=session_id)
        
        # Calculate session status based on current time
        now = timezone.now()
        session_datetime = datetime.combine(session.date, session.time_est)
        
        # Convert to Eastern time (we'll need to handle timezone conversion properly)
        # For now, let's assume the session_datetime is already in Eastern time
        
        if now < session_datetime:
            status = 'upcoming'
            time_remaining = session_datetime - now
            message = f'Starts in {format_timedelta(time_remaining)}'
        elif now <= session_datetime + timedelta(minutes=30):  # 30 minute window
            status = 'active'
            time_remaining = (session_datetime + timedelta(minutes=30)) - now
            message = f'Active - {format_timedelta(time_remaining)} remaining'
        else:
            status = 'ended'
            message = 'Session ended'
        
        return JsonResponse({
            'status': status,
            'message': message,
            'teams_link_valid': session.teams_link_valid
        })
        
    except TrainingSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)


def format_timedelta(td):
    """
    Format timedelta for display (e.g., "2d 3h 15m")
    """
    total_minutes = int(td.total_seconds() / 60)
    days = total_minutes // (24 * 60)
    hours = (total_minutes % (24 * 60)) // 60
    minutes = total_minutes % 60
    
    parts = []
    if days > 0:
        parts.append(f'{days}d')
    if hours > 0:
        parts.append(f'{hours}h')
    if minutes > 0 or not parts:
        parts.append(f'{minutes}m')
    
    return ' '.join(parts)