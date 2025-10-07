from django import forms
from datetime import time
from .models import TrainingProgram, TrainingSession, TrainingPage, CustomUser
from .validators import validate_password_strength, validate_username, validate_email_domain, sanitize_html
import logging

logger = logging.getLogger(__name__)


class RegionCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    """
    Custom widget that shows only the region name for TrainingPage objects
    """
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        # Get the TrainingPage object and use just the region name
        if value:
            try:
                # Extract the actual value from ModelChoiceIteratorValue if needed
                actual_value = value.value if hasattr(value, 'value') else value
                training_page = TrainingPage.objects.get(pk=actual_value)
                option['label'] = training_page.get_region_display()
            except (TrainingPage.DoesNotExist, AttributeError):
                pass
        return option


class TimeSelectWidget(forms.Select):
    """
    Custom time widget with 30-minute intervals
    """
    def __init__(self, attrs=None):
        choices = []
        # Business hours: 8:00 AM to 5:00 PM (8:00 to 17:00)
        for hour in range(8, 17):  # 8 AM to 4 PM (inclusive), then add 5:00 PM separately
            for minute in [0, 30]:
                time_obj = time(hour, minute)
                time_str = time_obj.strftime('%I:%M %p')
                choices.append((time_obj.strftime('%H:%M'), time_str))
        
        # Add 5:00 PM as the final choice
        time_5pm = time(17, 0)
        choices.append((time_5pm.strftime('%H:%M'), time_5pm.strftime('%I:%M %p')))
        
        # Add empty choice at the beginning for better UX
        choices.insert(0, ('', 'Select a time'))
        
        super().__init__(attrs, choices=choices)
    
    def format_value(self, value):
        """
        Format the time value to match our choice format (HH:MM)
        """
        if value is None:
            return ''
        
        if hasattr(value, 'strftime'):
            # Format as HH:MM to match our choices
            return value.strftime('%H:%M')
        elif isinstance(value, str):
            # If it's already a string, try to parse it
            try:
                from datetime import datetime
                if len(value) == 5:  # Already HH:MM format
                    return value
                elif len(value) == 8:  # HH:MM:SS format
                    parsed_time = datetime.strptime(value, '%H:%M:%S').time()
                    return parsed_time.strftime('%H:%M')
                else:
                    return value
            except (ValueError, TypeError):
                return value
        
        return str(value)
    
    def value_from_datadict(self, data, files, name):
        """
        Override to handle initial values properly
        """
        value = super().value_from_datadict(data, files, name)
        # If no value from form data, return None so Django can use the initial value
        return value if value else None
    
    def render(self, name, value, attrs=None, renderer=None):
        """
        Override render to ensure the correct option is selected
        """
        if value is None:
            value = ''
        
        # Format the value to match our choice format
        formatted_value = self.format_value(value)
        
        # Create the select element
        output = []
        output.append(f'<select name="{name}" class="form-control" title="Select training time from dropdown" required id="id_{name}">')
        
        # Render each option
        for choice_value, choice_label in self.choices:
            selected = 'selected' if str(choice_value) == str(formatted_value) else ''
            output.append(f'  <option value="{choice_value}" {selected}>{choice_label}</option>')
        
        output.append('</select>')
        
        return '\n'.join(output)


class TimeInputWidget(forms.TimeInput):
    """
    Custom time input widget that properly formats time values for HTML5 time inputs
    """
    def format_value(self, value):
        """
        Format the time value for HTML5 time input (HH:MM format)
        """
        if value is None:
            return ''
        
        if hasattr(value, 'strftime'):
            # If it's a time object, format it as HH:MM
            return value.strftime('%H:%M')
        elif isinstance(value, str):
            # If it's already a string, try to parse and format it
            try:
                from datetime import datetime
                parsed_time = datetime.strptime(value, '%H:%M:%S').time()
                return parsed_time.strftime('%H:%M')
            except (ValueError, TypeError):
                return value
        
        return str(value)


class SimpleTrainingProgramForm(forms.ModelForm):
    """
    Simple form for creating training programs
    """
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # No restrictions needed - all users can create programs
    
    class Meta:
        model = TrainingProgram
        fields = ['name', 'title', 'title_fr', 'description', 'main_image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., PA466, PA467'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., PA466 New Grand Highlander Virtual Training'
            }),
            'title_fr': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ex.: Formation virtuelle PA466 Nouveau Grand Highlander'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description of the training program'
            }),
            'main_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }


class SimpleTrainingSessionForm(forms.ModelForm):
    """
    Simple form for creating training sessions
    Master users can select any region, Admin users can only select from their assigned regions
    """
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # All users can select from all available training programs
        active_programs = TrainingProgram.objects.filter(is_active=True)
        self.fields['training_program'].queryset = active_programs
        
        # Add help text for Teams link field
        self.fields['teams_link'].help_text = "Paste your complete Microsoft Teams meeting link. Long Teams URLs (up to 500 characters) are now supported and will open properly in the Teams app or browser."
        
        # Handle time field initial value for editing
        if self.instance and self.instance.pk and self.instance.time_est:
            # Format the time for the widget
            time_str = self.instance.time_est.strftime('%H:%M')
            self.initial['time_est'] = time_str
        
        # Auto-select and make read-only if only one active program is available
        if active_programs.count() == 1:
            self.initial['training_program'] = active_programs.first()
            self.fields['training_program'].widget.attrs.update({
                'readonly': True,
                'class': 'form-control readonly-program'
            })
            self.fields['training_program'].help_text = ""  # No help text for single program
        
        # Add region selection field for master users
        if user and user.user_type == 'master':
            self.fields['training_page'] = forms.ModelChoiceField(
                queryset=TrainingPage.objects.filter(is_active=True),
                widget=forms.Select(attrs={
                    'class': 'form-control'
                }),
                required=True,
                help_text="Select which region this training session is for"
            )
        elif user and user.user_type == 'admin':
            # Admin users can only select from their assigned regions
            assigned_regions = user.assigned_regions.filter(is_active=True)
            
            if assigned_regions.count() == 1:
                # If only one region assigned, make it read-only
                self.fields['training_page'] = forms.ModelChoiceField(
                    queryset=assigned_regions,
                    widget=forms.Select(attrs={
                        'class': 'form-control readonly-region',
                        'readonly': True
                    }),
                    required=True,
                    help_text=""  # No help text for single region
                )
                # Set the initial value to the single assigned region
                self.initial['training_page'] = assigned_regions.first()
            else:
                # Multiple regions assigned, allow selection
                self.fields['training_page'] = forms.ModelChoiceField(
                    queryset=assigned_regions,
                    widget=forms.Select(attrs={
                        'class': 'form-control'
                    }),
                    required=True,
                    help_text="Select which region this training session is for"
                )
    
    class Meta:
        model = TrainingSession
        fields = ['training_program', 'training_page', 'date', 'time_est', 'teams_link']
        widgets = {
            'training_program': forms.Select(attrs={
                'class': 'form-control'
            }),
            'training_page': forms.Select(attrs={
                'class': 'form-control'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'time_est': TimeSelectWidget(attrs={
                'class': 'form-control',
                'title': 'Select training time from dropdown'
            }),
            'teams_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://teams.microsoft.com/l/meetup-join/...',
                'title': 'Paste your Microsoft Teams meeting link here',
                'maxlength': '500'
            })
        }


class SimpleUserForm(forms.ModelForm):
    """
    Simple form for creating users
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        }),
        validators=[validate_password_strength],
        help_text='Secure password for the user (minimum 12 characters)'
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        }),
        label='Confirm Password'
    )
    
    assigned_regions = forms.ModelMultipleChoiceField(
        queryset=TrainingPage.objects.all(),
        widget=RegionCheckboxSelectMultiple,
        required=False,
        help_text="Select which training locations this admin user can manage (only applies to admin users)",
        label="Assigned Training Locations"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        user_type = cleaned_data.get('user_type')
        assigned_regions = cleaned_data.get('assigned_regions')
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        # Validate password confirmation
        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Passwords do not match.")
        elif password and not confirm_password:
            raise forms.ValidationError("Please confirm your password.")
        
        # If email is provided, use it as username
        if email and not self.instance.pk:  # Only for new users
            cleaned_data['username'] = email
        elif not self.instance.pk and not cleaned_data.get('username'):
            # If no email and no username, this is an error
            raise forms.ValidationError("Username is required.")
        
        # Validate that admin users have assigned regions
        if user_type == 'admin' and not assigned_regions:
            raise forms.ValidationError("Admin users must be assigned to at least one training location.")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Ensure username is set
        if not user.username and self.cleaned_data.get('email'):
            user.username = self.cleaned_data['email']
        
        if commit:
            user.save()
            self.save_m2m()
        
        return user
    
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'user_type', 'assigned_regions', 'password', 'confirm_password']
        exclude = ['username']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email address (will be used as username)'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name'
            }),
            'user_type': forms.Select(attrs={
                'class': 'form-control'
            })
        }


