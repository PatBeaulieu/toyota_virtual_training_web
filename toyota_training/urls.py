"""
URL configuration for toyota_training project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from training_app import views
from training_app.health_checks import health_check, detailed_health_check, readiness_check, liveness_check

urlpatterns = [
    # Django Admin
    path('django-admin/', admin.site.urls),
    
    # Simple Admin Interface
    path('', include('training_app.simple_admin_urls')),
    
    # Custom Admin Authentication
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/logout/', auth_views.LogoutView.as_view(next_page='/'), name='admin_logout'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Home redirect (must be before training_app URLs)
    path('', views.home_redirect, name='home'),
    
    # Training app URLs (regional pages)
    path('', include('training_app.urls')),
    
    # Health check endpoints
    path('health/', health_check, name='health_check'),
    path('health/detailed/', detailed_health_check, name='detailed_health_check'),
    path('health/ready/', readiness_check, name='readiness_check'),
    path('health/live/', liveness_check, name='liveness_check'),
]

# Serve media files in development and production
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
