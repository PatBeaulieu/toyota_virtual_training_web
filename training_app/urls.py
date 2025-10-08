from django.urls import path
from . import views

app_name = 'training_app'

urlpatterns = [
    # Path-based routing (e.g., rtmtoyota.ca/quebec/)
    # Subdomain routing (e.g., quebec.rtmtoyota.ca/) is handled in home_redirect view
    path('<str:region>/', views.training_page_view, name='training_page'),
    
    # AJAX endpoints
    path('api/test-teams-link/<int:session_id>/', views.test_teams_link, name='test_teams_link'),
    path('api/session-status/<int:session_id>/', views.get_session_status, name='get_session_status'),
]
