#!/usr/bin/env python3
"""
Create Admin User for Testing
"""

import os
import sys
import django

# Setup Django
sys.path.append('/Users/patb/code/toyota_virtual_training')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toyota_training.settings')
django.setup()

from training_app.models import CustomUser, TrainingPage, TrainingProgram

def create_admin_user():
    print("🔐 Creating Admin User...")
    
    # Create or get Quebec page
    quebec_page, created = TrainingPage.objects.get_or_create(
        region='quebec',
        defaults={
            'timezone': 'America/Toronto'
        }
    )
    
    # Get or create a sample training program
    try:
        program = TrainingProgram.objects.filter(name='PA466').first()
        if not program:
            program = TrainingProgram.objects.create(
                name='PA466',
                title='PA466 New Grand Highlander Virtual Training',
                description='Virtual training for the new Grand Highlander',
                is_active=True
            )
    except:
        program = TrainingProgram.objects.first()
    
    # Assign program to Quebec page
    quebec_page.current_program = program
    quebec_page.save()
    
    # Create admin user
    admin_user, created = CustomUser.objects.get_or_create(
        username='quebec.admin@rtmtoyota.ca',
        defaults={
            'email': 'quebec.admin@rtmtoyota.ca',
            'first_name': 'Quebec',
            'last_name': 'Admin',
            'user_type': 'admin',
            'is_staff': True,
            'is_active': True
        }
    )
    
    if created:
        admin_user.set_password('Toyota2025!')
        admin_user.assigned_regions.add(quebec_page)
        admin_user.save()
        print("✅ Admin user created successfully!")
        print(f"   - Username: quebec.admin@rtmtoyota.ca")
        print(f"   - Password: Toyota2025!")
        print(f"   - Assigned to: Quebec region")
    else:
        print("✅ Admin user already exists!")
    
    print("\n🎯 Test the improved workflow:")
    print("1. Login at: http://127.0.0.1:8000/simple-admin/login/")
    print("2. Create a new training program")
    print("3. Notice immediate redirect to add training sessions")
    print("4. Add multiple sessions seamlessly")

if __name__ == '__main__':
    create_admin_user()
