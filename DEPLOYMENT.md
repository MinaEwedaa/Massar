# Deployment Guide for Massar

This guide will help you deploy both the backend and frontend of the Massar application to production.

## Prerequisites

- GitHub account with the repository pushed
- Accounts on hosting platforms (Railway/Render for backend, Vercel/Netlify for frontend)

## Step 1: Push to GitHub

If you haven't already pushed your code:

```bash
git add .
git commit -m "Prepare for production deployment"
git push origin main
```

## Step 2: Deploy Backend

### Option A: Railway (Recommended)

1. Go to [Railway.app](https://railway.app) and sign up/login
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `MinaEwedaa/Massar` repository
4. **IMPORTANT**: After the service is created, go to Settings → Source → Root Directory and set it to `backend`
   - This tells Railway to use the `backend/` folder as the project root
   - Alternatively, you can use the Railway CLI: `railway link` then set root directory
5. Railway will now detect Python and use the `Procfile` or `Dockerfile` in the backend directory
6. Set environment variables in Railway dashboard (Variables tab):
   - `CORS_ORIGINS`: Your frontend URL (e.g., `https://your-frontend.vercel.app`) - set this after deploying frontend
   - `DATABASE_URL`: Leave default (Railway provides SQLite) or set to PostgreSQL if needed
   - `MODEL_PATH`: `/app/model/model.joblib` (default, only if using Docker)
   - `PORT`: Railway sets this automatically, but ensure your start command uses `$PORT`
7. Railway will automatically deploy and provide a URL like `https://your-app.up.railway.app`
8. Copy this URL - you'll need it for the frontend

**Note**: If Railway still can't detect the project, it will use the Dockerfile in the `backend/` directory automatically once the root directory is set.

### Option B: Render

1. Go to [Render.com](https://render.com) and sign up/login
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `massar-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Set environment variables:
   - `CORS_ORIGINS`: Your frontend URL
   - `DATABASE_URL`: Leave default or set PostgreSQL URL
   - `MODEL_PATH`: `/opt/render/project/src/model/model.joblib`
6. Click "Create Web Service"
7. Copy the service URL (e.g., `https://massar-backend.onrender.com`)

## Step 3: Deploy Frontend

### Option A: Vercel (Recommended)

1. Go to [Vercel.com](https://vercel.com) and sign up/login
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build/client`
5. Add environment variable:
   - `VITE_API_BASE_URL`: Your backend URL (e.g., `https://your-backend.railway.app/api/v1`)
6. Click "Deploy"
7. Vercel will provide a URL like `https://your-app.vercel.app`

### Option B: Netlify

1. Go to [Netlify.com](https://netlify.com) and sign up/login
2. Click "Add new site" → "Import an existing project"
3. Connect your GitHub repository
4. Configure:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `build/client`
5. Add environment variable:
   - `VITE_API_BASE_URL`: Your backend URL
6. Click "Deploy site"
7. Netlify will provide a URL like `https://your-app.netlify.app`

## Step 4: Update CORS Settings

After deploying the frontend, update the backend's `CORS_ORIGINS` environment variable to include your frontend URL:

- In Railway: Go to your project → Variables → Add `CORS_ORIGINS` with your frontend URL
- In Render: Go to your service → Environment → Add `CORS_ORIGINS` with your frontend URL

**Important**: If using multiple origins, separate them with commas:
```
https://your-app.vercel.app,https://your-app.netlify.app
```

## Step 5: Verify Deployment

1. Visit your frontend URL
2. Open browser developer tools (F12)
3. Check the Network tab to ensure API calls are going to your backend
4. Test the application functionality

## Troubleshooting

### Backend Issues

- **Model not loading**: Ensure `MODEL_PATH` points to the correct location in your deployment
- **Database errors**: For production, consider using PostgreSQL instead of SQLite
- **CORS errors**: Verify `CORS_ORIGINS` includes your exact frontend URL (with https://)

### Frontend Issues

- **API connection errors**: Verify `VITE_API_BASE_URL` is set correctly
- **Build failures**: Check Node.js version (should be 18+)
- **404 errors**: Ensure redirect rules are configured (Vercel/Netlify handle this automatically)

## Production Considerations

1. **Database**: Consider migrating from SQLite to PostgreSQL for production
2. **Authentication**: Add authentication/authorization before exposing publicly
3. **Rate Limiting**: Implement rate limiting on API endpoints
4. **HTTPS**: All hosting platforms provide HTTPS by default
5. **Monitoring**: Set up error tracking (e.g., Sentry) and monitoring

## Environment Variables Summary

### Backend
- `CORS_ORIGINS`: Comma-separated list of allowed frontend URLs
- `DATABASE_URL`: Database connection string (optional, defaults to SQLite)
- `MODEL_PATH`: Path to model file (optional, has default)

### Frontend
- `VITE_API_BASE_URL`: Backend API base URL (e.g., `https://api.example.com/api/v1`)

