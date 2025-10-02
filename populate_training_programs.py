#!/usr/bin/env python3
"""
Populate Training Program for Existing Sessions
=============================================

This script populates the new training_program field for existing TrainingSession objects
by using the current_program from their associated TrainingPage.
"""

import os
import sys
import django

# Setup Django
sys.path.append('/Users/patb/code/toyota_virtual_training')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toyota_training.settings')
django.setup()

from training_app.models import TrainingSession, TrainingProgram

def populate_training_programs():
    print("🔄 Populating Training Programs for Existing Sessions...")
    
    # Get all sessions without training_program
    sessions_without_program = TrainingSession.objects.filter(training_program__isnull=True)
    print(f"Found {sessions_without_program.count()} sessions without training program")
    
    updated_count = 0
    
    for session in sessions_without_program:
        # Get the training page's current program
        if session.training_page.current_program:
            session.training_program = session.training_page.current_program
            session.save()
            updated_count += 1
            print(f"✅ Updated session {session.id} with program: {session.training_page.current_program.title}")
        else:
            # If no current program, assign the first available program
            first_program = TrainingProgram.objects.first()
            if first_program:
                session.training_program = first_program
                session.save()
                updated_count += 1
                print(f"⚠️  Session {session.id} had no program, assigned: {first_program.title}")
            else:
                print(f"❌ No training programs available for session {session.id}")
    
    print(f"\n🎉 Successfully updated {updated_count} sessions!")
    
    # Show summary
    print("\n📊 Summary:")
    all_sessions = TrainingSession.objects.all()
    sessions_with_program = TrainingSession.objects.filter(training_program__isnull=False)
    sessions_without_program = TrainingSession.objects.filter(training_program__isnull=True)
    
    print(f"   • Total sessions: {all_sessions.count()}")
    print(f"   • Sessions with program: {sessions_with_program.count()}")
    print(f"   • Sessions without program: {sessions_without_program.count()}")

if __name__ == '__main__':
    populate_training_programs()

