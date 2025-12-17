# Quick Railway Setup Guide

## ✅ Automatic Configuration

The project now includes a root-level `railway.json` file that tells Railway to:
- Use the Dockerfile from `backend/Dockerfile`
- Build and deploy the backend automatically

**You don't need to manually set the root directory anymore!**

## Step-by-Step Deployment:

1. **Create the project in Railway:**
   - Go to [Railway.app](https://railway.app) and sign up/login
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your `MinaEwedaa/Massar` repository
   - Railway will automatically detect the `railway.json` configuration

2. **Railway will now:**
   - Use the Dockerfile from `backend/Dockerfile`
   - Build the Python application
   - Deploy automatically

3. **Set Environment Variables:**
   - Go to your service → **Variables** tab
   - Add: `CORS_ORIGINS` = `https://your-frontend-url.vercel.app` (set after deploying frontend)
   - `PORT` is automatically set by Railway

4. **Deploy:**
   - Railway will automatically build and deploy
   - Wait for the build to complete
   - Copy the generated URL (e.g., `https://your-app.up.railway.app`)

## How It Works

The root-level `railway.json` file tells Railway to:
- Use Dockerfile builder
- Point to `backend/Dockerfile` 
- The Dockerfile is configured to copy files from the `backend/` directory when built from root

## Alternative: Using Railway CLI

If you prefer using the CLI:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Deploy
railway up
```

## Troubleshooting

- **Still getting "could not determine how to build":** Make sure the `railway.json` file is in the root directory
- **Build fails:** Check that `backend/Dockerfile` exists and `backend/requirements.txt` is present
- **Port errors:** Railway sets `$PORT` automatically - the Dockerfile CMD uses this
- **File not found errors:** The Dockerfile copies from `backend/` directory, so all paths are relative to root

