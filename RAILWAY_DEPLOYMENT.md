# Railway.com Deployment Guide
## Toyota Virtual Training Session Admin

This guide will walk you through deploying your Django application on Railway.com.

---

## Prerequisites

- A Railway.com account (sign up at https://railway.app)
- Git repository (GitHub, GitLab, or Bitbucket)
- Your code pushed to the repository

---

## Step-by-Step Deployment Instructions

### Step 1: Prepare Your Repository

1. **Commit all changes to Git:**
   ```bash
   git add .
   git commit -m "Prepare for Railway deployment"
   git push origin main
   ```

### Step 2: Create a New Project on Railway

1. Go to https://railway.app and log in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authenticate with GitHub if needed
5. Select your `toyota_virtual_training` repository
6. Railway will automatically detect your Django application

### Step 3: Add PostgreSQL Database

1. In your Railway project dashboard, click **"+ New"**
2. Select **"Database"**
3. Choose **"Add PostgreSQL"**
4. Railway will automatically:
   - Create a PostgreSQL database
   - Generate a `DATABASE_URL` environment variable
   - Link it to your application

### Step 4: Configure Environment Variables

Click on your **web service** (not the database), then go to the **"Variables"** tab and add the following:

#### Required Variables:

| Variable Name | Value | Description |
|--------------|-------|-------------|
| `DJANGO_SETTINGS_MODULE` | `toyota_training.settings_production` | Use production settings |
| `SECRET_KEY` | *(generate new key)* | See below for generation |
| `DEBUG` | `False` | Disable debug mode |
| `CLOUDINARY_CLOUD_NAME` | `your_cloud_name` | Your Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | `your_api_key` | Your Cloudinary API key |
| `CLOUDINARY_API_SECRET` | `your_api_secret` | Your Cloudinary API secret |

#### Optional Variables:

| Variable Name | Value | Description |
|--------------|-------|-------------|
| `EMAIL_HOST` | `smtp.gmail.com` | SMTP server for emails |
| `EMAIL_PORT` | `587` | SMTP port |
| `EMAIL_HOST_USER` | `your-email@gmail.com` | Email address |
| `EMAIL_HOST_PASSWORD` | `your-app-password` | Email app password |
| `DEFAULT_FROM_EMAIL` | `noreply@rtmtoyota.ca` | Default sender email |

**Note:** Railway automatically provides:
- `PORT` - The port your app should listen on
- `DATABASE_URL` - PostgreSQL connection string
- `RAILWAY_STATIC_URL` - Your app's URL
- `RAILWAY_PUBLIC_DOMAIN` - Your public domain

### Step 5: Generate a Secret Key

Run this command locally to generate a secure secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and paste it as the `SECRET_KEY` environment variable in Railway.

### Step 6: Set Up Cloudinary (Media Storage)

Railway uses ephemeral storage (files are deleted on redeploy), so you need cloud storage for media files:

1. Sign up at https://cloudinary.com (free tier available)
2. Get your credentials from the Cloudinary dashboard
3. Add them as environment variables in Railway (see Step 4)

### Step 7: Deploy Your Application

Railway will automatically deploy when you:
1. Click **"Deploy"** in the Railway dashboard, OR
2. Push new commits to your repository (if auto-deploy is enabled)

**Deployment Process:**
- Railway reads `nixpacks.toml` for build configuration
- Installs dependencies from `requirements_production.txt`
- Runs `collectstatic` to gather static files
- Starts the app using the `Procfile` command

### Step 8: Run Database Migrations

After the first deployment:

1. Go to your **web service** in Railway
2. Click on the **"Settings"** tab
3. Scroll to **"Deploy"** section
4. Add a **"Deploy Hook"** or run manually:

**Option A: Using Railway CLI (Recommended)**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Run migrations
railway run python manage.py migrate

# Create superuser
railway run python manage.py createsuperuser
```

**Option B: Using Railway Dashboard**
1. Go to your service's **"Settings"** → **"Deploy"**
2. Under **"Custom Start Command"**, temporarily change to:
   ```
   python manage.py migrate && python manage.py createsuperuser && gunicorn toyota_training.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 30
   ```
3. Redeploy the service
4. After superuser is created, remove the `createsuperuser` part

### Step 9: Seed Initial Data (Optional)

If you need to populate initial training programs:

```bash
railway run python create_initial_data.py
```

Or upload via the admin interface at: `https://your-app.railway.app/simple-admin/`

### Step 10: Set Up Custom Domain (Optional)

1. In Railway, go to your **web service**
2. Click **"Settings"** → **"Networking"**
3. Under **"Custom Domain"**, click **"Add Domain"**
4. Enter your domain (e.g., `training.rtmtoyota.ca`)
5. Add the provided DNS records to your domain registrar:
   - **CNAME** record pointing to Railway
6. Wait for DNS propagation (5-30 minutes)
7. Railway will automatically provision an SSL certificate

**Important:** After adding your custom domain, update the `CSRF_TRUSTED_ORIGINS` in `settings_production.py`:

```python
CSRF_TRUSTED_ORIGINS = [
    'https://your-custom-domain.com',
    'https://*.railway.app',
]
```

---

## Post-Deployment Checklist

- [ ] Application loads successfully
- [ ] Database connection works
- [ ] Static files (CSS/JS) are loading
- [ ] Admin login works at `/simple-admin/`
- [ ] Image uploads work (Cloudinary integration)
- [ ] Training programs display correctly
- [ ] All regions are accessible
- [ ] SSL certificate is active (https://)
- [ ] Environment variables are set correctly
- [ ] No sensitive data in logs

---

## Monitoring and Logs

### View Logs:
1. Go to your Railway project
2. Click on your **web service**
3. Click **"Deployments"**
4. View real-time logs in the dashboard

### Common Log Commands:
```bash
# View recent logs
railway logs

# Follow logs in real-time
railway logs --follow
```

---

## Environment-Specific Settings

Railway automatically sets these environment variables:

| Variable | Description |
|----------|-------------|
| `RAILWAY_ENVIRONMENT` | Current environment (production, staging, etc.) |
| `RAILWAY_STATIC_URL` | Your app's Railway URL |
| `RAILWAY_PUBLIC_DOMAIN` | Your public domain |
| `DATABASE_URL` | PostgreSQL connection string |
| `PORT` | Port to bind the application to |

---

## Troubleshooting

### Issue: Static Files Not Loading

**Solution:**
1. Ensure `whitenoise` is installed (check `requirements_production.txt`)
2. Verify `STATICFILES_STORAGE` is set in `settings_production.py`
3. Check that `collectstatic` ran during deployment (check logs)

### Issue: Database Connection Error

**Solution:**
1. Verify PostgreSQL database is added to the project
2. Check that `DATABASE_URL` environment variable exists
3. Ensure `psycopg2-binary` is in `requirements_production.txt`
4. Run migrations: `railway run python manage.py migrate`

### Issue: Application Won't Start

**Solution:**
1. Check deployment logs for errors
2. Verify all required environment variables are set
3. Ensure `SECRET_KEY` is set
4. Check that `DJANGO_SETTINGS_MODULE` is set to `toyota_training.settings_production`

### Issue: Media Files Not Saving

**Solution:**
1. Verify Cloudinary credentials are set correctly
2. Check `DEFAULT_FILE_STORAGE` in `settings_production.py`
3. Test Cloudinary connection from Railway CLI:
   ```bash
   railway run python -c "import cloudinary; print(cloudinary.config())"
   ```

### Issue: CSRF Verification Failed

**Solution:**
1. Add your Railway domain to `CSRF_TRUSTED_ORIGINS` in `settings_production.py`
2. Ensure `CSRF_COOKIE_SECURE = True` (for HTTPS)
3. Redeploy after making changes

---

## Scaling Your Application

Railway makes scaling easy:

### Vertical Scaling (More Resources):
1. Go to **"Settings"** → **"Resources"**
2. Adjust **CPU** and **Memory** limits
3. Railway will restart your service with new resources

### Horizontal Scaling (More Instances):
1. Adjust `--workers` in `Procfile`:
   ```
   web: gunicorn toyota_training.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 30
   ```
2. Redeploy the service

**Recommended Workers:** `(2 x CPU cores) + 1`

---

## Cost Optimization

Railway offers:
- **$5/month free credits** (for hobby projects)
- **Pay-as-you-go pricing** after free credits

**Tips to reduce costs:**
1. Use the smallest database size that meets your needs
2. Optimize worker count (start with 2)
3. Enable **"Sleep on Idle"** for staging environments
4. Use Cloudinary's free tier for media storage
5. Monitor usage in Railway dashboard

---

## Backup Strategy

### Database Backups:

Railway doesn't provide automatic backups on the free tier. Set up manual backups:

```bash
# Export database backup
railway run python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > backup.json

# Import database backup
railway run python manage.py loaddata backup.json
```

### Automated Backup Script:
Create a scheduled task using Railway cron or external service to run:
```bash
railway run pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
```

---

## Security Best Practices

1. ✅ **Never commit `.env` or secrets** to Git
2. ✅ **Use strong `SECRET_KEY`** (min 50 characters)
3. ✅ **Keep `DEBUG = False`** in production
4. ✅ **Enable HTTPS** (automatic with Railway)
5. ✅ **Use environment variables** for all secrets
6. ✅ **Regularly update dependencies**:
   ```bash
   pip list --outdated
   pip install --upgrade django
   ```
7. ✅ **Monitor logs** for suspicious activity
8. ✅ **Implement rate limiting** for login endpoints
9. ✅ **Use Cloudinary** for secure file uploads
10. ✅ **Keep Railway CLI** up to date

---

## Continuous Deployment

Railway supports automatic deployments:

1. **Enable Auto-Deploy:**
   - Go to **"Settings"** → **"Environment"**
   - Enable **"Auto Deploy"**
   - Choose your branch (usually `main`)

2. **Deploy on Push:**
   - Every push to the selected branch triggers a deployment
   - Railway automatically builds and deploys your app

3. **Deploy Specific Branches:**
   - Create separate Railway services for staging/production
   - Link different branches to each service

---

## Getting Help

- **Railway Docs:** https://docs.railway.app
- **Railway Discord:** https://discord.gg/railway
- **Django Docs:** https://docs.djangoproject.com

---

## Quick Reference Commands

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# View environment variables
railway variables

# Set an environment variable
railway variables set KEY=value

# Run migrations
railway run python manage.py migrate

# Create superuser
railway run python manage.py createsuperuser

# View logs
railway logs

# SSH into container
railway shell

# Deploy from CLI
railway up
```

---

## Summary

Your application is now deployed on Railway! 🚀

**Your URLs:**
- **Application:** `https://your-app.railway.app`
- **Admin Panel:** `https://your-app.railway.app/simple-admin/`
- **API Health Check:** `https://your-app.railway.app/health/`

**Next Steps:**
1. Test all functionality
2. Set up custom domain
3. Configure monitoring/alerts
4. Create database backups
5. Add team members in Railway dashboard

---

**Questions or Issues?** 
Check the troubleshooting section above or contact your development team.

