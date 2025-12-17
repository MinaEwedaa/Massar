# Quick Railway Setup Guide

## The Issue
Railway is analyzing the root directory which contains both `backend/` and `frontend/` folders. Railway needs to know to use the `backend/` directory as the project root.

## Solution: Set Root Directory in Railway

### Step-by-Step:

1. **After creating the project from GitHub:**
   - Go to your Railway project dashboard
   - Click on the service that was created
   - Go to **Settings** tab
   - Scroll down to **Source** section
   - Find **Root Directory** field
   - Set it to: `backend`
   - Click **Save**

2. **Railway will now:**
   - Detect Python from `requirements.txt` in the `backend/` folder
   - Use the `Procfile` or `Dockerfile` in the `backend/` directory
   - Build and deploy correctly

3. **Set Environment Variables:**
   - Go to **Variables** tab
   - Add: `CORS_ORIGINS` = `https://your-frontend-url.vercel.app` (set after deploying frontend)
   - `PORT` is automatically set by Railway

4. **Deploy:**
   - Railway will automatically redeploy when you set the root directory
   - Wait for the build to complete
   - Copy the generated URL (e.g., `https://your-app.up.railway.app`)

## Alternative: Using Railway CLI

If you prefer using the CLI:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Set root directory
railway variables set RAILWAY_ROOT_DIRECTORY=backend

# Deploy
railway up
```

## Troubleshooting

- **Still getting "could not determine how to build":** Make sure the Root Directory is set to exactly `backend` (not `./backend` or `/backend`)
- **Build fails:** Check that `requirements.txt` exists in the `backend/` directory
- **Port errors:** Railway sets `$PORT` automatically - the `Procfile` and `start.sh` use this

