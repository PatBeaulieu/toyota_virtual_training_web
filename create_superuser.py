#!/usr/bin/env python
"""
Create a MASTER superuser for Railway deployment
Set these environment variables in Railway:
- DJANGO_SUPERUSER_USERNAME
- DJANGO_SUPERUSER_EMAIL
- DJANGO_SUPERUSER_PASSWORD
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toyota_training.settings_production')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'changeme123')

if not User.objects.filter(username=username).exists():
    # Create superuser with MASTER user_type for full permissions
    user = User.objects.create_superuser(
        username=username, 
        email=email, 
        password=password
    )
    user.user_type = 'master'  # Set as Master user for full access
    user.save()
    print(f"✅ Master Superuser '{username}' created successfully!")
    print(f"   Email: {email}")
    print(f"   User Type: Master (full access)")
    print(f"\n⚠️  Change the password after first login!")
else:
    # Update existing user to master if not already
    user = User.objects.get(username=username)
    if user.user_type != 'master':
        user.user_type = 'master'
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print(f"✅ Updated '{username}' to Master user with full permissions!")
    else:
        print(f"ℹ️  Master Superuser '{username}' already exists")

