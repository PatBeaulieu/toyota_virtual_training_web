#!/usr/bin/env python
"""
Check Django models for PostgreSQL compatibility.

This script analyzes your Django models and identifies potential issues
when migrating from SQLite to PostgreSQL.
"""

import os
import sys


def check_model_fields():
    """Check for field types that may behave differently in PostgreSQL."""
    print("=" * 60)
    print("Checking Model Field Compatibility")
    print("=" * 60)
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toyota_training.settings')
        import django
        django.setup()
        
        from django.apps import apps
        from django.db import models
        
        issues = []
        warnings = []
        
        for model in apps.get_models():
            if model._meta.app_label == 'training_app':
                model_name = f"{model._meta.app_label}.{model.__name__}"
                
                for field in model._meta.get_fields():
                    if not hasattr(field, 'get_internal_type'):
                        continue
                    
                    field_type = field.get_internal_type()
                    field_name = f"{model_name}.{field.name}"
                    
                    # Check for boolean fields (different defaults)
                    if field_type == 'BooleanField':
                        if not hasattr(field, 'default'):
                            warnings.append(
                                f"⚠️ {field_name}: BooleanField without default. "
                                "PostgreSQL requires explicit default or null=True"
                            )
                    
                    # Check for CharField without max_length
                    if field_type == 'CharField':
                        if not hasattr(field, 'max_length') or field.max_length is None:
                            issues.append(
                                f"❌ {field_name}: CharField must have max_length in PostgreSQL"
                            )
                    
                    # Check for TextField with max_length (different behavior)
                    if field_type == 'TextField' and hasattr(field, 'max_length') and field.max_length:
                        warnings.append(
                            f"⚠️ {field_name}: TextField with max_length. "
                            "Consider using CharField for better PostgreSQL performance"
                        )
                    
                    # Check for DateTimeField with auto_now/auto_now_add
                    if field_type == 'DateTimeField':
                        if hasattr(field, 'auto_now') and field.auto_now:
                            print(f"ℹ️ {field_name}: Uses auto_now (compatible)")
                        if hasattr(field, 'auto_now_add') and field.auto_now_add:
                            print(f"ℹ️ {field_name}: Uses auto_now_add (compatible)")
        
        if issues:
            print("\n❌ CRITICAL ISSUES FOUND:")
            for issue in issues:
                print(f"  {issue}")
        
        if warnings:
            print("\n⚠️ WARNINGS:")
            for warning in warnings:
                print(f"  {warning}")
        
        if not issues and not warnings:
            print("\n✅ No compatibility issues found!")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_database_operations():
    """Check for database operations that differ between SQLite and PostgreSQL."""
    print("\n" + "=" * 60)
    print("Checking Database Operations")
    print("=" * 60)
    
    try:
        import os
        from pathlib import Path
        
        # Check for case-sensitive queries
        warnings = []
        
        # Search for case-sensitive queries in views
        views_file = Path('training_app/views.py')
        if views_file.exists():
            content = views_file.read_text()
            
            # Check for exact matches without iexact
            if '__exact' in content and '__iexact' not in content:
                warnings.append(
                    "⚠️ Found __exact lookups. PostgreSQL is case-sensitive. "
                    "Consider using __iexact for case-insensitive matching"
                )
            
            # Check for LIKE patterns
            if '.filter(' in content and not '.icontains' in content:
                if 'LIKE' in content.upper():
                    warnings.append(
                        "⚠️ Found LIKE patterns. Use icontains/istartswith for "
                        "case-insensitive matching in PostgreSQL"
                    )
        
        if warnings:
            print("\n⚠️ POTENTIAL ISSUES:")
            for warning in warnings:
                print(f"  {warning}")
        else:
            print("\n✅ No obvious issues found in database operations")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking database operations: {e}")
        return False


def check_migrations():
    """Check for migration files that might have issues."""
    print("\n" + "=" * 60)
    print("Checking Migrations")
    print("=" * 60)
    
    try:
        from pathlib import Path
        
        migrations_dir = Path('training_app/migrations')
        if not migrations_dir.exists():
            print("⚠️ No migrations directory found")
            return False
        
        migration_files = sorted(migrations_dir.glob('*.py'))
        migration_files = [f for f in migration_files if f.name != '__init__.py']
        
        print(f"\nFound {len(migration_files)} migration files:")
        
        issues = []
        for mig_file in migration_files:
            print(f"  ✓ {mig_file.name}")
            
            # Check for SQLite-specific operations
            content = mig_file.read_text()
            if 'sqlite' in content.lower():
                issues.append(f"⚠️ {mig_file.name} contains SQLite-specific code")
        
        if issues:
            print("\n⚠️ MIGRATION WARNINGS:")
            for issue in issues:
                print(f"  {issue}")
            print("\nThese migrations may need to be regenerated for PostgreSQL")
        else:
            print("\n✅ Migrations look compatible")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking migrations: {e}")
        return False


def check_indexes_and_constraints():
    """Check for indexes and constraints."""
    print("\n" + "=" * 60)
    print("Checking Indexes and Constraints")
    print("=" * 60)
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toyota_training.settings')
        import django
        django.setup()
        
        from django.apps import apps
        
        recommendations = []
        
        for model in apps.get_models():
            if model._meta.app_label == 'training_app':
                model_name = f"{model._meta.app_label}.{model.__name__}"
                
                # Check for indexes
                if hasattr(model._meta, 'indexes') and model._meta.indexes:
                    print(f"✓ {model_name} has {len(model._meta.indexes)} indexes")
                
                # Check for unique constraints
                unique_fields = [
                    f.name for f in model._meta.get_fields()
                    if hasattr(f, 'unique') and f.unique
                ]
                if unique_fields:
                    print(f"✓ {model_name} has unique fields: {', '.join(unique_fields)}")
                
                # Check for foreign keys
                fk_fields = [
                    f.name for f in model._meta.get_fields()
                    if f.get_internal_type() == 'ForeignKey'
                ]
                if fk_fields:
                    print(f"✓ {model_name} has foreign keys: {', '.join(fk_fields)}")
                    recommendations.append(
                        f"ℹ️ {model_name}: PostgreSQL will automatically create indexes on foreign keys"
                    )
        
        if recommendations:
            print("\n" + "ℹ️ INFORMATION:")
            for rec in recommendations:
                print(f"  {rec}")
        
        print("\n✅ Indexes and constraints check complete")
        return True
        
    except Exception as e:
        print(f"❌ Error checking indexes: {e}")
        return False


def check_data_compatibility():
    """Check current data for PostgreSQL compatibility."""
    print("\n" + "=" * 60)
    print("Checking Data Compatibility")
    print("=" * 60)
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toyota_training.settings')
        import django
        django.setup()
        
        from django.db import connection
        
        db_engine = connection.settings_dict['ENGINE']
        
        if 'sqlite' in db_engine:
            print("📊 Current database: SQLite")
            print("\nTo test with PostgreSQL:")
            print("  1. Set up PostgreSQL database")
            print("  2. Export data: python manage.py dumpdata > data.json")
            print("  3. Switch to PostgreSQL (set environment variables)")
            print("  4. Run migrations: python manage.py migrate")
            print("  5. Import data: python manage.py loaddata data.json")
        elif 'postgresql' in db_engine:
            print("📊 Current database: PostgreSQL")
            
            # Check data stats
            with connection.cursor() as cursor:
                # Check for any data
                cursor.execute("""
                    SELECT table_name, 
                           (xpath('/row/cnt/text()', xml_count))[1]::text::int as row_count
                    FROM (
                        SELECT table_name, 
                               query_to_xml(format('select count(*) as cnt from %I.%I', 
                                          table_schema, table_name), false, true, '') as xml_count
                        FROM information_schema.tables
                        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                        AND table_name LIKE 'training_app_%'
                    ) t;
                """)
                
                tables = cursor.fetchall()
                if tables:
                    print("\n📈 Data in database:")
                    total_rows = 0
                    for table_name, row_count in tables:
                        print(f"  {table_name}: {row_count} rows")
                        total_rows += row_count if row_count else 0
                    
                    if total_rows > 0:
                        print(f"\n✅ Total rows: {total_rows}")
                    else:
                        print("\n⚠️ No data found. You may want to load test data.")
                else:
                    print("\n⚠️ No application tables found")
        
        return True
        
    except Exception as e:
        print(f"⚠️ Could not check data: {e}")
        print("This is normal if using SQLite or tables haven't been created yet")
        return True  # Not a critical error


def main():
    """Run all compatibility checks."""
    print("\n" + "=" * 60)
    print("PostgreSQL Compatibility Check")
    print("=" * 60)
    
    results = []
    
    results.append(("Model Fields", check_model_fields()))
    results.append(("Database Operations", check_database_operations()))
    results.append(("Migrations", check_migrations()))
    results.append(("Indexes & Constraints", check_indexes_and_constraints()))
    results.append(("Data Compatibility", check_data_compatibility()))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for check_name, passed in results:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("✅ Your application appears to be PostgreSQL-compatible!")
        print("\nNext steps:")
        print("  1. Set up PostgreSQL: ./setup_postgres_test.sh")
        print("  2. Test connection: python test_postgres_connection.py")
        print("  3. Run migrations: python manage.py migrate")
        print("  4. Test your application thoroughly")
    else:
        print("⚠️ Some issues were found")
        print("\nPlease address the issues above before deploying to PostgreSQL")
    
    print("=" * 60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())

