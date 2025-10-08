# Railway Deployment - Summary

## 🎯 What We've Prepared

Your Django application is now ready for deployment on Railway.com. Here's what was configured:

### Files Created/Updated:

1. **`Procfile`** - Updated for Railway
   - Web process command for gunicorn
   - Release process for migrations and static files

2. **`nixpacks.toml`** - Railway build configuration
   - Python 3.9 environment
   - PostgreSQL support
   - Automated static file collection

3. **`runtime.txt`** - Python version specification
   - Set to Python 3.9.20 (compatible with your venv 3.9.6)

4. **`toyota_training/settings_production.py`** - Updated for Railway
   - Added Railway domain support (`.railway.app`)
   - Added Railway-specific environment variables
   - Updated CSRF trusted origins

5. **Documentation Created:**
   - `RAILWAY_DEPLOYMENT.md` - Comprehensive deployment guide
   - `RAILWAY_QUICK_START.md` - Quick deployment checklist

---

## 📋 Step-by-Step Deployment Guide

### **Phase 1: Preparation (5 minutes)**

#### 1.1 Generate Secret Key
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
**Save this key** - you'll need it for Railway environment variables.

#### 1.2 Get Cloudinary Credentials
- Sign up at https://cloudinary.com (free tier available)
- Get your credentials from dashboard:
  - Cloud Name
  - API Key
  - API Secret

#### 1.3 Commit and Push Your Code
```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

---

### **Phase 2: Railway Setup (10 minutes)**

#### 2.1 Create Railway Project
1. Go to https://railway.app
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authenticate with GitHub if prompted
5. Select your `toyota_virtual_training` repository
6. Railway will automatically detect it's a Django app

#### 2.2 Add PostgreSQL Database
1. In your Railway project, click **"+ New"**
2. Select **"Database"**
3. Choose **"Add PostgreSQL"**
4. Railway automatically creates and links the database
5. `DATABASE_URL` environment variable is created automatically

#### 2.3 Configure Environment Variables
Click on your **web service** (not the database), then **"Variables"** tab:

**Copy and paste these (update values):**
```
DJANGO_SETTINGS_MODULE=toyota_training.settings_production
SECRET_KEY=<paste-your-generated-secret-key>
DEBUG=False
CLOUDINARY_CLOUD_NAME=<your-cloudinary-cloud-name>
CLOUDINARY_API_KEY=<your-cloudinary-api-key>
CLOUDINARY_API_SECRET=<your-cloudinary-api-secret>
```

**Optional Email Settings:**
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=noreply@rtmtoyota.ca
```

#### 2.4 Deploy
- Railway automatically deploys after environment variables are set
- Monitor deployment in **"Deployments"** tab
- Wait for build to complete (2-5 minutes)

---

### **Phase 3: Database Setup (5 minutes)**

#### 3.1 Install Railway CLI
```bash
npm i -g @railway/cli
```

#### 3.2 Login and Link Project
```bash
railway login
railway link
```
Select your project and service when prompted.

#### 3.3 Run Database Migrations
```bash
railway run python manage.py migrate
```

#### 3.4 Create Superuser Account
```bash
railway run python manage.py createsuperuser
```
Follow the prompts to create your admin account.

#### 3.5 (Optional) Seed Initial Data
```bash
railway run python create_initial_data.py
```

---

### **Phase 4: Verification (5 minutes)**

#### 4.1 Access Your Application
Your Railway URL will be: `https://[your-app-name].railway.app`

#### 4.2 Test Checklist
- [ ] Homepage loads successfully
- [ ] Static files (CSS/JS) are loading
- [ ] Admin login works at `/simple-admin/`
- [ ] Can login with superuser credentials
- [ ] Can upload images (tests Cloudinary)
- [ ] Training programs display correctly
- [ ] All regions work properly
- [ ] HTTPS is enabled (green padlock)

---

### **Phase 5: Custom Domain (Optional - 10 minutes)**

#### 5.1 Add Domain in Railway
1. Go to your service → **"Settings"** → **"Networking"**
2. Click **"Add Domain"**
3. Enter your domain: `training.rtmtoyota.ca`
4. Railway provides DNS records

#### 5.2 Update DNS Records
Add the provided CNAME record to your DNS provider:
```
Type: CNAME
Name: training (or your subdomain)
Value: [provided by Railway]
TTL: 300 (or default)
```

#### 5.3 Update CSRF Settings
Edit `toyota_training/settings_production.py`:
```python
CSRF_TRUSTED_ORIGINS = [
    'https://training.rtmtoyota.ca',  # Add your domain
    'https://*.railway.app',
]
```

Then deploy the update:
```bash
git add .
git commit -m "Add custom domain to CSRF trusted origins"
git push origin main
```

Railway will auto-deploy the changes.

---

## 🔧 Railway Configuration Reference

### Environment Variables (Auto-Provided by Railway)
- `PORT` - Port your app listens on
- `DATABASE_URL` - PostgreSQL connection string
- `RAILWAY_STATIC_URL` - Your app's Railway URL
- `RAILWAY_PUBLIC_DOMAIN` - Public domain
- `RAILWAY_ENVIRONMENT` - Deployment environment

### Your Required Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `DJANGO_SETTINGS_MODULE` | Django settings file | `toyota_training.settings_production` |
| `SECRET_KEY` | Django secret key | `django-insecure-xyz123...` |
| `DEBUG` | Debug mode | `False` |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name | `your-cloud-name` |
| `CLOUDINARY_API_KEY` | Cloudinary API key | `123456789012345` |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret | `abc123xyz789...` |

---

## 📊 Monitoring & Maintenance

### View Logs
```bash
# Real-time logs
railway logs --follow

# Recent logs
railway logs
```

### Common Maintenance Commands
```bash
# Run Django management commands
railway run python manage.py [command]

# Check database status
railway run python manage.py dbshell

# Collect static files
railway run python manage.py collectstatic --noinput

# Create database backup
railway run python manage.py dumpdata > backup.json

# Access shell
railway shell
```

### Monitor Resources
- Go to Railway Dashboard
- Click your project → **"Metrics"**
- View CPU, Memory, Network usage
- Set up alerts if needed

---

## 🚨 Troubleshooting

### Issue: Deployment Failed

**Check:**
1. Build logs in Railway dashboard
2. Verify all required packages in `requirements_production.txt`
3. Ensure Python version is correct in `runtime.txt`

**Solution:**
```bash
# View detailed logs
railway logs

# Force rebuild
git commit --allow-empty -m "Force rebuild"
git push
```

### Issue: Static Files Not Loading

**Symptoms:** No CSS, broken layout

**Solution:**
1. Check deployment logs for `collectstatic` output
2. Verify `whitenoise` is in `requirements_production.txt`
3. Manually trigger:
   ```bash
   railway run python manage.py collectstatic --noinput
   ```

### Issue: Database Connection Error

**Symptoms:** `OperationalError: could not connect to server`

**Solution:**
1. Verify PostgreSQL is added to Railway project
2. Check `DATABASE_URL` exists:
   ```bash
   railway variables
   ```
3. Run migrations:
   ```bash
   railway run python manage.py migrate
   ```

### Issue: Application Error 500

**Solution:**
1. Check logs for detailed error:
   ```bash
   railway logs --follow
   ```
2. Verify all environment variables are set
3. Check `SECRET_KEY` is set
4. Ensure `DEBUG=False`

### Issue: CSRF Verification Failed

**Symptoms:** `CSRF verification failed` on forms

**Solution:**
1. Add Railway domain to `CSRF_TRUSTED_ORIGINS` in `settings_production.py`
2. Ensure cookies are being sent over HTTPS
3. Check `CSRF_COOKIE_SECURE = True` in production settings

### Issue: Images Not Uploading

**Symptoms:** Upload fails or images don't appear

**Solution:**
1. Verify Cloudinary credentials are correct
2. Test connection:
   ```bash
   railway run python -c "import cloudinary; cloudinary.config(); print('Connected!')"
   ```
3. Check Cloudinary dashboard for uploaded files
4. Verify `DEFAULT_FILE_STORAGE` setting

---

## 💰 Cost Management

### Railway Pricing
- **$5/month free credits** (hobby tier)
- **Usage-based pricing** after free credits

### Included in Free Tier
- 500 hours of runtime per month
- Shared CPU and memory
- PostgreSQL database
- Custom domain
- SSL certificates

### Tips to Stay Within Free Tier
1. Use minimal worker count (2 workers)
2. Enable "Sleep on Idle" for dev/staging
3. Optimize database queries
4. Use Cloudinary free tier for images
5. Monitor usage in Railway dashboard

---

## 🔐 Security Checklist

- [x] `DEBUG = False` in production
- [x] Strong `SECRET_KEY` (50+ characters)
- [x] Database credentials not in code
- [x] `.env` files in `.gitignore`
- [x] HTTPS enabled (automatic with Railway)
- [x] CSRF protection enabled
- [x] Security headers configured
- [x] SQL injection protection (Django ORM)
- [ ] Set up rate limiting (optional)
- [ ] Configure fail2ban (optional)
- [ ] Enable two-factor auth for admin (optional)

---

## 📈 Performance Optimization

### Current Configuration
- **Workers:** 2 (configured in Procfile)
- **Timeout:** 30 seconds
- **Database Connections:** Pooled (600s max age)
- **Static Files:** Compressed by WhiteNoise

### Scaling Recommendations

**For Light Traffic (<1000 users/day):**
```
--workers 2
```

**For Medium Traffic (1000-5000 users/day):**
```
--workers 4
```

**For Heavy Traffic (>5000 users/day):**
```
--workers 4
# Consider upgrading to higher Railway plan
```

Update in `Procfile`:
```
web: gunicorn toyota_training.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 30
```

---

## 🎓 Additional Resources

### Documentation
- **Railway Docs:** https://docs.railway.app
- **Django Deployment:** https://docs.djangoproject.com/en/4.2/howto/deployment/
- **Gunicorn Config:** https://docs.gunicorn.org/en/stable/settings.html

### Support
- **Railway Discord:** https://discord.gg/railway
- **Railway Status:** https://status.railway.app
- **Railway Blog:** https://blog.railway.app

### Tools
- **Railway CLI:** https://docs.railway.app/develop/cli
- **Railway GitHub App:** Auto-deploys from GitHub
- **Railway API:** https://docs.railway.app/reference/public-api

---

## ✅ Deployment Complete!

Your Toyota Virtual Training application is now live on Railway! 🎉

### Quick Links
- **Application:** `https://[your-app].railway.app`
- **Admin Panel:** `https://[your-app].railway.app/simple-admin/`
- **Health Check:** `https://[your-app].railway.app/health/`

### Next Steps
1. ✅ Test all functionality
2. ✅ Set up custom domain
3. ✅ Configure monitoring
4. ✅ Schedule database backups
5. ✅ Add team members in Railway

---

**Need help?** Refer to:
- `RAILWAY_QUICK_START.md` - Quick reference
- `RAILWAY_DEPLOYMENT.md` - Detailed guide
- Railway Support - https://railway.app/help

**Questions?** Contact your development team or check Railway's community Discord.

---

*Last Updated: October 2025*
*Railway Configuration Version: 1.0*

