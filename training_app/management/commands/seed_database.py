"""
Management command to seed the database with initial data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from training_app.models import TrainingPage, TrainingProgram

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding database with initial data...')
        
        # Create master user if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@rtmtoyota.ca',
                password='admin123',
                user_type='master',
                first_name='Master',
                last_name='Admin'
            )
            self.stdout.write(self.style.SUCCESS('✅ Created master admin user (admin/admin123)'))
        else:
            self.stdout.write('ℹ️ Master admin user already exists')
        
        # Create training pages if they don't exist
        regions = [
            ('quebec', 'Quebec', 'America/Toronto'),
            ('central', 'Central', 'America/Toronto'),
            ('pacific', 'Pacific', 'America/Vancouver'),
            ('prairie', 'Prairie', 'America/Regina'),
            ('atlantic', 'Atlantic', 'America/Halifax'),
        ]
        
        for region_code, region_name, timezone in regions:
            training_page, created = TrainingPage.objects.get_or_create(
                region=region_code,
                defaults={
                    'timezone': timezone,
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Created {region_name} training page'))
            else:
                self.stdout.write(f'ℹ️ {region_name} training page already exists')
        
        # Create a sample training program if none exist
        if not TrainingProgram.objects.exists():
            sample_program = TrainingProgram.objects.create(
                name='PA466',
                title='PA466 New Grand Highlander Virtual Training',
                description='Virtual training program for the new Toyota Grand Highlander featuring advanced safety systems and hybrid technology.',
                is_active=True
            )
            
            # Assign this program to all training pages
            TrainingPage.objects.update(current_program=sample_program)
            
            self.stdout.write(self.style.SUCCESS('✅ Created sample training program (PA466 Grand Highlander)'))
            self.stdout.write(self.style.SUCCESS('✅ Assigned program to all training pages'))
        else:
            self.stdout.write('ℹ️ Training programs already exist')
        
        self.stdout.write(self.style.SUCCESS('🎉 Database seeding completed!'))
        self.stdout.write('📝 Login credentials: admin / admin123')
