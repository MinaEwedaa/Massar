# CORS Error - Quick Fix

## The Problem
```
Access to fetch at 'https://massar-production.up.railway.app/api/v1/health' 
from origin 'https://massar-mhiz.vercel.app' has been blocked by CORS policy
```

Your frontend at `https://massar-mhiz.vercel.app` is being blocked by the backend.

## The Fix (2 Minutes)

### Step 1: Set CORS in Railway

1. Go to [Railway Dashboard](https://railway.app)
2. Click on your **massar-production** service
3. Go to **Variables** tab
4. Add or update the variable:
   - **Name**: `CORS_ORIGINS`
   - **Value**: `https://massar-mhiz.vercel.app`
   - (Make sure there are no spaces or trailing slashes)
5. Click **Save**

### Step 2: Wait for Redeploy

Railway will automatically redeploy. Wait 1-2 minutes.

### Step 3: Test

Go back to your Vercel site and try again. It should work now!

## If You Have Multiple Frontend URLs

If you have multiple Vercel deployments (production, preview, etc.), separate them with commas:

```
https://massar-mhiz.vercel.app,https://massar-mhiz-git-main.vercel.app
```

## Verify It's Set

After Railway redeploys, check the Railway logs. You should see:
```
INFO:app.main:CORS origins from environment: ['https://massar-mhiz.vercel.app']
```

If you see the default localhost origins, the variable isn't set correctly.

