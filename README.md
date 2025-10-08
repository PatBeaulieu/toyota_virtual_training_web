# Toyota Virtual Training Session Admin

A Django-based web application for managing virtual training sessions for Toyota dealerships across different regions.

## Features

- 🌍 **Multi-Region Support** - Separate training content for different geographical regions
- 🎓 **Training Programs** - Manage and deliver training materials
- 📊 **Admin Dashboard** - Simple admin interface for content management
- 🔒 **Secure Authentication** - Role-based access control
- 📱 **Responsive Design** - Works on desktop and mobile devices
- ☁️ **Cloud Storage** - Cloudinary integration for media files
- 🚀 **Production Ready** - Configured for PostgreSQL and production deployment

## Tech Stack

- **Backend:** Django 4.2.25
- **Database:** PostgreSQL (production) / SQLite (development)
- **Web Server:** Gunicorn
- **Static Files:** WhiteNoise
- **Media Storage:** Cloudinary
- **Python:** 3.9+

## Quick Start (Development)

### Prerequisites
- Python 3.9+
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd toyota_virtual_training
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server:**
   ```bash
   python manage.py runserver
   ```

7. **Access the application:**
   - Application: http://localhost:8000
   - Admin: http://localhost:8000/simple-admin/

## Deployment

This application is ready to deploy on multiple platforms:

### 🚂 Railway.com (Recommended)

**Complete guides available:**
- 📄 **[RAILWAY_QUICK_START.md](RAILWAY_QUICK_START.md)** - Quick deployment checklist (15 minutes)
- 📄 **[RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)** - Comprehensive deployment guide
- 📄 **[RAILWAY_DEPLOYMENT_SUMMARY.md](RAILWAY_DEPLOYMENT_SUMMARY.md)** - Detailed summary with troubleshooting
- 📋 **[DEPLOY_CHECKLIST.txt](DEPLOY_CHECKLIST.txt)** - Printable checklist

**Quick Deploy:**
```bash
# 1. Install Railway CLI
npm i -g @railway/cli

# 2. Login and deploy
railway login
railway init
railway up

# 3. Add PostgreSQL
railway add postgresql

# 4. Set environment variables (see RAILWAY_QUICK_START.md)

# 5. Run migrations
railway run python manage.py migrate
railway run python manage.py createsuperuser
```

### Other Platforms

- **Render.com** - See `PRODUCTION_DEPLOYMENT.md`
- **Heroku** - Compatible with existing `Procfile`
- **DigitalOcean** - Use Docker configuration
- **AWS/GCP/Azure** - Follow standard Django deployment guides

## Configuration

### Environment Variables

Required environment variables for production:

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Django secret key | ✅ Yes |
| `DEBUG` | Debug mode (False in production) | ✅ Yes |
| `DATABASE_URL` | PostgreSQL connection string | ✅ Yes |
| `DJANGO_SETTINGS_MODULE` | Settings module path | ✅ Yes |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name | ✅ Yes |
| `CLOUDINARY_API_KEY` | Cloudinary API key | ✅ Yes |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret | ✅ Yes |

Optional variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `EMAIL_HOST` | SMTP server | smtp.gmail.com |
| `EMAIL_PORT` | SMTP port | 587 |
| `EMAIL_HOST_USER` | Email username | - |
| `EMAIL_HOST_PASSWORD` | Email password | - |

### Generate Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Project Structure

```
toyota_virtual_training/
├── toyota_training/          # Django project settings
│   ├── settings.py          # Development settings
│   ├── settings_production.py  # Production settings
│   ├── urls.py              # URL routing
│   └── wsgi.py              # WSGI configuration
├── training_app/            # Main application
│   ├── models.py            # Database models
│   ├── views.py             # View logic
│   ├── admin.py             # Admin configuration
│   ├── forms.py             # Form definitions
│   ├── templates/           # HTML templates
│   └── static/              # Static files (CSS, JS)
├── static/                  # Global static files
├── staticfiles/            # Collected static files (production)
├── media/                  # User-uploaded files (development)
├── requirements.txt        # Development dependencies
├── requirements_production.txt  # Production dependencies
├── Procfile               # Process configuration
├── nixpacks.toml         # Railway build configuration
├── runtime.txt           # Python version
└── manage.py            # Django management script
```

## Admin Interface

### Access Levels

1. **Super Admin** - Full access to all regions and settings
2. **Regional Admin** - Access to specific regions only

### Admin URLs

- Simple Admin: `/simple-admin/`
- Django Admin: `/django-admin/` (if enabled)
- Login: `/admin/login/`

## Database

### Development
- SQLite database (`db.sqlite3`)
- Automatically created on first run

### Production
- PostgreSQL required
- Configured via `DATABASE_URL` environment variable
- Connection pooling enabled
- SSL support

### Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations
```

## Static Files

Static files are managed by WhiteNoise in production:

```bash
# Collect static files
python manage.py collectstatic --noinput
```

## Media Files

Media files (uploaded images) are stored in Cloudinary for production:

1. Sign up at https://cloudinary.com
2. Get API credentials
3. Set environment variables
4. Uploads automatically sync to Cloudinary

## Testing

```bash
# Run tests
python manage.py test

# Run specific test
python manage.py test training_app.tests.TestName

# With coverage
coverage run --source='.' manage.py test
coverage report
```

## Troubleshooting

### Common Issues

**Static files not loading:**
- Run `python manage.py collectstatic`
- Verify WhiteNoise is in `MIDDLEWARE`

**Database connection error:**
- Check `DATABASE_URL` is set correctly
- Verify PostgreSQL is running
- Check database credentials

**Import errors:**
- Activate virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`

**Migration errors:**
- Delete migration files (except `__init__.py`)
- Run `python manage.py makemigrations`
- Run `python manage.py migrate`

### Get Help

1. Check deployment guides in `/docs`
2. Review Railway documentation
3. Check application logs
4. Contact development team

## Security

### Production Security Checklist

- [x] `DEBUG = False`
- [x] Strong `SECRET_KEY`
- [x] HTTPS enabled
- [x] CSRF protection
- [x] SQL injection protection (Django ORM)
- [x] XSS protection
- [x] Secure cookies
- [x] Security headers
- [ ] Rate limiting (optional)
- [ ] Two-factor authentication (optional)

## License

Proprietary - Toyota Motor Corporation

## Support

For technical support or questions:
- Email: support@rtmtoyota.ca
- Documentation: See deployment guides in project root

## Changelog

### Version 1.0 (October 2025)
- Initial production release
- Multi-region support
- Cloudinary integration
- Railway deployment configuration
- PostgreSQL support
- Security enhancements

---

**Quick Links:**
- 🚂 [Deploy to Railway](RAILWAY_QUICK_START.md)
- 📖 [Full Documentation](RAILWAY_DEPLOYMENT.md)
- 📋 [Deployment Checklist](DEPLOY_CHECKLIST.txt)
- ⚙️ [Configuration Guide](RAILWAY_DEPLOYMENT_SUMMARY.md)

---

*Last Updated: October 2025*

