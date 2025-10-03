from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.db import transaction
from datetime import timedelta
from .forms import SimpleTrainingProgramForm, SimpleTrainingSessionForm, SimpleUserForm
from .models import TrainingProgram, TrainingSession, TrainingPage, CustomUser
from .security import require_master_user, require_admin_or_master, rate_limit_requests, log_security_event
from .performance import monitor_db_queries, get_optimized_training_sessions, get_dashboard_stats, get_calendar_sessions
from .error_handlers import handle_database_error, handle_permission_error
import logging

User = get_user_model()


@csrf_protect
@require_http_methods(["GET", "POST"])
@rate_limit_requests(max_requests=5, window_minutes=15)
def simple_admin_login(request):
    """
    Simple login page for the simple admin interface with enhanced security
    """
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            return render(request, 'training_app/simple_admin/login.html')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                log_security_event('login_success', request, user=user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                return redirect('simple_admin:simple_admin_dashboard')
            else:
                log_security_event('login_inactive_user', request, user=user)
                messages.error(request, 'Your account is inactive. Please contact your administrator.')
        else:
            log_security_event('login_failed', request, details=f'username: {username}')
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'training_app/simple_admin/login.html')


@login_required
@require_admin_or_master
@monitor_db_queries
def simple_admin_dashboard(request):
    """
    Simple admin dashboard with easy access to main functions
    """
    user = request.user
    
    # Get recent data - filter by user permissions
    if user.user_type == 'master':
        recent_programs = TrainingProgram.objects.filter(is_active=True)[:3]
        recent_sessions = TrainingSession.objects.select_related('training_page').order_by('-created_at')[:5]
        total_sessions = TrainingSession.objects.count()
        total_programs = TrainingProgram.objects.filter(is_active=True).count()  # Only active programs
        total_users = CustomUser.objects.count()
        
        # Calendar sessions for master users (all regions)
        today = timezone.now().date()
        first_day = today.replace(day=1)
        if today.month == 12:
            last_day = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            last_day = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        
        calendar_sessions = TrainingSession.objects.filter(
            date__gte=first_day,
            date__lte=last_day
        ).select_related('training_page', 'training_program').order_by('date', 'time_est')
    else:
        # Admin users can see all training programs but only their assigned regions
        assigned_pages = user.assigned_regions.all()
        recent_programs = TrainingProgram.objects.filter(is_active=True)[:3]  # Only active programs
        
        # Only show sessions for assigned regions (consistent with manage sessions)
        if assigned_pages:
            recent_sessions = TrainingSession.objects.filter(
                training_page__in=assigned_pages
            ).select_related('training_page').order_by('-created_at')[:5]
            total_sessions = TrainingSession.objects.filter(training_page__in=assigned_pages).count()
            
            # Calendar sessions - get all sessions for assigned regions for the current month
            today = timezone.now().date()
            first_day = today.replace(day=1)
            if today.month == 12:
                last_day = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                last_day = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
            
            calendar_sessions = TrainingSession.objects.filter(
                training_page__in=assigned_pages,
                date__gte=first_day,
                date__lte=last_day
            ).select_related('training_page', 'training_program').order_by('date', 'time_est')
        else:
            recent_sessions = TrainingSession.objects.none()  # No sessions if no assigned regions
            total_sessions = 0
            calendar_sessions = TrainingSession.objects.none()
            
        total_programs = TrainingProgram.objects.filter(is_active=True).count()  # Only active programs
        total_users = 1  # Admin users don't see user count
    
    context = {
        'user': user,
        'recent_programs': recent_programs,
        'recent_sessions': recent_sessions,
        'total_sessions': total_sessions,
        'total_programs': total_programs,
        'total_users': total_users,
    }
    
    # Add calendar_sessions for all users
    if 'calendar_sessions' in locals():
        context['calendar_sessions'] = calendar_sessions
    else:
        context['calendar_sessions'] = None
    
    return render(request, 'training_app/simple_admin/dashboard.html', context)


@login_required
def create_training_program(request):
    """
    Simple form to create a new training program
    Only master users can create training programs
    """
    if request.user.user_type != 'master':
        messages.error(request, '❌ Only master users can create training programs.')
        return redirect('simple_admin:simple_admin_dashboard')
    if request.method == 'POST':
        form = SimpleTrainingProgramForm(request.POST, request.FILES, user=request.user)
        print(f"Form data: {request.POST}")
        print(f"Form files: {request.FILES}")
        print(f"Form is valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
        if form.is_valid():
            program = form.save()
            print(f"Program saved: {program}")
            print(f"Program main_image: {program.main_image}")
            
            # Copy uploaded image to static directory for production persistence
            if program.main_image:
                import os
                import shutil
                from django.conf import settings
                
                try:
                    # Create static directory if it doesn't exist
                    static_images_dir = os.path.join(settings.BASE_DIR, 'training_app', 'static', 'training_images')
                    os.makedirs(static_images_dir, exist_ok=True)
                    
                    # Get the filename from the uploaded image
                    filename = program.main_image.name.split('/')[-1]
                    
                    # Copy the uploaded image to static directory
                    source_path = program.main_image.path
                    destination_path = os.path.join(static_images_dir, filename)
                    
                    # Ensure source file exists
                    if os.path.exists(source_path):
                        shutil.copy2(source_path, destination_path)
                        print(f"✅ Copied image from {source_path} to {destination_path}")
                        
                        # Also try to collect static files if in production
                        if not settings.DEBUG:
                            try:
                                from django.core.management import call_command
                                call_command('collectstatic', '--noinput', verbosity=0)
                                print(f"✅ Collected static files after image upload")
                            except Exception as collect_error:
                                print(f"⚠️ Could not collect static files: {collect_error}")
                    else:
                        print(f"⚠️ Source image file not found: {source_path}")
                        
                except Exception as e:
                    print(f"❌ Error copying image to static directory: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Auto-assign the new program to all active training pages
            from training_app.models import TrainingPage
            active_pages = TrainingPage.objects.filter(is_active=True)
            updated_count = active_pages.update(current_program=program)
            
            messages.success(request, f'✅ Training program "{program.name}" created successfully and assigned to {updated_count} regions!')
            
            # Redirect to add training sessions for this program
            return redirect('simple_admin:create_training_session_with_program', program_id=program.id)
    else:
        form = SimpleTrainingProgramForm(user=request.user)
    
    return render(request, 'training_app/simple_admin/create_program.html', {
        'form': form
    })


@login_required
def create_training_session(request):
    """
    Simple form to create a new training session
    Admin users can only create sessions for their assigned regions
    """
    user = request.user
    
    if request.method == 'POST':
        form = SimpleTrainingSessionForm(request.POST, user=user)
        if form.is_valid():
            session = form.save(commit=False)
            
            # Handle training_program assignment for readonly fields
            if not session.training_program_id:
                from training_app.models import TrainingProgram
                active_programs = TrainingProgram.objects.filter(is_active=True)
                if active_programs.count() == 1:
                    session.training_program = active_programs.first()
                else:
                    messages.error(request, '❌ Please select a training program.')
                    return redirect('simple_admin:simple_admin_dashboard')
            
            # Handle training_page assignment for readonly fields
            if not session.training_page_id:
                if user.user_type == 'admin':
                    assigned_regions = user.assigned_regions.filter(is_active=True)
                    if assigned_regions.count() == 1:
                        session.training_page = assigned_regions.first()
                    elif assigned_regions.count() > 1:
                        messages.error(request, '❌ Please select a training region.')
                        return redirect('simple_admin:simple_admin_dashboard')
                    else:
                        messages.error(request, '❌ You have no assigned regions. Please contact administrator.')
                        return redirect('simple_admin:simple_admin_dashboard')
                else:
                    # Master users should have the field in cleaned_data
                    messages.error(request, '❌ Please select a training region.')
                    return redirect('simple_admin:simple_admin_dashboard')
            
            session.save()
            messages.success(request, f'✅ Training session created for {session.training_page.get_region_display()} on {session.date}!')
            return redirect('simple_admin:simple_admin_dashboard')
        else:
            # Debug: show form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'❌ {field}: {error}')
    else:
        form = SimpleTrainingSessionForm(user=user)
        
        # Pre-fill date if provided from calendar
        if 'date' in request.GET:
            try:
                from datetime import datetime
                date_str = request.GET['date']
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                form.initial['date'] = date_obj
            except ValueError:
                pass  # Invalid date format, ignore
    
    return render(request, 'training_app/simple_admin/create_session.html', {
        'form': form
    })


@login_required
def create_training_session_with_program(request, program_id):
    """
    Create a training session for a specific program
    This is used after creating a new program to immediately add sessions
    """
    try:
        program = TrainingProgram.objects.get(id=program_id)
    except TrainingProgram.DoesNotExist:
        messages.error(request, '❌ Training program not found.')
        return redirect('simple_admin:simple_admin_dashboard')
    
    user = request.user
    
    if request.method == 'POST':
        form = SimpleTrainingSessionForm(request.POST, user=user)
        if form.is_valid():
            session = form.save(commit=False)
            
            # Handle training_page assignment for readonly fields
            if not session.training_page_id:
                if user.user_type == 'admin':
                    assigned_regions = user.assigned_regions.filter(is_active=True)
                    if assigned_regions.count() == 1:
                        session.training_page = assigned_regions.first()
                    elif assigned_regions.count() > 1:
                        messages.error(request, '❌ Please select a training region.')
                        return redirect('simple_admin:simple_admin_dashboard')
                    else:
                        messages.error(request, '❌ You have no assigned regions. Please contact administrator.')
                        return redirect('simple_admin:simple_admin_dashboard')
                else:
                    # Master users should have the field in cleaned_data
                    messages.error(request, '❌ Please select a training region.')
                    return redirect('simple_admin:simple_admin_dashboard')
            
            session.save()
            messages.success(request, f'✅ Training session created successfully for {session.training_page.get_region_display()}!')
            return redirect('simple_admin:create_training_session_with_program', program_id=program_id)
    else:
        form = SimpleTrainingSessionForm(user=user)
    
    return render(request, 'training_app/simple_admin/create_session.html', {
        'form': form,
        'program': program,
        'show_add_more': True
    })


@login_required
def manage_training_sessions(request):
    """
    Simple list of training sessions with edit/delete options
    Admin users only see sessions for their assigned regions
    """
    user = request.user
    
    # Filter sessions based on user permissions
    if user.user_type == 'master':
        sessions = TrainingSession.objects.select_related('training_page').order_by('-date', '-time_est')
    else:
        # Admin users only see sessions for their assigned regions
        assigned_pages = user.assigned_regions.all()
        sessions = TrainingSession.objects.filter(
            training_page__in=assigned_pages
        ).select_related('training_page').order_by('-date', '-time_est')
    
    # Add pagination
    paginator = Paginator(sessions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'training_app/simple_admin/manage_sessions.html', {
        'page_obj': page_obj,
        'sessions': page_obj
    })


@login_required
def edit_training_session(request, session_id):
    """
    Edit a training session
    Admin users can only edit sessions for their assigned regions
    """
    session = get_object_or_404(TrainingSession, id=session_id)
    user = request.user
    
    # Check permissions - admin users can only edit their assigned regions
    if user.user_type != 'master' and session.training_page not in user.assigned_regions.all():
        messages.error(request, '❌ You do not have permission to edit this session.')
        return redirect('simple_admin:manage_training_sessions')
    
    if request.method == 'POST':
        form = SimpleTrainingSessionForm(request.POST, instance=session, user=user)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Training session updated successfully!')
            return redirect('simple_admin:manage_training_sessions')
    else:
        form = SimpleTrainingSessionForm(instance=session, user=user)
    
    return render(request, 'training_app/simple_admin/edit_session.html', {
        'form': form,
        'session': session
    })


@login_required
def delete_training_session(request, session_id):
    """
    Delete a training session
    Admin users can only delete sessions for their assigned regions
    """
    session = get_object_or_404(TrainingSession, id=session_id)
    user = request.user
    
    # Check permissions - admin users can only delete their assigned regions
    if user.user_type != 'master' and session.training_page not in user.assigned_regions.all():
        messages.error(request, '❌ You do not have permission to delete this session.')
        return redirect('simple_admin:manage_training_sessions')
    
    if request.method == 'POST':
        session.delete()
        messages.success(request, '✅ Training session deleted successfully!')
        return redirect('simple_admin:simple_admin_dashboard')
    
    return render(request, 'training_app/simple_admin/confirm_delete.html', {
        'object': session,
        'object_type': 'training session',
        'back_url': 'simple_admin:simple_admin_dashboard'
    })


@login_required
def create_user(request):
    """
    Simple form to create a new user
    Only master users can create users
    """
    if request.user.user_type != 'master':
        messages.error(request, '❌ Only master users can create users.')
        return redirect('simple_admin:simple_admin_dashboard')
    
    if request.method == 'POST':
        form = SimpleUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Ensure username is set from email if not already set
            if not user.username and form.cleaned_data.get('email'):
                user.username = form.cleaned_data['email']
            
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Save the many-to-many relationship for assigned_regions
            form.save_m2m()
            
            messages.success(request, f'✅ User "{user.username}" created successfully!')
            return redirect('simple_admin:simple_admin_dashboard')
    else:
        form = SimpleUserForm()
    
    return render(request, 'training_app/simple_admin/create_user.html', {
        'form': form
    })


@login_required
def manage_users(request):
    """
    Simple list of all users
    Only master users can manage users
    """
    if request.user.user_type != 'master':
        messages.error(request, '❌ Only master users can manage users.')
        return redirect('simple_admin:simple_admin_dashboard')
    
    users = CustomUser.objects.all().order_by('-date_joined')
    master_count = CustomUser.objects.filter(user_type='master').count()
    
    return render(request, 'training_app/simple_admin/manage_users.html', {
        'users': users,
        'master_count': master_count
    })


@login_required
def manage_training_courses(request):
    """
    Manage training courses - view, edit, delete
    Only master users can manage training courses
    """
    if request.user.user_type != 'master':
        messages.error(request, '❌ Only master users can manage training courses.')
        return redirect('simple_admin:simple_admin_dashboard')
    
    courses = TrainingProgram.objects.all().order_by('-created_at')
    
    return render(request, 'training_app/simple_admin/manage_courses.html', {
        'courses': courses
    })


@login_required
def delete_training_course(request, course_id):
    """
    Delete a training course
    Only master users can delete training courses
    """
    if request.user.user_type != 'master':
        messages.error(request, '❌ Only master users can delete training courses.')
        return redirect('simple_admin:simple_admin_dashboard')
    
    try:
        course = TrainingProgram.objects.get(id=course_id)
    except TrainingProgram.DoesNotExist:
        messages.error(request, '❌ Training course not found.')
        return redirect('simple_admin:manage_training_courses')
    
    if request.method == 'POST':
        course_name = course.name
        
        # First, remove this program from all TrainingPage.current_program references
        # to avoid ProtectedError
        TrainingPage.objects.filter(current_program=course).update(current_program=None)
        
        course.delete()
        messages.success(request, f'✅ Training course "{course_name}" deleted successfully!')
        return redirect('simple_admin:manage_training_courses')
    
    return render(request, 'training_app/simple_admin/confirm_delete.html', {
        'object': course,
        'object_type': 'training course',
        'confirm_message': f'Are you sure you want to delete "{course.name}"?',
        'back_url': 'simple_admin:manage_training_courses'
    })


@login_required
def view_regions(request):
    """
    Simple view showing all regions and their current programs
    Only master users can view all regions
    """
    if request.user.user_type != 'master':
        messages.error(request, '❌ Only master users can view all regions.')
        return redirect('simple_admin:simple_admin_dashboard')
    
    regions = TrainingPage.objects.filter(is_active=True).select_related('current_program')
    
    return render(request, 'training_app/simple_admin/view_regions.html', {
        'regions': regions
    })


@login_required
def edit_training_course(request, course_id):
    """
    Edit an existing training course
    Only master users can edit training courses
    """
    if request.user.user_type != 'master':
        messages.error(request, '❌ Only master users can edit training courses.')
        return redirect('simple_admin:simple_admin_dashboard')
    
    try:
        course = TrainingProgram.objects.get(id=course_id)
    except TrainingProgram.DoesNotExist:
        messages.error(request, '❌ Training course not found.')
        return redirect('simple_admin:manage_training_courses')
    
    if request.method == 'POST':
        form = SimpleTrainingProgramForm(request.POST, request.FILES, instance=course, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Training course "{course.name}" updated successfully!')
            return redirect('simple_admin:manage_training_courses')
    else:
        form = SimpleTrainingProgramForm(instance=course, user=request.user)
    
    return render(request, 'training_app/simple_admin/edit_course.html', {
        'form': form,
        'course': course
    })


@login_required
def toggle_course_status(request, course_id):
    """
    Toggle the active status of a training course
    Only master users can toggle course status
    """
    if request.user.user_type != 'master':
        messages.error(request, '❌ Only master users can toggle course status.')
        return redirect('simple_admin:simple_admin_dashboard')
    
    try:
        course = TrainingProgram.objects.get(id=course_id)
    except TrainingProgram.DoesNotExist:
        messages.error(request, '❌ Training course not found.')
        return redirect('simple_admin:manage_training_courses')
    
    # Toggle the status
    course.is_active = not course.is_active
    course.save()
    
    status = "activated" if course.is_active else "deactivated"
    messages.success(request, f'✅ Training course "{course.name}" {status} successfully!')
    
    return redirect('simple_admin:manage_training_courses')


@login_required
def delete_user(request, user_id):
    """
    Delete a user with safety checks
    Only master users can delete users
    Cannot delete the last master user in the system
    """
    if request.user.user_type != 'master':
        messages.error(request, '❌ Only master users can delete users.')
        return redirect('simple_admin:simple_admin_dashboard')
    
    try:
        user_to_delete = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, '❌ User not found.')
        return redirect('simple_admin:manage_users')
    
    # Safety check: Cannot delete yourself
    if user_to_delete == request.user:
        messages.error(request, '❌ You cannot delete your own account.')
        return redirect('simple_admin:manage_users')
    
    # Safety check: Cannot delete the last master user
    if user_to_delete.user_type == 'master':
        master_count = CustomUser.objects.filter(user_type='master').count()
        if master_count <= 1:
            messages.error(request, '❌ Cannot delete the last master user. At least one master user must remain in the system.')
            return redirect('simple_admin:manage_users')
    
    if request.method == 'POST':
        username = user_to_delete.username
        user_to_delete.delete()
        messages.success(request, f'✅ User "{username}" deleted successfully!')
        return redirect('simple_admin:manage_users')
    
    return render(request, 'training_app/simple_admin/confirm_delete.html', {
        'object': user_to_delete,
        'object_type': 'user account',
        'back_url': 'simple_admin:manage_users'
    })


@login_required
def edit_user(request, user_id):
    """
    Edit a user account
    Only master users can edit users
    """
    if request.user.user_type != 'master':
        messages.error(request, '❌ Only master users can edit users.')
        return redirect('simple_admin:simple_admin_dashboard')
    
    try:
        user_to_edit = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, '❌ User not found.')
        return redirect('simple_admin:manage_users')
    
    if request.method == 'POST':
        # Update user fields (username cannot be changed)
        user_to_edit.first_name = request.POST.get('first_name')
        user_to_edit.last_name = request.POST.get('last_name')
        user_to_edit.email = request.POST.get('email')
        user_to_edit.user_type = request.POST.get('user_type')
        user_to_edit.is_active = request.POST.get('is_active') == 'on'
        
        # Handle password if provided
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password:
            if new_password != confirm_password:
                messages.error(request, '❌ Passwords do not match.')
                training_pages = TrainingPage.objects.filter(is_active=True)
                return render(request, 'training_app/simple_admin/edit_user.html', {
                    'user': user_to_edit,
                    'training_pages': training_pages
                })
            user_to_edit.set_password(new_password)
        
        # Handle assigned regions for admin users
        if user_to_edit.user_type == 'admin':
            # Get selected regions
            selected_regions = request.POST.getlist('assigned_regions')
            user_to_edit.assigned_regions.set(selected_regions)
        else:
            # Clear assigned regions for master users
            user_to_edit.assigned_regions.clear()
        
        try:
            user_to_edit.save()
            messages.success(request, f'✅ User "{user_to_edit.username}" updated successfully!')
            return redirect('simple_admin:manage_users')
        except Exception as e:
            messages.error(request, f'❌ Error updating user: {str(e)}')
    
    # Get all training pages for region selection
    training_pages = TrainingPage.objects.filter(is_active=True)
    
    return render(request, 'training_app/simple_admin/edit_user.html', {
        'user': user_to_edit,
        'training_pages': training_pages
    })
