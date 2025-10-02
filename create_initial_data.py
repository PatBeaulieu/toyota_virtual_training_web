#!/usr/bin/env python
"""
Script to create initial data for the Toyota Training system
Run this with: python create_initial_data.py
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toyota_training.settings')
django.setup()

from training_app.models import CustomUser, TrainingPage, TrainingSession
from datetime import date, time


def create_master_user():
    """Create the master user"""
    try:
        master_user = CustomUser.objects.create_user(
            username='master',
            email='master@rtmtoyota.ca',
            password='Toyota2025!',  # You can change this password later
            user_type='master',
            first_name='Master',
            last_name='User',
            is_staff=True,
            is_superuser=True
        )
        print(f"✅ Created master user: {master_user.username}")
        return master_user
    except Exception as e:
        print(f"❌ Error creating master user: {e}")


def create_training_pages():
    """Create the 5 regional training pages"""
    regions = [
        ('quebec', 'Quebec'),
        ('central', 'Central'),
        ('pacific', 'Pacific'),
        ('prairie', 'Prairie'),
        ('atlantic', 'Atlantic'),
    ]
    
    created_pages = []
    for region_key, region_name in regions:
        try:
            page, created = TrainingPage.objects.get_or_create(
                region=region_key,
                defaults={
                    'title': f'PA465 2026 bZ Virtual Training - {region_name}',
                    'timezone': 'America/Toronto',
                    'is_active': True
                }
            )
            if created:
                print(f"✅ Created training page: {page.get_region_display()}")
            else:
                print(f"ℹ️  Training page already exists: {page.get_region_display()}")
            created_pages.append(page)
        except Exception as e:
            print(f"❌ Error creating training page for {region_name}: {e}")
    
    return created_pages


def create_sample_sessions():
    """Create some sample training sessions"""
    try:
        # Get Quebec page for sample sessions
        quebec_page = TrainingPage.objects.get(region='quebec')
        
        # Sample sessions (you can modify these dates)
        sample_sessions = [
            {'date': date(2025, 1, 15), 'time': time(10, 0)},
            {'date': date(2025, 1, 15), 'time': time(14, 0)},
            {'date': date(2025, 1, 16), 'time': time(10, 0)},
            {'date': date(2025, 1, 16), 'time': time(14, 0)},
        ]
        
        for session_data in sample_sessions:
            session, created = TrainingSession.objects.get_or_create(
                training_page=quebec_page,
                date=session_data['date'],
                time_est=session_data['time'],
                defaults={
                    'teams_link': 'https://teams.microsoft.com/l/meetup-join/example',
                    'teams_link_valid': False
                }
            )
            if created:
                print(f"✅ Created sample session: {session}")
        
        print("✅ Created sample training sessions")
    except Exception as e:
        print(f"❌ Error creating sample sessions: {e}")


def main():
    print("🚀 Creating initial data for Toyota Training System...")
    print()
    
    # Create master user
    create_master_user()
    print()
    
    # Create training pages
    pages = create_training_pages()
    print()
    
    # Create sample sessions
    create_sample_sessions()
    print()
    
    print("🎉 Initial data creation completed!")
    print()
    print("📋 What was created:")
    print("   • Master user: username='master', password='Toyota2025!'")
    print("   • 5 regional training pages (Quebec, Central, Pacific, Prairie, Atlantic)")
    print("   • Sample training sessions for Quebec")
    print()
    print("🔐 You can now:")
    print("   1. Run: python manage.py runserver")
    print("   2. Go to: http://127.0.0.1:8000/admin/")
    print("   3. Login with: master / Toyota2025!")
    print("   4. Start adding training sessions!")


if __name__ == '__main__':
    main()


