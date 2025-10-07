# Production Deployment Checklist ✅
**Toyota Virtual Training - PostgreSQL Edition**

Use this checklist to ensure a smooth production deployment.

---

## Pre-Deployment

### Environment Setup
- [ ] PostgreSQL database created (version 12+)
- [ ] Domain name purchased and configured
- [ ] SSL certificate obtained (Let's Encrypt or commercial)
- [ ] Cloudinary account created (for media files)
- [ ] Email service configured (optional)

### Local Testing
- [ ] Tested application with PostgreSQL locally
- [ ] Run `python test_postgres_connection.py` - all tests pass
- [ ] Run `python check_postgres_compatibility.py` - no issues
- [ ] All features work with PostgreSQL
- [ ] Database migrations successful
- [ ] Media uploads work with Cloudinary

### Code & Configuration
- [ ] Latest code committed to git
- [ ] `.env` files not in git (.gitignore configured)
- [ ] `requirements_production.txt` includes all dependencies
- [ ] `psycopg2-binary==2.9.9` in requirements

---

## Configuration

### Environment Variables (CRITICAL)
- [ ] `SECRET_KEY` - NEW unique key generated ⚠️ NEVER use default
- [ ] `DEBUG=False` ⚠️ MUST be False in production
- [ ] `DJANGO_SETTINGS_MODULE=toyota_training.settings_production`
- [ ] `ALLOWED_HOSTS` - includes your domain(s)
- [ ] `DATABASE_URL` OR all `DB_*` variables set
- [ ] `CLOUDINARY_CLOUD_NAME` set
- [ ] `CLOUDINARY_API_KEY` set
- [ ] `CLOUDINARY_API_SECRET` set
- [ ] `CSRF_TRUSTED_ORIGINS` - includes your domain

### Generate SECRET_KEY
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Database Configuration (choose one)
**Option A: DATABASE_URL** (Recommended)
```bash
DATABASE_URL=postgres://user:password@host:5432/database
```

**Option B: Individual Variables**
```bash
DB_NAME=toyota_training_prod
DB_USER=toyota_user
DB_PASSWORD=your_strong_password
DB_HOST=your-db-host.com
DB_PORT=5432
DB_SSLMODE=require
```

---

## Deployment

### Initial Setup
- [ ] Install dependencies: `pip install -r requirements_production.txt`
- [ ] Collect static files: `python manage.py collectstatic --noinput`
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Test database connection: `python test_postgres_connection.py`

### Using Deployment Script
```bash
./deploy_production.sh
```

This script automatically:
- Verifies environment
- Installs dependencies
- Runs migrations
- Collects static files
- Sets up cache
- Runs security checks

---

## Security

### Required Security Settings
- [ ] `DEBUG=False` ⚠️ CRITICAL
- [ ] Unique `SECRET_KEY` (not default)
- [ ] HTTPS enabled (SSL certificate installed)
- [ ] `SECURE_SSL_REDIRECT=True` (in settings_production.py)
- [ ] `CSRF_COOKIE_SECURE=True`
- [ ] `SESSION_COOKIE_SECURE=True`
- [ ] Strong database password
- [ ] Admin password is strong

### Security Verification
```bash
# Run Django security check
python manage.py check --deploy --settings=toyota_training.settings_production
```

Expected: No warnings or all warnings reviewed and accepted

---

## Testing

### Functional Testing
- [ ] Homepage loads successfully
- [ ] Admin login works (`/simple-admin/login/`)
- [ ] Can create training program
- [ ] Can upload images
- [ ] Can create training sessions
- [ ] Can create users
- [ ] User permissions work correctly
- [ ] All region pages accessible
- [ ] Forms submit successfully
- [ ] Error pages display correctly (404, 500)

### Health Checks
- [ ] `/health/` returns `{"status": "healthy"}`
- [ ] `/health/detailed/` shows system status
- [ ] Database connection confirmed

### Performance Testing
- [ ] Page load times acceptable (<3 seconds)
- [ ] Images load from Cloudinary
- [ ] Static files load correctly
- [ ] Database queries performant

---

## Post-Deployment

### Immediate Checks (First Hour)
- [ ] Application accessible at production URL
- [ ] HTTPS working (no certificate errors)
- [ ] Admin panel accessible
- [ ] Can log in with superuser
- [ ] Health check endpoint responds
- [ ] No errors in application logs
- [ ] Database connections stable

### First Day
- [ ] Monitor error logs
- [ ] Test all major features
- [ ] Verify file uploads work
- [ ] Check email notifications (if configured)
- [ ] Test from different devices/browsers
- [ ] Monitor database performance
- [ ] Check memory/CPU usage

### First Week
- [ ] Set up automated backups
- [ ] Configure monitoring/alerts
- [ ] Document any issues encountered
- [ ] Fine-tune performance settings
- [ ] Review security logs
- [ ] Test backup restoration

---

## Backups & Monitoring

### Database Backups
- [ ] Automated daily backups configured
- [ ] Backup retention policy set
- [ ] Tested backup restoration
- [ ] Off-site backup storage configured

### Monitoring Setup
- [ ] Application health monitoring
- [ ] Database performance monitoring
- [ ] Disk space monitoring
- [ ] SSL certificate expiration monitoring
- [ ] Error tracking (Sentry, etc.)
- [ ] Uptime monitoring

---

## Platform-Specific

### Render.com
- [ ] PostgreSQL service created
- [ ] Web service created and deployed
- [ ] Environment variables set in dashboard
- [ ] Build command: `pip install -r requirements_production.txt && python manage.py collectstatic --noinput`
- [ ] Start command: `python main.py`
- [ ] Migrations run via Shell
- [ ] Auto-deploy enabled (optional)

### Heroku
- [ ] App created: `heroku create`
- [ ] PostgreSQL addon: `heroku addons:create heroku-postgresql`
- [ ] Environment variables: `heroku config:set ...`
- [ ] Deployed: `git push heroku main`
- [ ] Migrations: `heroku run python manage.py migrate`
- [ ] Scaled: `heroku ps:scale web=1`

### VPS (Custom Server)
- [ ] Server secured (firewall, SSH keys)
- [ ] PostgreSQL installed and running
- [ ] Nginx installed and configured
- [ ] SSL certificate installed (Let's Encrypt)
- [ ] Gunicorn service configured
- [ ] Application deployed to `/var/www/`
- [ ] Services started and enabled
- [ ] Log rotation configured

---

## Documentation

### Required Documentation
- [ ] Production URL documented
- [ ] Admin credentials stored securely
- [ ] Database connection details saved
- [ ] Cloudinary credentials saved
- [ ] Deployment process documented
- [ ] Rollback procedure documented
- [ ] Emergency contacts list
- [ ] Monitoring dashboard URLs

### Update These Files
- [ ] README.md with production info
- [ ] Add production domain to documentation
- [ ] Document any custom configurations
- [ ] Update deployment history

---

## Maintenance Plan

### Regular Tasks

**Daily**
- [ ] Check application is up
- [ ] Review error logs
- [ ] Monitor response times

**Weekly**
- [ ] Review security logs
- [ ] Check database size
- [ ] Test backup restoration
- [ ] Monitor disk space

**Monthly**
- [ ] Update dependencies
- [ ] Review Django security advisories
- [ ] Update SSL certificates (if needed)
- [ ] Performance optimization review
- [ ] Security audit

**Quarterly**
- [ ] Full security review
- [ ] Disaster recovery test
- [ ] Performance optimization
- [ ] Documentation update

---

## Emergency Procedures

### Application Down
```bash
# Check logs first
# Then restart:
./start_production.sh

# Or on cloud platform, use restart button
```

### Database Connection Issues
```bash
# Test connection
python test_postgres_connection.py

# Check database status
psql $DATABASE_URL -c "SELECT 1;"

# Restart database (if self-hosted)
sudo systemctl restart postgresql
```

### Rollback Procedure
```bash
# If using git deploy:
git revert HEAD
git push production main

# Or restore previous version
# Restore database from backup if needed
```

---

## Success Criteria

### Deployment is Successful When:
✅ Application accessible via HTTPS  
✅ All tests pass  
✅ No errors in logs  
✅ Health checks return healthy  
✅ Admin panel accessible  
✅ Database operations working  
✅ File uploads functional  
✅ Performance acceptable  
✅ Security checks pass  
✅ Backups configured  
✅ Monitoring active  

---

## Quick Commands

```bash
# Deploy
./deploy_production.sh

# Start
./start_production.sh

# Test connection
python test_postgres_connection.py

# Check compatibility
python check_postgres_compatibility.py

# Security check
python manage.py check --deploy

# Migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static
python manage.py collectstatic --noinput

# Database backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# View logs (platform dependent)
# Render: Dashboard → Logs
# Heroku: heroku logs --tail
# VPS: tail -f /var/log/toyota_training/django.log
```

---

## Troubleshooting Quick Reference

| Issue | Quick Fix |
|-------|-----------|
| 502 Bad Gateway | Restart application/gunicorn |
| Static files not loading | Run `collectstatic` |
| Database connection failed | Check `DATABASE_URL` and credentials |
| 500 errors | Check logs, set `DEBUG=True` temporarily |
| HTTPS not working | Check SSL certificate |
| Slow performance | Check database indexes, add caching |

---

## Resources

- **Full Guide**: `PRODUCTION_DEPLOYMENT_POSTGRESQL.md`
- **Local Testing**: `POSTGRESQL_TESTING_GUIDE.md`
- **Quick Start**: `QUICK_START_POSTGRES.md`
- **Test Connection**: `python test_postgres_connection.py`
- **Check Compatibility**: `python check_postgres_compatibility.py`

---

**Deployment Date**: ________________  
**Deployed By**: ________________  
**Production URL**: ________________  
**Notes**: ________________

---

✅ **Ready for Production!**

Once all items are checked, your application is production-ready with PostgreSQL! 🚀

