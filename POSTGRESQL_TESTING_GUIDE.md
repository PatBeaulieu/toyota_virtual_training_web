# PostgreSQL Offline Testing Guide

This guide will help you test your Django application with PostgreSQL locally before deploying to production.

## Prerequisites

You need to have PostgreSQL installed on your system.

### Installing PostgreSQL on macOS

```bash
# Using Homebrew (recommended)
brew install postgresql@15

# Start PostgreSQL service
brew services start postgresql@15

# Or start it manually for this session only:
# pg_ctl -D /opt/homebrew/var/postgresql@15 start
```

### Installing PostgreSQL on Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Installing PostgreSQL on Windows

Download and install from: https://www.postgresql.org/download/windows/

## Step 1: Install Python Dependencies

First, install the PostgreSQL adapter for Python:

```bash
# Activate your virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install updated requirements (includes psycopg2-binary)
pip install -r requirements.txt
```

## Step 2: Create a Test Database

```bash
# Connect to PostgreSQL (macOS/Linux)
psql postgres

# Or on Linux, you may need:
# sudo -u postgres psql

# In the PostgreSQL prompt, run these commands:
```

```sql
-- Create a database user
CREATE USER toyota_user WITH PASSWORD 'your_secure_password';

-- Create the database
CREATE DATABASE toyota_training_test OWNER toyota_user;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE toyota_training_test TO toyota_user;

-- Exit PostgreSQL
\q
```

## Step 3: Configure Environment Variables

### Option A: Using a .env file (Recommended for local testing)

Create a `.env` file in your project root:

```bash
# Database Configuration for PostgreSQL Testing
DB_NAME=toyota_training_test
DB_USER=toyota_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

Then load it before running Django:

```bash
# On macOS/Linux
export $(cat .env | xargs)

# Or use python-dotenv (install: pip install python-dotenv)
```

### Option B: Set environment variables directly

```bash
# macOS/Linux
export DB_NAME=toyota_training_test
export DB_USER=toyota_user
export DB_PASSWORD=your_secure_password
export DB_HOST=localhost
export DB_PORT=5432

# Windows (Command Prompt)
set DB_NAME=toyota_training_test
set DB_USER=toyota_user
set DB_PASSWORD=your_secure_password
set DB_HOST=localhost
set DB_PORT=5432

# Windows (PowerShell)
$env:DB_NAME="toyota_training_test"
$env:DB_USER="toyota_user"
$env:DB_PASSWORD="your_secure_password"
$env:DB_HOST="localhost"
$env:DB_PORT="5432"
```

### Option C: Using DATABASE_URL (Alternative format)

```bash
export DATABASE_URL="postgres://toyota_user:your_secure_password@localhost:5432/toyota_training_test"
```

## Step 4: Test Database Connection

Use the provided test script:

```bash
python test_postgres_connection.py
```

This script will verify:
- PostgreSQL driver is installed
- Database connection is successful
- Settings are configured correctly

## Step 5: Run Migrations

```bash
# Create database tables
python manage.py migrate

# Create a superuser for admin access
python manage.py createsuperuser
```

## Step 6: Load Initial Data (Optional)

If you have existing data or seed scripts:

```bash
# Run your data population scripts
python populate_training_programs.py

# Or use fixtures if you have them
python manage.py loaddata your_fixture.json
```

## Step 7: Run the Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` to test your application with PostgreSQL.

## Step 8: Verify Database is Being Used

Check the startup logs. You should see:
```
✅ Using PostgreSQL database
```

You can also verify by checking which database is in use:

```bash
python manage.py dbshell
```

This should open a PostgreSQL prompt, not SQLite.

## Testing Different Scenarios

### Test 1: Fresh Installation
```bash
# Drop and recreate the database
psql postgres -c "DROP DATABASE toyota_training_test;"
psql postgres -c "CREATE DATABASE toyota_training_test OWNER toyota_user;"

# Run migrations again
python manage.py migrate
```

### Test 2: Data Migration from SQLite to PostgreSQL

```bash
# 1. Export data from SQLite
python manage.py dumpdata --natural-foreign --natural-primary \
    --exclude=contenttypes --exclude=auth.Permission \
    --indent=2 > backup.json

# 2. Switch to PostgreSQL (set environment variables)
export DB_NAME=toyota_training_test
# ... (other variables)

# 3. Run migrations on PostgreSQL
python manage.py migrate

# 4. Load data into PostgreSQL
python manage.py loaddata backup.json
```

### Test 3: Performance Testing

```bash
# Time how long migrations take
time python manage.py migrate

# Check query performance in Django shell
python manage.py shell
>>> from training_app.models import TrainingProgram
>>> import time
>>> start = time.time()
>>> list(TrainingProgram.objects.all())
>>> print(f"Query took {time.time() - start:.4f} seconds")
```

## Troubleshooting

### Error: "psycopg2.OperationalError: could not connect to server"

**Solution:** Make sure PostgreSQL is running:
```bash
# macOS
brew services start postgresql@15

# Linux
sudo systemctl start postgresql

# Check status
psql postgres -c "SELECT version();"
```

### Error: "FATAL: role 'toyota_user' does not exist"

**Solution:** Create the user:
```sql
psql postgres
CREATE USER toyota_user WITH PASSWORD 'your_secure_password';
\q
```

### Error: "FATAL: database 'toyota_training_test' does not exist"

**Solution:** Create the database:
```sql
psql postgres
CREATE DATABASE toyota_training_test OWNER toyota_user;
\q
```

### Error: "psycopg2.OperationalError: FATAL: password authentication failed"

**Solution:** Check your password in the environment variables. You can also update it:
```sql
psql postgres
ALTER USER toyota_user WITH PASSWORD 'new_password';
\q
```

### Error: "django.db.utils.OperationalError: could not connect to server: Connection refused"

**Solution:** PostgreSQL might not be running or listening on the wrong port:
```bash
# Check if PostgreSQL is running
ps aux | grep postgres

# Check which port it's listening on
sudo lsof -i :5432

# Or check PostgreSQL config
psql postgres -c "SHOW port;"
```

## Switching Back to SQLite

To switch back to SQLite for development:

```bash
# Simply unset the PostgreSQL environment variables
unset DB_NAME DB_USER DB_PASSWORD DB_HOST DB_PORT DATABASE_URL

# Or start a new terminal session

# The application will automatically use SQLite
python manage.py runserver
```

## Production Deployment Checklist

Before deploying to production with PostgreSQL:

- [ ] Test all CRUD operations (Create, Read, Update, Delete)
- [ ] Test file uploads and image handling
- [ ] Test user authentication and permissions
- [ ] Test all forms and data validation
- [ ] Run the full test suite: `python manage.py test`
- [ ] Check for migration issues: `python manage.py migrate --plan`
- [ ] Verify all queries work with PostgreSQL syntax
- [ ] Test database backups and restores
- [ ] Configure proper connection pooling settings
- [ ] Set up database backups in production
- [ ] Use strong passwords for production databases
- [ ] Enable SSL for database connections in production

## Additional Resources

- [Django Database Documentation](https://docs.djangoproject.com/en/4.2/ref/databases/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)
- [dj-database-url](https://github.com/jazzband/dj-database-url)

## Quick Reference Commands

```bash
# Connect to PostgreSQL
psql postgres

# List databases
\l

# Connect to specific database
\c toyota_training_test

# List tables
\dt

# Describe table structure
\d training_app_trainingprogram

# View database size
SELECT pg_size_pretty(pg_database_size('toyota_training_test'));

# Exit PostgreSQL
\q
```

