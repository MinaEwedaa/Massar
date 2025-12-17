# Troubleshooting 404 Errors

## Issue: Frontend getting 404 when connecting to Railway backend

### Step 1: Verify Railway Backend is Running

1. Go to your Railway dashboard
2. Check that your service is **Deployed** and **Active**
3. Copy the Railway URL (e.g., `https://your-app.up.railway.app`)
4. Test the backend directly:
   - Visit: `https://your-app.up.railway.app/api/v1/health`
   - You should see a JSON response like `{"status": "healthy"}`

### Step 2: Set Environment Variable in Vercel

**IMPORTANT**: The Railway integration in Railway settings doesn't automatically set Vercel environment variables. You need to set it in Vercel:

1. Go to your Vercel project dashboard
2. Go to **Settings** → **Environment Variables**
3. Add a new variable:
   - **Name**: `VITE_API_BASE_URL`
   - **Value**: `https://your-railway-url.up.railway.app/api/v1`
   - **Environment**: Select all (Production, Preview, Development)
4. Click **Save**
5. **Redeploy** your Vercel app (go to Deployments → click the three dots → Redeploy)

### Step 3: Set CORS in Railway

1. Go to your Railway service dashboard
2. Go to **Variables** tab
3. Add/Update the `CORS_ORIGINS` variable:
   - **Name**: `CORS_ORIGINS`
   - **Value**: Your Vercel URL (e.g., `https://your-app.vercel.app`)
   - If you have multiple origins, separate with commas: `https://app1.vercel.app,https://app2.vercel.app`
4. Railway will automatically redeploy

### Step 4: Verify the Connection

1. Open your Vercel frontend in a browser
2. Open Developer Tools (F12) → **Network** tab
3. Try to use the app (e.g., submit a form or load data)
4. Check the Network tab:
   - Look for requests to your Railway URL
   - Check if they return 404, CORS errors, or 200 OK

### Common Issues:

#### Issue: Still getting 404
- **Check**: Is the Railway URL correct? It should end with `/api/v1` for the base URL
- **Check**: Did you redeploy Vercel after setting the environment variable?
- **Check**: Open browser console and check what URL the frontend is trying to use

#### Issue: CORS Error
- **Check**: Is `CORS_ORIGINS` set in Railway with your exact Vercel URL?
- **Check**: Make sure there's no trailing slash in the Vercel URL in CORS_ORIGINS
- **Check**: Railway service needs to be redeployed after changing CORS_ORIGINS

#### Issue: Network Error / Connection Refused
- **Check**: Is Railway service actually running? Check the Railway dashboard
- **Check**: Is the Railway URL accessible? Try visiting it directly in a browser
- **Check**: Railway might be using a different port - make sure your start command uses `$PORT`

### Quick Test:

Run this in your browser console on your Vercel site:
```javascript
console.log('API URL:', import.meta.env.VITE_API_BASE_URL);
```

This will show you what URL the frontend is trying to use. It should be your Railway URL.

