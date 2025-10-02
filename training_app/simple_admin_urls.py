from django.urls import path
from . import simple_admin_views

app_name = 'simple_admin'

urlpatterns = [
    # Simple Admin Login
    path('simple-admin/login/', simple_admin_views.simple_admin_login, name='simple_admin_login'),
    
    # Simple Admin Dashboard
    path('simple-admin/', simple_admin_views.simple_admin_dashboard, name='simple_admin_dashboard'),
    
    # Training Program Management
    path('simple-admin/create-program/', simple_admin_views.create_training_program, name='create_training_program'),
    path('simple-admin/manage-courses/', simple_admin_views.manage_training_courses, name='manage_training_courses'),
    path('simple-admin/edit-course/<int:course_id>/', simple_admin_views.edit_training_course, name='edit_training_course'),
    path('simple-admin/toggle-course/<int:course_id>/', simple_admin_views.toggle_course_status, name='toggle_course_status'),
    path('simple-admin/delete-course/<int:course_id>/', simple_admin_views.delete_training_course, name='delete_training_course'),
    
    # Training Session Management
    path('simple-admin/create-session/', simple_admin_views.create_training_session, name='create_training_session'),
    path('simple-admin/create-session/program/<int:program_id>/', simple_admin_views.create_training_session_with_program, name='create_training_session_with_program'),
    path('simple-admin/manage-sessions/', simple_admin_views.manage_training_sessions, name='manage_training_sessions'),
    path('simple-admin/edit-session/<int:session_id>/', simple_admin_views.edit_training_session, name='edit_training_session'),
    path('simple-admin/delete-session/<int:session_id>/', simple_admin_views.delete_training_session, name='delete_training_session'),
    
    # User Management
    path('simple-admin/create-user/', simple_admin_views.create_user, name='create_user'),
    path('simple-admin/manage-users/', simple_admin_views.manage_users, name='manage_users'),
    path('simple-admin/edit-user/<int:user_id>/', simple_admin_views.edit_user, name='edit_user'),
    path('simple-admin/delete-user/<int:user_id>/', simple_admin_views.delete_user, name='delete_user'),
    
    # Region Management
    path('simple-admin/view-regions/', simple_admin_views.view_regions, name='view_regions'),
]
