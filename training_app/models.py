from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator
from .validators import validate_teams_link, validate_region, validate_timezone, validate_training_session_date, validate_training_session_time
import logging

logger = logging.getLogger(__name__)


class CustomUser(AbstractUser):
    """
    Custom user model with different user types:
    - Master: Can edit all training pages
    - Admin: Can edit only assigned training pages
    """
    USER_TYPE_CHOICES = [
        ('master', 'Master User'),
        ('admin', 'Admin User'),
    ]
    
    user_type = models.CharField(
        max_length=10, 
        choices=USER_TYPE_CHOICES,
        default='admin',
        help_text="Master users can edit all pages, Admin users can only edit assigned pages"
    )
    
    assigned_regions = models.ManyToManyField(
        'TrainingPage',
        blank=True,
        help_text="Training pages this admin user can manage (only applies to admin users)"
    )
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


class TrainingProgram(models.Model):
    """
    Represents a training program (e.g., PA465 2026 bZ, PA466 Grand Highlander)
    """
    name = models.CharField(
        max_length=100,
        help_text="Short name for the program (e.g., PA465, PA466)"
    )
    
    title = models.CharField(
        max_length=200,
        help_text="Full title of the training program (e.g., PA465 2026 bZ Virtual Training)"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Description of the training program"
    )
    
    main_image = models.ImageField(
        upload_to='training_programs/',
        help_text="Main image for this training program"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this training program is currently active"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.title}"


class TrainingPage(models.Model):
    """
    Represents one of the 5 regional training pages
    """
    REGION_CHOICES = [
        ('quebec', 'Quebec'),
        ('central', 'Central'),
        ('pacific', 'Pacific'),
        ('prairie', 'Prairie'),
        ('atlantic', 'Atlantic'),
    ]
    
    region = models.CharField(
        max_length=20, 
        choices=REGION_CHOICES, 
        unique=True,
        validators=[validate_region],
        help_text="The region this training page is for"
    )
    
    current_program = models.ForeignKey(
        TrainingProgram,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="The currently active training program for this region"
    )
    
    timezone = models.CharField(
        max_length=50, 
        default='America/Toronto',
        validators=[validate_timezone],
        help_text="Timezone for this region (EST/EDT)"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this training page is active"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['region']
    
    def __str__(self):
        if self.current_program:
            return f"{self.get_region_display()} - {self.current_program.title}"
        else:
            return f"{self.get_region_display()}"
    
    def get_domain(self):
        """Returns the subdomain for this region"""
        return f"{self.region}.rtmtoyota.ca"
    
    @property
    def title(self):
        """Get the title from the current program or show 'Virtual Training' if no sessions"""
        if self.current_program:
            # Check if there are any training sessions
            if self.sessions.exists():
                return self.current_program.title
            else:
                return "Virtual Training"
        else:
            return "Virtual Training"
    
    @property
    def main_image(self):
        """Get the main image from the current program"""
        return self.current_program.main_image


class TrainingSession(models.Model):
    """
    Individual training sessions for each region
    """
    training_page = models.ForeignKey(
        TrainingPage, 
        on_delete=models.CASCADE, 
        related_name='sessions',
        help_text="Which training page this session belongs to"
    )
    
    training_program = models.ForeignKey(
        TrainingProgram,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Which training program this session is for"
    )
    
    date = models.DateField(
        validators=[validate_training_session_date],
        help_text="Date of the training session"
    )
    
    time_est = models.TimeField(
        validators=[validate_training_session_time],
        help_text="Time of the training session (Eastern Time)"
    )
    
    teams_link = models.URLField(
        blank=True,
        max_length=500,
        validators=[validate_teams_link],
        help_text="Microsoft Teams meeting link"
    )
    
    teams_link_valid = models.BooleanField(
        default=False,
        help_text="Whether the Teams link is working"
    )
    
    teams_link_last_tested = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When the Teams link was last tested"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date', 'time_est']
        unique_together = ['training_page', 'date', 'time_est']
    
    def __str__(self):
        return f"{self.training_page.get_region_display()} - {self.date} at {self.time_est}"
    
    def get_datetime_est(self):
        """Returns the full datetime in Eastern time"""
        from datetime import datetime
        return datetime.combine(self.date, self.time_est)