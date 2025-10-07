# Production Deployment Guide with PostgreSQL
**Toyota Virtual Training Session Admin**

Complete guide for deploying your application to production with PostgreSQL database.

---

## 📋 Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Quick Start (Cloud Platforms)](#quick-start-cloud-platforms)
3. [Detailed Deployment Steps](#detailed-deployment-steps)
4. [Platform-Specific Guides](#platform-specific-guides)
5. [Post-Deployment](#post-deployment)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)

---

## 🔍 Pre-Deployment Checklist

### Required Components

- [ ] **PostgreSQL Database** (12+ recommended, 15+ optimal)
- [ ] **Python 3.9+** installed on server
- [ ] **Domain Name** configured and pointing to server
- [ ] **SSL Certificate** (Let's Encrypt or commercial)
- [ ] **Cloud Storage** (Cloudinary or AWS S3) for media files
- [ ] **Email Service** (Gmail, SendGrid, or AWS SES) for notifications

### Environment Variables Required

- [ ] `SECRET_KEY` - Unique secret key for Django
- [ ] `DEBUG=False` - Must be False in production
- [ ] `ALLOWED_HOSTS` - Your production domain(s)
- [ ] `DATABASE_URL` OR `DB_*` variables - PostgreSQL connection
- [ ] `CLOUDINARY_*` variables - Media file storage

### Security Checklist

- [ ] Changed `SECRET_KEY` from default
- [ ] Set `DEBUG=False`
- [ ] Configured `ALLOWED_HOSTS` with your domain
- [ ] Using strong database password
- [ ] HTTPS enabled (SSL certificate installed)
- [ ] Configured `CSRF_TRUSTED_ORIGINS`
- [ ] Reviewed security settings in `settings_production.py`

---

## 🚀 Quick Start (Cloud Platforms)

### Option 1: Render.com (Recommended - Easiest)

**1. Create PostgreSQL Database**
```
Dashboard → New → PostgreSQL
```

**2. Create Web Service**
```
Dashboard → New → Web Service
Connect your GitHub repo
```

**3. Configure Environment**
```
Build Command: pip install -r requirements_production.txt && python manage.py collectstatic --noinput
Start Command: python main.py
```

**4. Set Environment Variables**
```
DJANGO_SETTINGS_MODULE=toyota_training.settings_production
SECRET_KEY=<generate-new-key>
DEBUG=False
DATABASE_URL=<from-render-postgresql>
CLOUDINARY_CLOUD_NAME=<your-value>
CLOUDINARY_API_KEY=<your-value>
CLOUDINARY_API_SECRET=<your-value>
```

**5. Deploy**
```
Render automatically deploys on git push
```

**6. Run Migrations**
```
Shell → python manage.py migrate
Shell → python manage.py createsuperuser
```

---

### Option 2: Heroku

**1. Create App**
```bash
heroku create toyota-training-app
```

**2. Add PostgreSQL**
```bash
heroku addons:create heroku-postgresql:mini
```

**3. Set Environment Variables**
```bash
heroku config:set DJANGO_SETTINGS_MODULE=toyota_training.settings_production
heroku config:set SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
heroku config:set DEBUG=False
heroku config:set CLOUDINARY_CLOUD_NAME=your_value
heroku config:set CLOUDINARY_API_KEY=your_value
heroku config:set CLOUDINARY_API_SECRET=your_value
```

**4. Deploy**
```bash
git push heroku main
```

**5. Run Migrations**
```bash
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

---

### Option 3: Railway.app

**1. Create Project**
```
Dashboard → New Project → Deploy from GitHub
```

**2. Add PostgreSQL**
```
Add Service → Database → PostgreSQL
```

**3. Configure Variables**
```
Add variables as shown in env.production.template
DATABASE_URL will be automatically set
```

**4. Deploy**
```
Railway auto-deploys on git push
```

---

## 📝 Detailed Deployment Steps

### Step 1: Prepare Your Application

**1. Test Locally with PostgreSQL First**
```bash
# Follow POSTGRESQL_TESTING_GUIDE.md to test locally
./setup_postgres_test.sh
export $(cat .env.postgres | xargs)
python manage.py runserver
```

**2. Generate Production SECRET_KEY**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**3. Create Production Environment File**
```bash
cp env.production.template .env.production
# Edit with your production values
# NEVER commit this file to git
```

---

### Step 2: Set Up PostgreSQL Database

**Cloud Managed (Recommended)**
- Render PostgreSQL
- Heroku Postgres
- AWS RDS
- Google Cloud SQL
- Azure Database for PostgreSQL

**Self-Hosted (Advanced)**
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE toyota_training_prod;
CREATE USER toyota_user WITH PASSWORD 'strong_password_here';
GRANT ALL PRIVILEGES ON DATABASE toyota_training_prod TO toyota_user;
\q
```

---

### Step 3: Configure Environment Variables

**Required Variables:**

```bash
# Django Core
SECRET_KEY=your-unique-secret-key-here
DEBUG=False
DJANGO_SETTINGS_MODULE=toyota_training.settings_production
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (Choose one method)
# Method 1: DATABASE_URL (Recommended)
DATABASE_URL=postgres://user:password@host:5432/dbname

# Method 2: Individual variables
DB_NAME=toyota_training_prod
DB_USER=toyota_user
DB_PASSWORD=your_password
DB_HOST=your-db-host.com
DB_PORT=5432
DB_SSLMODE=require

# Cloudinary (for media files)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

---

### Step 4: Deploy Application

**Using Provided Scripts:**

```bash
# 1. Deploy (install dependencies, migrate, collect static)
./deploy_production.sh

# 2. Start application
./start_production.sh
```

**Manual Deployment:**

```bash
# 1. Install dependencies
pip install -r requirements_production.txt

# 2. Run migrations
python manage.py migrate --settings=toyota_training.settings_production

# 3. Collect static files
python manage.py collectstatic --noinput --settings=toyota_training.settings_production

# 4. Create superuser
python manage.py createsuperuser --settings=toyota_training.settings_production

# 5. Start with Gunicorn
gunicorn toyota_training.wsgi:application --bind 0.0.0.0:8000 --workers 2
```

---

### Step 5: Configure Web Server (if using VPS)

**Nginx Configuration** (`/etc/nginx/sites-available/toyota_training`):

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    client_max_body_size 10M;

    location /static/ {
        alias /var/www/toyota_training/staticfiles/;
        expires 30d;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Enable Site:**
```bash
sudo ln -s /etc/nginx/sites-available/toyota_training /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🌐 Platform-Specific Guides

### Render.com Full Guide

**Advantages:**
- Managed PostgreSQL included
- Free SSL certificates
- Auto-deploy from GitHub
- Built-in health checks

**Setup:**

1. **Create Account**: https://render.com

2. **Create PostgreSQL Database**:
   - Dashboard → New → PostgreSQL
   - Name: `toyota-training-db`
   - Plan: Starter ($7/month) or higher
   - Copy the `Internal Database URL`

3. **Create Web Service**:
   - Dashboard → New → Web Service
   - Connect your GitHub repository
   - Name: `toyota-training-app`
   - Environment: `Python 3`
   - Build Command:
     ```bash
     pip install -r requirements_production.txt && python manage.py collectstatic --noinput
     ```
   - Start Command:
     ```bash
     python main.py
     ```

4. **Environment Variables**:
   ```
   DJANGO_SETTINGS_MODULE=toyota_training.settings_production
   SECRET_KEY=<generate-new>
   DEBUG=False
   DATABASE_URL=<from-postgresql-service>
   CLOUDINARY_CLOUD_NAME=<your-value>
   CLOUDINARY_API_KEY=<your-value>
   CLOUDINARY_API_SECRET=<your-value>
   ```

5. **Deploy**: Automatically deploys on git push

6. **Run Migrations**:
   - Go to Web Service → Shell
   - Run: `python manage.py migrate`
   - Run: `python manage.py createsuperuser`

---

### AWS Deployment (Advanced)

**Components:**
- EC2 instance (or Elastic Beanstalk)
- RDS PostgreSQL database
- S3 for media files
- CloudFront for CDN
- Route 53 for DNS
- Certificate Manager for SSL

**Quick Setup with Elastic Beanstalk:**

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.9 toyota-training

# Create environment with RDS
eb create production --database.engine postgres

# Set environment variables
eb setenv DJANGO_SETTINGS_MODULE=toyota_training.settings_production
eb setenv SECRET_KEY=your-key
eb setenv DEBUG=False

# Deploy
eb deploy
```

---

## ✅ Post-Deployment

### 1. Verify Deployment

```bash
# Check health endpoint
curl https://yourdomain.com/health/

# Expected: {"status": "healthy"}
```

### 2. Create Admin User

```bash
python manage.py createsuperuser
```

### 3. Test All Features

- [ ] Admin login works
- [ ] Creating training programs
- [ ] Uploading images
- [ ] User permissions
- [ ] All region pages load
- [ ] Forms submission
- [ ] Email notifications (if configured)

### 4. Set Up Monitoring

**Health Checks:**
- `/health/` - Basic health check
- `/health/detailed/` - Detailed system status

**Logs:**
```bash
# Application logs (check your platform's log viewer)
# Render: Dashboard → Logs
# Heroku: heroku logs --tail
# AWS: CloudWatch Logs
```

### 5. Database Backups

**Render:**
```bash
# Automatic daily backups included
# Manual backup: Dashboard → Database → Backups
```

**Heroku:**
```bash
heroku pg:backups:schedule --at '02:00 America/Toronto'
```

**Manual Backup:**
```bash
pg_dump -h hostname -U username -d dbname > backup.sql
```

---

## 📊 Monitoring & Maintenance

### Regular Checks

**Daily:**
- [ ] Application is accessible
- [ ] Health check endpoint responds
- [ ] Error logs are clear

**Weekly:**
- [ ] Database size and performance
- [ ] Disk space usage
- [ ] Memory usage
- [ ] Failed login attempts

**Monthly:**
- [ ] Update dependencies
- [ ] Review security logs
- [ ] Test backups restoration
- [ ] SSL certificate validity

### Performance Monitoring

**Database Queries:**
```python
# In Django shell
from django.db import connection
print(connection.queries)  # Shows all SQL queries
```

**Slow Queries:**
```sql
-- In PostgreSQL
SELECT * FROM pg_stat_statements 
ORDER BY mean_time DESC LIMIT 10;
```

---

## 🔧 Troubleshooting

### Common Issues

**1. "No PostgreSQL configuration found"**
```bash
# Check environment variables
echo $DATABASE_URL
# or
echo $DB_NAME

# Solution: Set DATABASE_URL or DB_* variables
```

**2. "psycopg2 not found"**
```bash
# Solution: Install PostgreSQL adapter
pip install psycopg2-binary==2.9.9
```

**3. "Database connection failed"**
```bash
# Test connection
python test_postgres_connection.py

# Check:
# - Database is running
# - Credentials are correct
# - Firewall allows connection
# - SSL settings match requirements
```

**4. "Static files not loading"**
```bash
# Run collectstatic again
python manage.py collectstatic --noinput

# Check STATIC_ROOT and STATIC_URL in settings
```

**5. "502 Bad Gateway"**
```bash
# Check if gunicorn is running
ps aux | grep gunicorn

# Check logs
tail -f /var/log/nginx/error.log
```

### Emergency Procedures

**Application Down:**
```bash
# Restart application
sudo systemctl restart toyota_training

# Or on cloud platforms, use their restart button
```

**Database Issues:**
```bash
# Check database status
psql $DATABASE_URL -c "SELECT version();"

# Restore from backup
psql $DATABASE_URL < backup.sql
```

---

## 📚 Additional Resources

- **Local Testing**: `POSTGRESQL_TESTING_GUIDE.md`
- **Quick Reference**: `QUICK_START_POSTGRES.md`
- **Connection Testing**: Run `python test_postgres_connection.py`
- **Compatibility Check**: Run `python check_postgres_compatibility.py`

---

## 🎯 Production Checklist

### Before Going Live

- [ ] Tested locally with PostgreSQL
- [ ] All environment variables set
- [ ] SECRET_KEY changed from default
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS configured
- [ ] PostgreSQL database created
- [ ] Migrations applied
- [ ] Static files collected
- [ ] Superuser created
- [ ] SSL certificate installed
- [ ] Health checks working
- [ ] Backups configured
- [ ] Monitoring set up
- [ ] Documentation reviewed

### Security Verification

- [ ] Strong database password
- [ ] HTTPS enforced
- [ ] CSRF protection enabled
- [ ] Security headers configured
- [ ] Session security enabled
- [ ] File upload limits set
- [ ] Admin URL customized (optional)
- [ ] Rate limiting enabled

### Performance Optimization

- [ ] Database connection pooling enabled
- [ ] Static files served with CDN
- [ ] Gzip compression enabled
- [ ] Browser caching configured
- [ ] Database indexes optimized
- [ ] Appropriate number of workers set

---

## 🆘 Support

**Need Help?**

1. Check this guide first
2. Run diagnostic scripts:
   - `python test_postgres_connection.py`
   - `python check_postgres_compatibility.py`
3. Review logs
4. Check platform-specific documentation

**Common Commands:**
```bash
# Test database connection
python test_postgres_connection.py

# Check deployment readiness
python manage.py check --deploy

# View migrations status
python manage.py showmigrations

# Create database backup
python manage.py dumpdata > backup.json
```

---

**Last Updated**: October 2025  
**Version**: 2.0 (PostgreSQL Production)

Your application is production-ready with PostgreSQL! 🚀

