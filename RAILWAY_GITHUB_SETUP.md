# Railway + GitHub Authorization Guide

## Step-by-Step: Connect Railway to GitHub

### Option 1: Sign Up with GitHub (Easiest)

1. **Visit Railway:**
   ```
   https://railway.app
   ```

2. **Click "Login with GitHub"**
   - If you don't have a Railway account, click "Sign up with GitHub"

3. **Authorize Railway:**
   - GitHub will show: "Railway by Railway Corp would like permission to:"
     - ✓ Verify your GitHub identity
     - ✓ Know which resources you can access
     - ✓ Act on your behalf
   - Click **"Authorize Railway"**

4. **Grant Repository Access:**
   - Choose one:
     - **"All repositories"** (easiest)
     - **"Only select repositories"** → Select `toyota_virtual_training_web`
   - Click **"Install & Authorize"**

5. **Done!** You can now deploy from GitHub

---

### Option 2: Connect GitHub to Existing Railway Account

If you already have a Railway account with email:

1. **Login to Railway:**
   ```
   https://railway.app/login
   ```

2. **Go to Your Profile:**
   - Click your avatar (bottom left)
   - Click **"Settings"**

3. **Connect GitHub:**
   - Go to **"Integrations"** tab
   - Find **"GitHub"** section
   - Click **"Connect GitHub"**

4. **Authorize on GitHub:**
   - You'll be redirected to GitHub
   - Click **"Authorize Railway"**

5. **Select Repositories:**
   - Choose repository access
   - Click **"Install & Authorize"**

---

### Troubleshooting: Railway Can't See Your Repository

If your repository doesn't show up in Railway:

#### Check GitHub Installation Settings

1. **Go to GitHub:**
   ```
   https://github.com/settings/installations
   ```

2. **Find "Railway":**
   - Look for "Railway" in the installed applications list
   - Click **"Configure"** next to Railway

3. **Update Repository Access:**
   - Under "Repository access":
     - Select **"All repositories"**, OR
     - Select **"Only select repositories"**
     - Make sure `toyota_virtual_training_web` is checked

4. **Save Changes:**
   - Click **"Save"**
   - Wait a few seconds

5. **Return to Railway:**
   - Refresh the page
   - Your repository should now appear!

#### Check Repository Visibility

Make sure your repository is not private, or if it is, that Railway has access:

1. **Go to your repository:**
   ```
   https://github.com/PatBeaulieu/toyota_virtual_training_web
   ```

2. **Check Settings:**
   - Click **"Settings"** tab
   - Under "Danger Zone", check if it's private or public
   - If private, ensure Railway has access (see steps above)

---

## Deploy from GitHub Repository

Once authorized:

### 1. Create New Project

1. **Railway Dashboard:**
   ```
   https://railway.app/dashboard
   ```

2. **Click "New Project"**

3. **Select "Deploy from GitHub repo"**

4. **Choose Repository:**
   - Search for: `toyota_virtual_training_web`
   - Click on it

5. **Railway Auto-Detects:**
   - Sees it's a Python/Django app
   - Reads `nixpacks.toml`
   - Reads `Procfile`
   - Starts initial build

### 2. Configure Project

1. **Add PostgreSQL Database:**
   - Click **"+ New"**
   - Select **"Database"**
   - Choose **"Add PostgreSQL"**

2. **Set Environment Variables:**
   - Click on your web service
   - Go to **"Variables"** tab
   - Add required variables (see RAILWAY_QUICK_START.md)

3. **Deploy:**
   - Railway automatically deploys after variables are set
   - Or click **"Deploy"** manually

---

## Enable Auto-Deploy from GitHub

To automatically deploy when you push to GitHub:

### 1. Enable Auto-Deploy

1. **In Railway:**
   - Click on your **web service**
   - Go to **"Settings"** tab

2. **Find "Environment" Section:**
   - Look for **"Source"**
   - You should see your GitHub repo connected

3. **Enable Auto Deploy:**
   - Find **"Automatic Deployments"** toggle
   - Turn it **ON** (should be blue)

4. **Select Branch:**
   - Choose branch: **`main`** (or your default branch)
   - Railway will deploy every push to this branch

### 2. Test Auto-Deploy

Make a small change and push:

```bash
# Make a small change
echo "# Test" >> README.md

# Commit and push
git add README.md
git commit -m "Test auto-deploy"
git push origin main

# Check Railway dashboard - it should start deploying automatically!
```

---

## Manage Deployments

### View Deployment Status

1. **Railway Dashboard:**
   - Click on your service
   - Go to **"Deployments"** tab

2. **See Recent Deployments:**
   - Each push creates a new deployment
   - Shows build logs
   - Shows success/failure status

### Rollback to Previous Deployment

1. **Deployments Tab:**
   - Click on a previous successful deployment
   - Click **"Redeploy"**
   - Confirms rollback

---

## Disconnect/Reconnect GitHub

### Disconnect GitHub from Railway

1. **Railway Settings:**
   - Profile → Settings → Integrations
   - Find GitHub
   - Click **"Disconnect"**

### Reconnect GitHub

1. **Railway Settings:**
   - Profile → Settings → Integrations
   - Click **"Connect GitHub"**
   - Follow authorization steps again

---

## Common Issues & Solutions

### Issue: "Railway app is not installed on your account"

**Solution:**
1. Go to https://github.com/settings/installations
2. Find Railway
3. Click "Configure"
4. Grant access to repositories
5. Save and refresh Railway

### Issue: Repository not showing in Railway

**Solution:**
1. Check GitHub installation settings
2. Ensure repository is not archived
3. Refresh Railway page
4. Try disconnecting and reconnecting GitHub

### Issue: "Failed to fetch repository"

**Solution:**
1. Check internet connection
2. Verify GitHub is not down (https://www.githubstatus.com)
3. Re-authorize Railway in GitHub settings
4. Contact Railway support if persists

### Issue: Auto-deploy not working

**Solution:**
1. Check "Automatic Deployments" is enabled in Railway settings
2. Verify correct branch is selected
3. Check webhook exists: GitHub repo → Settings → Webhooks
4. Look for Railway webhook (should be there)
5. Test webhook by clicking "Redeliver"

---

## Security Best Practices

### Repository Access

- **Recommended:** Use "Only select repositories" for better security
- Only grant Railway access to repos you want to deploy
- Regularly review access in GitHub settings

### Environment Variables

- **Never commit secrets** to GitHub
- Use Railway's environment variables for all sensitive data
- Keep `.env` files in `.gitignore`

### Webhook Security

- Railway uses secure webhooks for auto-deploy
- Don't disable or modify Railway's webhook
- Webhook is automatically created and managed

---

## Quick Reference

### Key URLs

| Service | URL |
|---------|-----|
| Railway Dashboard | https://railway.app/dashboard |
| Railway Settings | https://railway.app/account/settings |
| GitHub Installations | https://github.com/settings/installations |
| Your Repository | https://github.com/PatBeaulieu/toyota_virtual_training_web |

### Railway CLI Commands

```bash
# Login to Railway
railway login

# Link to project
railway link

# Check current project
railway status

# View logs
railway logs

# Deploy manually
railway up
```

---

## Next Steps

After connecting GitHub to Railway:

1. ✅ Authorize Railway with GitHub
2. ✅ Create new Railway project from GitHub repo
3. ✅ Add PostgreSQL database
4. ✅ Configure environment variables
5. ✅ Enable auto-deploy
6. ✅ Push changes to GitHub
7. ✅ Watch automatic deployments!

---

**Need Help?**
- Railway Docs: https://docs.railway.app/develop/integrations#github
- Railway Discord: https://discord.gg/railway
- GitHub Support: https://support.github.com

---

*Last Updated: October 2025*

