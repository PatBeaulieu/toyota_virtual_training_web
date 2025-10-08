# Railway Deployment - Quick Start Checklist

## ✅ Pre-Deployment (Do This Now)

1. **Commit and Push Your Code**
   ```bash
   git add .
   git commit -m "Prepare for Railway deployment"
   git push origin main
   ```

2. **Generate Secret Key** (Save this for later)
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

3. **Get Cloudinary Credentials** (Sign up at https://cloudinary.com if needed)
   - Cloud Name: `_________________`
   - API Key: `_________________`
   - API Secret: `_________________`

---

## 🚀 Railway Setup (15 minutes)

### 1. Create Project (2 min)
- [ ] Go to https://railway.app
- [ ] Click **"New Project"**
- [ ] Select **"Deploy from GitHub repo"**
- [ ] Choose `toyota_virtual_training` repository

### 2. Add Database (1 min)
- [ ] Click **"+ New"** → **"Database"** → **"Add PostgreSQL"**
- [ ] Railway automatically creates `DATABASE_URL`

### 3. Set Environment Variables (5 min)
Click on your **web service** → **"Variables"** tab:

**Required Variables:**
```
DJANGO_SETTINGS_MODULE=toyota_training.settings_production
SECRET_KEY=(paste generated key from step 2 above)
DEBUG=False
CLOUDINARY_CLOUD_NAME=(your cloud name)
CLOUDINARY_API_KEY=(your api key)
CLOUDINARY_API_SECRET=(your api secret)
```

**Optional Email Variables:**
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@rtmtoyota.ca
```

### 4. Deploy (5 min)
- [ ] Railway auto-deploys after variables are set
- [ ] Wait for build to complete (check **"Deployments"** tab)
- [ ] Verify deployment succeeded (green checkmark)

### 5. Run Migrations (2 min)

**Option A - Railway CLI (Recommended):**
```bash
npm i -g @railway/cli
railway login
railway link
railway run python manage.py migrate
railway run python manage.py createsuperuser
```

**Option B - One-time Script:**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and run migrations
railway login
railway link
railway run python manage.py migrate

# Create admin user (follow prompts)
railway run python manage.py createsuperuser
```

---

## 🎯 Post-Deployment Testing (5 minutes)

- [ ] Visit your app: `https://your-app-name.railway.app`
- [ ] Login to admin: `https://your-app-name.railway.app/simple-admin/`
- [ ] Upload a test image (verify Cloudinary works)
- [ ] Check a training program page loads
- [ ] Verify CSS/JS files load correctly

---

## 🌐 Custom Domain (Optional - 10 minutes)

1. **In Railway:**
   - [ ] **"Settings"** → **"Networking"** → **"Add Domain"**
   - [ ] Enter your domain (e.g., `training.rtmtoyota.ca`)

2. **In Your DNS Provider:**
   - [ ] Add CNAME record provided by Railway
   - [ ] Wait 5-30 minutes for propagation

3. **Update Code:**
   ```bash
   # Edit toyota_training/settings_production.py
   # Add your domain to CSRF_TRUSTED_ORIGINS
   CSRF_TRUSTED_ORIGINS = [
       'https://your-custom-domain.com',
       'https://*.railway.app',
   ]
   
   git add .
   git commit -m "Add custom domain to CSRF trusted origins"
   git push
   ```

---

## 📊 Quick Reference

### Your URLs:
- **App:** `https://[your-app].railway.app`
- **Admin:** `https://[your-app].railway.app/simple-admin/`
- **Health:** `https://[your-app].railway.app/health/`

### Common Commands:
```bash
# View logs
railway logs

# Run Django commands
railway run python manage.py [command]

# Open shell
railway shell

# Check variables
railway variables

# Set a variable
railway variables set KEY=value
```

### Troubleshooting:
| Issue | Solution |
|-------|----------|
| Static files not loading | Check deployment logs, verify `collectstatic` ran |
| Database error | Verify PostgreSQL is added, check `DATABASE_URL` |
| CSRF error | Add Railway domain to `CSRF_TRUSTED_ORIGINS` |
| 500 error | Check logs: `railway logs` |

---

## 📝 Notes

- **Free Tier:** Railway provides $5/month in free credits
- **Auto-Deploy:** Enable in Settings → Auto Deploy
- **Backups:** Set up periodic database exports
- **Monitoring:** Check Railway dashboard for usage/metrics

---

## ✅ Done!

Your app is deployed! 🎉

**Next:** See `RAILWAY_DEPLOYMENT.md` for detailed documentation.

