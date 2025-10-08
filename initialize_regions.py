#!/usr/bin/env python
"""
Initialize the 5 regional Training Pages if they don't exist
This should run automatically on first deployment
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toyota_training.settings_production')
django.setup()

from training_app.models import TrainingPage

# Define the 5 regions with their timezones
REGIONS = [
    {
        'region': 'quebec',
        'timezone': 'America/Toronto',  # EST/EDT
    },
    {
        'region': 'central',
        'timezone': 'America/Toronto',  # EST/EDT
    },
    {
        'region': 'pacific',
        'timezone': 'America/Vancouver',  # PST/PDT
    },
    {
        'region': 'prairie',
        'timezone': 'America/Regina',  # CST (no DST in Saskatchewan)
    },
    {
        'region': 'atlantic',
        'timezone': 'America/Halifax',  # AST/ADT
    },
]

print("🔧 Initializing regional training pages...")

created_count = 0
existing_count = 0

for region_data in REGIONS:
    region_code = region_data['region']
    
    # Check if region already exists
    if TrainingPage.objects.filter(region=region_code).exists():
        existing_count += 1
        print(f"   ℹ️  {region_code.capitalize()} region already exists")
    else:
        # Create the training page
        training_page = TrainingPage.objects.create(
            region=region_code,
            timezone=region_data['timezone'],
            is_active=True
        )
        created_count += 1
        print(f"   ✅ Created {region_code.capitalize()} region (timezone: {region_data['timezone']})")

print(f"\n📊 Summary:")
print(f"   ✅ Created: {created_count} regions")
print(f"   ℹ️  Already existed: {existing_count} regions")
print(f"   📍 Total regions: {TrainingPage.objects.count()}")

if created_count > 0:
    print(f"\n✅ Regional training pages initialized successfully!")
    print(f"   Master users can now create sessions for all {TrainingPage.objects.count()} regions")
else:
    print(f"\n✅ All regional training pages already exist")

