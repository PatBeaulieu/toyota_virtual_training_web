# PostgreSQL Database Optimization Guide
**Toyota Virtual Training - Production Performance Tuning**

This guide covers PostgreSQL optimization for production deployment.

---

## Table of Contents

1. [Connection Settings](#connection-settings)
2. [Query Optimization](#query-optimization)
3. [Indexing Strategy](#indexing-strategy)
4. [Performance Monitoring](#performance-monitoring)
5. [Backup & Maintenance](#backup--maintenance)

---

## Connection Settings

### Django Database Configuration

Your production settings already include optimized connection settings:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,  # ✅ Connection pooling (10 min)
        'OPTIONS': {
            'connect_timeout': 10,  # ✅ Connection timeout
            'sslmode': os.environ.get('DB_SSLMODE', 'prefer'),
            'options': '-c statement_timeout=30000',  # ✅ Query timeout (30s)
        },
        'ATOMIC_REQUESTS': True,  # ✅ Transaction per request
        'AUTOCOMMIT': True,
    }
}
```

### Connection Pooling Explained

**CONN_MAX_AGE=600**
- Keeps database connections open for 10 minutes
- Reduces overhead of creating new connections
- Recommended: 300-600 seconds for web applications

**Adjust based on traffic:**
- Low traffic (< 100 req/day): `CONN_MAX_AGE=60`
- Medium traffic (100-1000 req/day): `CONN_MAX_AGE=300`
- High traffic (> 1000 req/day): `CONN_MAX_AGE=600`

---

## Query Optimization

### 1. Use select_related() for Foreign Keys

**Bad:**
```python
# This creates N+1 queries
for session in TrainingSession.objects.all():
    print(session.training_page.title)  # Extra query each time
```

**Good:**
```python
# This creates only 1 query
for session in TrainingSession.objects.select_related('training_page').all():
    print(session.training_page.title)  # No extra query
```

### 2. Use prefetch_related() for Reverse Relations

**Bad:**
```python
# N+1 queries
for program in TrainingProgram.objects.all():
    sessions = program.trainingsession_set.all()  # Extra query
```

**Good:**
```python
# 2 queries total
for program in TrainingProgram.objects.prefetch_related('trainingsession_set').all():
    sessions = program.trainingsession_set.all()  # No extra query
```

### 3. Use only() to Limit Fields

**Bad:**
```python
# Fetches all fields
users = CustomUser.objects.all()
```

**Good:**
```python
# Fetches only needed fields
users = CustomUser.objects.only('id', 'username', 'email')
```

### 4. Use exists() Instead of count()

**Bad:**
```python
if TrainingProgram.objects.filter(is_active=True).count() > 0:
    # ...
```

**Good:**
```python
if TrainingProgram.objects.filter(is_active=True).exists():
    # Faster - stops at first match
```

---

## Indexing Strategy

### Current Indexes

Django automatically creates indexes for:
- Primary keys (`id`)
- Foreign keys
- Fields with `unique=True`
- Fields with `db_index=True`

### Recommended Additional Indexes

**1. Frequently Queried Fields**

```python
# In models.py

class TrainingPage(models.Model):
    region = models.CharField(
        max_length=50, 
        unique=True,
        db_index=True  # ✅ Already indexed (unique=True)
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True  # ✅ Add if filtering by this often
    )
```

**2. Composite Indexes** (if needed)

```python
class TrainingProgram(models.Model):
    # ...
    class Meta:
        indexes = [
            models.Index(fields=['is_active', 'created_at']),
            # For queries like: TrainingProgram.objects.filter(is_active=True).order_by('-created_at')
        ]
```

### Check Existing Indexes

```sql
-- In PostgreSQL
SELECT 
    tablename, 
    indexname, 
    indexdef 
FROM pg_indexes 
WHERE schemaname = 'public' 
    AND tablename LIKE 'training_app%'
ORDER BY tablename, indexname;
```

### Analyze Index Usage

```sql
-- Find unused indexes
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
    AND idx_scan = 0
    AND indexrelname !~ '^pg_toast';
```

---

## Performance Monitoring

### 1. Enable Query Logging (Development)

```python
# In settings.py (development only!)
if DEBUG:
    LOGGING = {
        'version': 1,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django.db.backends': {
                'handlers': ['console'],
                'level': 'DEBUG',
            },
        },
    }
```

### 2. Django Debug Toolbar (Development)

```bash
pip install django-debug-toolbar
```

```python
# settings.py
INSTALLED_APPS = [
    ...
    'debug_toolbar',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    ...
]

INTERNAL_IPS = ['127.0.0.1']
```

### 3. Monitor Slow Queries (Production)

```sql
-- Enable pg_stat_statements
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Find slow queries
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### 4. Check Database Size

```sql
-- Database size
SELECT pg_size_pretty(pg_database_size('toyota_training_prod'));

-- Table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 5. Connection Statistics

```sql
-- Current connections
SELECT count(*) FROM pg_stat_activity;

-- Connections by state
SELECT state, count(*) 
FROM pg_stat_activity 
GROUP BY state;

-- Long-running queries
SELECT 
    pid,
    now() - pg_stat_activity.query_start AS duration,
    query,
    state
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes'
    AND state != 'idle';
```

---

## PostgreSQL Server Optimization

### Basic Configuration (postgresql.conf)

```ini
# Memory Settings
shared_buffers = 256MB              # 25% of RAM (for dedicated server)
effective_cache_size = 1GB          # 50-75% of RAM
work_mem = 4MB                      # Per operation memory
maintenance_work_mem = 64MB         # For VACUUM, CREATE INDEX

# Connection Settings
max_connections = 100               # Adjust based on needs
superuser_reserved_connections = 3

# Query Planning
random_page_cost = 1.1             # Lower for SSD (default 4.0)
effective_io_concurrency = 200     # Higher for SSD (default 1)

# Logging
log_min_duration_statement = 1000  # Log queries > 1 second
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '

# Auto-vacuum
autovacuum = on
autovacuum_max_workers = 3
autovacuum_naptime = 1min
```

### For Cloud Managed Databases

Most settings are pre-configured. You can typically adjust:
- Connection limits
- Statement timeout
- Query logging

---

## Backup & Maintenance

### Automated Backups

**Daily Backup Script:**

```bash
#!/bin/bash
# /usr/local/bin/backup_database.sh

BACKUP_DIR="/var/backups/toyota_training"
DATE=$(date +%Y%m%d_%H%M%S)
DB_URL="$DATABASE_URL"  # or construct from DB_* variables

# Create backup
pg_dump "$DB_URL" | gzip > "$BACKUP_DIR/backup_$DATE.sql.gz"

# Keep last 30 days
find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: backup_$DATE.sql.gz"
```

**Schedule with cron:**
```bash
# Run daily at 2 AM
0 2 * * * /usr/local/bin/backup_database.sh
```

### Regular Maintenance

**VACUUM (Reclaim Space):**
```sql
-- Manual vacuum (done automatically by autovacuum)
VACUUM ANALYZE;

-- Full vacuum (locks table, use with caution)
VACUUM FULL;

-- Check when last vacuumed
SELECT 
    schemaname,
    relname,
    last_vacuum,
    last_autovacuum,
    n_dead_tup
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY n_dead_tup DESC;
```

**ANALYZE (Update Statistics):**
```sql
-- Update query planner statistics
ANALYZE;

-- For specific table
ANALYZE training_app_trainingprogram;
```

**REINDEX (Rebuild Indexes):**
```sql
-- Rebuild all indexes (rarely needed)
REINDEX DATABASE toyota_training_prod;

-- For specific table
REINDEX TABLE training_app_trainingprogram;
```

---

## Performance Benchmarking

### Django Management Command

Create `training_app/management/commands/benchmark_db.py`:

```python
from django.core.management.base import BaseCommand
from django.db import connection
from training_app.models import TrainingProgram, TrainingPage
import time

class Command(BaseCommand):
    help = 'Benchmark database performance'

    def handle(self, *args, **options):
        # Test 1: Simple query
        start = time.time()
        list(TrainingProgram.objects.all())
        duration = time.time() - start
        self.stdout.write(f"Simple query: {duration:.4f}s")

        # Test 2: With relations
        start = time.time()
        list(TrainingProgram.objects.select_related('trainingpage').all())
        duration = time.time() - start
        self.stdout.write(f"With relations: {duration:.4f}s")

        # Test 3: Query count
        queries_before = len(connection.queries)
        list(TrainingProgram.objects.select_related('trainingpage').all())
        queries_after = len(connection.queries)
        self.stdout.write(f"Queries executed: {queries_after - queries_before}")
```

Run with:
```bash
python manage.py benchmark_db
```

---

## Production Checklist

### Database Optimization

- [ ] Connection pooling enabled (`CONN_MAX_AGE`)
- [ ] Query timeout set (`statement_timeout`)
- [ ] Proper indexes on frequently queried fields
- [ ] `select_related()` used for foreign keys
- [ ] `prefetch_related()` used for reverse relations
- [ ] Slow query logging enabled
- [ ] Database monitoring set up
- [ ] Automated backups configured
- [ ] Regular maintenance scheduled
- [ ] Performance baseline established

### PostgreSQL Server

- [ ] Appropriate memory settings
- [ ] Connection limits configured
- [ ] Auto-vacuum enabled
- [ ] Query logging configured
- [ ] Monitoring tools installed
- [ ] Backup strategy implemented

---

## Troubleshooting

### Slow Queries

**Identify:**
```sql
SELECT * FROM pg_stat_statements 
ORDER BY total_time DESC LIMIT 10;
```

**Solutions:**
1. Add indexes on filtered/sorted columns
2. Use `select_related()` / `prefetch_related()`
3. Add database-level caching
4. Optimize query logic

### High Connection Count

**Check:**
```sql
SELECT count(*) FROM pg_stat_activity WHERE state = 'active';
```

**Solutions:**
1. Reduce `CONN_MAX_AGE`
2. Use connection pooler (PgBouncer)
3. Increase `max_connections`
4. Find connection leaks in code

### Database Growing Too Fast

**Check:**
```sql
SELECT pg_size_pretty(pg_database_size('toyota_training_prod'));
```

**Solutions:**
1. Review data retention policy
2. Archive old data
3. Check for unnecessary logging
4. Run `VACUUM FULL` (with caution)

---

## Additional Resources

- [PostgreSQL Performance Tips](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Django Database Optimization](https://docs.djangoproject.com/en/4.2/topics/db/optimization/)
- [pgAnalyze](https://pganalyze.com/) - PostgreSQL monitoring

---

**Your database is optimized for production!** 🚀

