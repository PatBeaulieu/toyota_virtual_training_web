#!/usr/bin/env python
"""
Script to create training programs and migrate existing data
Run this with: python create_training_program_migration.py
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toyota_training.settings')
django.setup()

from training_app.models import TrainingProgram, TrainingPage, TrainingSession


def create_default_training_program():
    """Create a default training program for existing data"""
    try:
        # Create the default PA465 training program
        default_program = TrainingProgram.objects.create(
            name='PA465',
            title='PA465 2026 bZ Virtual Training',
            description='Virtual training program for the 2026 Toyota bZ electric vehicle',
            is_active=True
        )
        print(f"✅ Created default training program: {default_program}")
        return default_program
    except Exception as e:
        print(f"❌ Error creating default training program: {e}")
        return None


def migrate_training_pages():
    """Update existing training pages to use the default program"""
    try:
        default_program = TrainingProgram.objects.first()
        if not default_program:
            print("❌ No default training program found. Please create one first.")
            return False
        
        # Update all existing training pages to use the default program
        updated_pages = 0
        for page in TrainingPage.objects.all():
            page.current_program = default_program
            page.save()
            updated_pages += 1
            print(f"✅ Updated {page.region} page to use {default_program.name}")
        
        print(f"✅ Successfully updated {updated_pages} training pages")
        return True
    except Exception as e:
        print(f"❌ Error migrating training pages: {e}")
        return False


def create_sample_training_programs():
    """Create some sample training programs for testing"""
    try:
        programs_data = [
            {
                'name': 'PA466',
                'title': 'PA466 New Grand Highlander Virtual Training',
                'description': 'Virtual training program for the new Toyota Grand Highlander',
            },
            {
                'name': 'PA467',
                'title': 'PA467 Hybrid Technology Training',
                'description': 'Advanced training for Toyota hybrid technology systems',
            },
        ]
        
        for program_data in programs_data:
            program, created = TrainingProgram.objects.get_or_create(
                name=program_data['name'],
                defaults=program_data
            )
            if created:
                print(f"✅ Created training program: {program}")
            else:
                print(f"ℹ️  Training program already exists: {program}")
        
        return True
    except Exception as e:
        print(f"❌ Error creating sample training programs: {e}")
        return False


def main():
    print("🚀 Creating Training Program Migration...")
    print()
    
    # Step 1: Create default training program
    default_program = create_default_training_program()
    if not default_program:
        print("❌ Failed to create default training program. Exiting.")
        return
    
    print()
    
    # Step 2: Migrate existing training pages
    if migrate_training_pages():
        print("✅ Training pages migration completed successfully!")
    else:
        print("❌ Training pages migration failed.")
        return
    
    print()
    
    # Step 3: Create sample training programs
    create_sample_training_programs()
    
    print()
    print("🎉 Training program migration completed!")
    print()
    print("📋 What was created:")
    print("   • Default PA465 training program")
    print("   • Updated all regional pages to use PA465 program")
    print("   • Sample PA466 and PA467 training programs")
    print()
    print("🔐 You can now:")
    print("   1. Go to Django Admin: http://127.0.0.1:8000/django-admin/")
    print("   2. Create new training programs")
    print("   3. Assign different programs to different regions")
    print("   4. Upload images for each training program")


if __name__ == '__main__':
    main()


