#!/usr/bin/env python
"""
Create an admin user for testing the restricted interface
"""

import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toyota_training.settings')
django.setup()

from training_app.models import CustomUser, TrainingPage

def create_admin_user():
    print("🔐 Creating Admin User...")
    
    # Get the Quebec training page to assign to the admin
    quebec_page = TrainingPage.objects.get(region='quebec')
    
    # Create admin user
    admin_user, created = CustomUser.objects.get_or_create(
        username='admin_quebec',
        defaults={
            'email': 'admin.quebec@toyota.com',
            'first_name': 'Quebec',
            'last_name': 'Admin',
            'user_type': 'admin',
            'is_active': True,
        }
    )
    
    if created:
        admin_user.set_password('Admin2025!')
        admin_user.save()
        print(f"✅ Created admin user: {admin_user.username}")
    else:
        print(f"🔄 Admin user already exists: {admin_user.username}")
    
    # Assign Quebec region to admin user
    admin_user.assigned_regions.add(quebec_page)
    print(f"✅ Assigned Quebec region to {admin_user.username}")
    
    print("\n🎉 Admin User Setup Complete!")
    print("\n📋 Login Credentials:")
    print(f"   Username: {admin_user.username}")
    print(f"   Password: Admin2025!")
    print(f"   User Type: {admin_user.user_type}")
    print(f"   Assigned Regions: {', '.join([page.get_region_display() for page in admin_user.assigned_regions.all()])}")
    
    print("\n🔗 Access URLs:")
    print("   • Simple Admin: http://127.0.0.1:8000/simple-admin/login/")
    print("   • Advanced Admin: http://127.0.0.1:8000/django-admin/")
    
    print("\n🎯 What Admin Users Can Do:")
    print("   ✅ Add Training Sessions")
    print("   ✅ Manage Training Sessions")
    print("   ❌ Create Training Programs")
    print("   ❌ Create Users")
    print("   ❌ Assign Programs to Regions")
    print("   ❌ View All Regions")

if __name__ == '__main__':
    create_admin_user()


