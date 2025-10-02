from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, TrainingProgram, TrainingPage, TrainingSession


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin interface for our custom user model
    """
    list_display = ('username', 'email', 'user_type', 'first_name', 'last_name', 'is_active')
    list_filter = ('user_type', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Toyota Training Settings', {
            'fields': ('user_type',)
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Toyota Training Settings', {
            'fields': ('user_type',)
        }),
    )


@admin.register(TrainingProgram)
class TrainingProgramAdmin(admin.ModelAdmin):
    """
    Admin interface for training programs
    """
    list_display = ('name', 'title', 'is_active', 'created_at', 'image_preview')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'title', 'description')
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    
    fieldsets = (
        ('Program Information', {
            'fields': ('name', 'title', 'description', 'main_image', 'image_preview')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        """Show a preview of the training program image"""
        if obj.main_image:
            return format_html('<img src="{}" width="200" height="auto" style="border-radius: 5px;" />', obj.main_image.url)
        return "No image uploaded"
    image_preview.short_description = "Image Preview"


@admin.register(TrainingPage)
class TrainingPageAdmin(admin.ModelAdmin):
    """
    Admin interface for training pages
    """
    list_display = ('region', 'current_program', 'is_active', 'domain_link', 'session_count', 'updated_at')
    list_filter = ('is_active', 'region', 'current_program')
    search_fields = ('region', 'current_program__name', 'current_program__title')
    readonly_fields = ('created_at', 'updated_at', 'domain_link')
    
    fieldsets = (
        ('Regional Settings', {
            'fields': ('region', 'timezone', 'is_active')
        }),
        ('Current Training Program', {
            'fields': ('current_program',)
        }),
        ('System Information', {
            'fields': ('domain_link', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def domain_link(self, obj):
        """Show the subdomain for this region"""
        if obj.pk:
            domain = f"https://{obj.get_domain()}"
            return format_html('<a href="{}" target="_blank">{}</a>', domain, domain)
        return "Save to see domain"
    domain_link.short_description = "Domain"
    
    def session_count(self, obj):
        """Show number of training sessions"""
        if obj.pk:
            count = obj.sessions.count()
            return f"{count} sessions"
        return "0 sessions"
    session_count.short_description = "Training Sessions"


@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    """
    Admin interface for training sessions
    """
    list_display = ('training_page', 'date', 'time_est', 'teams_link_status', 'updated_at')
    list_filter = ('training_page', 'date', 'teams_link_valid')
    search_fields = ('training_page__region', 'teams_link')
    date_hierarchy = 'date'
    ordering = ('date', 'time_est')
    
    fieldsets = (
        ('Session Details', {
            'fields': ('training_page', 'date', 'time_est', 'teams_link')
        }),
        ('Link Validation', {
            'fields': ('teams_link_valid', 'teams_link_last_tested'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('teams_link_valid', 'teams_link_last_tested', 'created_at', 'updated_at')
    
    def teams_link_status(self, obj):
        """Show Teams link validation status with icon"""
        if obj.teams_link_valid:
            return format_html('<span style="color: green;">✅ Valid</span>')
        else:
            return format_html('<span style="color: red;">❌ Invalid/Missing</span>')
    teams_link_status.short_description = "Teams Link Status"
    
    def get_queryset(self, request):
        """Optimize queries by selecting related objects"""
        return super().get_queryset(request).select_related('training_page')


# Customize admin site header and title
admin.site.site_header = "Toyota Training System Admin"
admin.site.site_title = "Toyota Training Admin"
admin.site.index_title = "Welcome to Toyota Training System"