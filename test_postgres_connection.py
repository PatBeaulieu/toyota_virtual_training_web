#!/usr/bin/env python
"""
Test PostgreSQL connection for Toyota Virtual Training application.

This script verifies that:
1. PostgreSQL driver (psycopg2) is installed
2. Environment variables are set correctly
3. Database connection can be established
4. Django can use the database

Run this before running migrations to ensure everything is configured properly.
"""

import os
import sys


def test_psycopg2_installation():
    """Test if psycopg2 is installed."""
    print("=" * 60)
    print("1. Checking psycopg2 installation...")
    print("=" * 60)
    
    try:
        import psycopg2
        print("✅ psycopg2 is installed")
        print(f"   Version: {psycopg2.__version__}")
        return True
    except ImportError:
        print("❌ psycopg2 is NOT installed")
        print("   Run: pip install psycopg2-binary")
        return False


def test_environment_variables():
    """Test if required environment variables are set."""
    print("\n" + "=" * 60)
    print("2. Checking environment variables...")
    print("=" * 60)
    
    database_url = os.environ.get('DATABASE_URL')
    db_name = os.environ.get('DB_NAME')
    db_user = os.environ.get('DB_USER')
    db_password = os.environ.get('DB_PASSWORD')
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '5432')
    
    if database_url:
        print("✅ DATABASE_URL is set")
        print(f"   URL: {database_url.split('@')[0]}@***")  # Hide sensitive info
        return True, 'DATABASE_URL'
    elif db_name and db_user and db_password:
        print("✅ Individual database environment variables are set:")
        print(f"   DB_NAME: {db_name}")
        print(f"   DB_USER: {db_user}")
        print(f"   DB_PASSWORD: {'*' * len(db_password)}")
        print(f"   DB_HOST: {db_host}")
        print(f"   DB_PORT: {db_port}")
        return True, 'individual'
    else:
        print("❌ Database environment variables are NOT set")
        print("\n   You need to set either:")
        print("   Option A: DATABASE_URL")
        print("   Option B: DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT")
        print("\n   Example:")
        print("   export DB_NAME=toyota_training_test")
        print("   export DB_USER=toyota_user")
        print("   export DB_PASSWORD=your_password")
        print("   export DB_HOST=localhost")
        print("   export DB_PORT=5432")
        return False, None


def test_direct_connection():
    """Test direct connection to PostgreSQL."""
    print("\n" + "=" * 60)
    print("3. Testing direct PostgreSQL connection...")
    print("=" * 60)
    
    try:
        import psycopg2
    except ImportError:
        print("⚠️ Skipping - psycopg2 not installed")
        return False
    
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # Parse DATABASE_URL
        try:
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()
            cursor.execute('SELECT version();')
            version = cursor.fetchone()[0]
            print("✅ Successfully connected to PostgreSQL!")
            print(f"   {version}")
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Failed to connect using DATABASE_URL")
            print(f"   Error: {e}")
            return False
    else:
        # Use individual variables
        db_name = os.environ.get('DB_NAME')
        db_user = os.environ.get('DB_USER')
        db_password = os.environ.get('DB_PASSWORD')
        db_host = os.environ.get('DB_HOST', 'localhost')
        db_port = os.environ.get('DB_PORT', '5432')
        
        if not all([db_name, db_user, db_password]):
            print("⚠️ Skipping - environment variables not set")
            return False
        
        try:
            conn = psycopg2.connect(
                dbname=db_name,
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port
            )
            cursor = conn.cursor()
            cursor.execute('SELECT version();')
            version = cursor.fetchone()[0]
            print("✅ Successfully connected to PostgreSQL!")
            print(f"   {version}")
            
            # Test if database exists and is accessible
            cursor.execute('SELECT current_database();')
            current_db = cursor.fetchone()[0]
            print(f"   Current database: {current_db}")
            
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Failed to connect to PostgreSQL")
            print(f"   Error: {e}")
            print("\n   Common issues:")
            print("   - PostgreSQL server is not running")
            print("   - Database does not exist")
            print("   - User does not have access")
            print("   - Wrong password")
            print("   - Wrong host or port")
            return False


def test_django_connection():
    """Test Django database connection."""
    print("\n" + "=" * 60)
    print("4. Testing Django database configuration...")
    print("=" * 60)
    
    try:
        # Set up Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toyota_training.settings')
        
        import django
        django.setup()
        
        from django.db import connection
        from django.conf import settings
        
        # Get database engine
        db_engine = settings.DATABASES['default']['ENGINE']
        print(f"   Database engine: {db_engine}")
        
        if 'postgresql' in db_engine:
            print("✅ Django is configured to use PostgreSQL")
            
            # Test connection
            with connection.cursor() as cursor:
                cursor.execute('SELECT version();')
                version = cursor.fetchone()[0]
                print(f"   Connection successful!")
                print(f"   {version}")
            
            # Get database name
            db_name = settings.DATABASES['default'].get('NAME', 'Unknown')
            print(f"   Database: {db_name}")
            
            return True
        elif 'sqlite' in db_engine:
            print("⚠️ Django is configured to use SQLite, not PostgreSQL")
            print("   This means environment variables are not set properly")
            return False
        else:
            print(f"⚠️ Django is using unexpected database engine: {db_engine}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to test Django connection")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_tables():
    """Test if migrations have been run."""
    print("\n" + "=" * 60)
    print("5. Checking database tables...")
    print("=" * 60)
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toyota_training.settings')
        
        import django
        django.setup()
        
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Get list of tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            if tables:
                print(f"✅ Found {len(tables)} tables in database:")
                for table in tables[:10]:  # Show first 10
                    print(f"   - {table}")
                if len(tables) > 10:
                    print(f"   ... and {len(tables) - 10} more")
                
                # Check for key Django tables
                key_tables = [
                    'django_migrations',
                    'auth_user',
                    'training_app_customuser',
                    'training_app_trainingprogram'
                ]
                
                missing = [t for t in key_tables if t not in tables]
                if missing:
                    print(f"\n⚠️ Some expected tables are missing:")
                    for table in missing:
                        print(f"   - {table}")
                    print("\n   Run migrations: python manage.py migrate")
                else:
                    print("\n✅ All key tables are present")
                
                return True
            else:
                print("⚠️ No tables found in database")
                print("   Run migrations: python manage.py migrate")
                return False
                
    except Exception as e:
        print(f"⚠️ Could not check tables (this is OK if migrations haven't been run yet)")
        print(f"   Error: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("PostgreSQL Connection Test for Toyota Virtual Training")
    print("=" * 60)
    
    results = []
    
    # Test 1: psycopg2 installation
    results.append(("psycopg2 installation", test_psycopg2_installation()))
    
    # Test 2: Environment variables
    env_result, env_type = test_environment_variables()
    results.append(("Environment variables", env_result))
    
    # Test 3: Direct connection (only if env vars are set)
    if env_result:
        results.append(("Direct PostgreSQL connection", test_direct_connection()))
    
    # Test 4: Django connection (only if psycopg2 is installed)
    if results[0][1]:
        results.append(("Django configuration", test_django_connection()))
    
    # Test 5: Database tables (only if Django connection works)
    if results[0][1] and len(results) >= 4 and results[3][1]:
        results.append(("Database tables", test_database_tables()))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("\nYou're ready to use PostgreSQL with your Django application.")
        print("\nNext steps:")
        print("  1. Run migrations: python manage.py migrate")
        print("  2. Create superuser: python manage.py createsuperuser")
        print("  3. Start server: python manage.py runserver")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease fix the issues above before proceeding.")
        print("Refer to POSTGRESQL_TESTING_GUIDE.md for detailed instructions.")
    
    print("=" * 60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())

