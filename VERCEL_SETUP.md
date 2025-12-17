# Vercel Environment Variable Setup

## Your Backend URL
Your Railway backend is hosted at: **https://massar-production.up.railway.app/**

## Quick Setup (2 Minutes)

### Step 1: Set Environment Variable in Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click on your **massar-pearl** project (or whatever your project name is)
3. Go to **Settings** → **Environment Variables**
4. Click **Add New**
5. Enter:
   - **Key**: `VITE_API_BASE_URL`
   - **Value**: `https://massar-production.up.railway.app/api/v1`
   - **Environment**: ✅ Check all three boxes:
     - Production
     - Preview  
     - Development
6. Click **Save**

### Step 2: Redeploy Vercel

**IMPORTANT**: After adding the environment variable, you MUST redeploy:

1. Go to **Deployments** tab
2. Find your latest deployment
3. Click the three dots (⋯) menu
4. Click **Redeploy**
5. Wait for deployment to complete

### Step 3: Set CORS in Railway

1. Go to [Railway Dashboard](https://railway.app)
2. Click on your **massar-production** service
3. Go to **Variables** tab
4. Add or update:
   - **Name**: `CORS_ORIGINS`
   - **Value**: `https://massar-pearl.vercel.app` (your Vercel URL)
5. Railway will automatically redeploy

### Step 4: Test

1. Wait for both deployments to complete
2. Visit your Vercel site: `https://massar-pearl.vercel.app`
3. Open browser console (F12)
4. Check the console - you should see the API URL being used
5. Try using the app - it should work!

## Verify It's Working

In your browser console on the Vercel site, run:
```javascript
console.log('API URL:', import.meta.env.VITE_API_BASE_URL);
```

You should see: `https://massar-production.up.railway.app/api/v1`

If you see `undefined` or `http://localhost:8000/api/v1`, the environment variable is not set correctly.

## Troubleshooting

- **Still seeing localhost error**: Make sure you redeployed Vercel after adding the environment variable
- **CORS errors**: Make sure `CORS_ORIGINS` in Railway includes your exact Vercel URL
- **404 errors**: Check that the Railway URL is correct and the backend is running

