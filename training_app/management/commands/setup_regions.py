"""
Django management command to set up all 5 regional training pages
Usage: python manage.py setup_regions
"""
from django.core.management.base import BaseCommand
from training_app.models import TrainingPage


class Command(BaseCommand):
    help = 'Initialize or verify all 5 regional training pages'

    def handle(self, *args, **options):
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

        self.stdout.write(self.style.WARNING('🔧 Setting up regional training pages...'))
        
        created_count = 0
        existing_count = 0
        
        for region_data in REGIONS:
            region_code = region_data['region']
            
            # Check if region already exists
            page, created = TrainingPage.objects.get_or_create(
                region=region_code,
                defaults={
                    'timezone': region_data['timezone'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'   ✅ Created {region_code.capitalize()} region'))
            else:
                existing_count += 1
                # Update timezone if it's different
                if page.timezone != region_data['timezone']:
                    page.timezone = region_data['timezone']
                    page.save()
                    self.stdout.write(self.style.WARNING(f'   🔄 Updated {region_code.capitalize()} timezone'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'   ℹ️  {region_code.capitalize()} region already exists'))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'📊 Summary:'))
        self.stdout.write(self.style.SUCCESS(f'   ✅ Created: {created_count} regions'))
        self.stdout.write(self.style.SUCCESS(f'   ℹ️  Already existed: {existing_count} regions'))
        self.stdout.write(self.style.SUCCESS(f'   📍 Total regions: {TrainingPage.objects.count()}'))
        
        if created_count > 0:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('✅ Regional training pages set up successfully!'))
        else:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('✅ All regional training pages already exist'))
        
        # List all regions
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('📋 Current regions:'))
        for page in TrainingPage.objects.all().order_by('region'):
            program_info = f" → {page.current_program.name}" if page.current_program else " (no program)"
            self.stdout.write(self.style.SUCCESS(f'   • {page.region.capitalize()}: {page.timezone}{program_info}'))

