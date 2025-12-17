# Debug Connection Issues Between Vercel and Railway

## Quick Checklist

### 1. Verify Backend is Running
Test the backend directly:
- Visit: `https://massar-production.up.railway.app/api/v1/health`
- Should return: `{"status": "ok", "model_loaded": true, ...}`
- If this fails, the backend is down - check Railway logs

### 2. Verify Environment Variable in Vercel
1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Check `VITE_API_BASE_URL` value
3. Should be EXACTLY: `https://massar-production.up.railway.app/api/v1`
4. After changing, **MUST redeploy** (Deployments → ⋯ → Redeploy)

### 3. Verify CORS in Railway (CRITICAL)
1. Go to Railway Dashboard → Your Service → Variables
2. Check `CORS_ORIGINS` variable
3. Should be your Vercel URL: `https://massar-pearl.vercel.app`
4. If missing or wrong, add/update it
5. Railway will auto-redeploy

### 4. Test in Browser Console
On your Vercel site, open console (F12) and run:
```javascript
console.log('API URL:', import.meta.env.VITE_API_BASE_URL);
fetch('https://massar-production.up.railway.app/api/v1/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error);
```

This will show:
- What URL the frontend is using
- If the backend is accessible
- Any CORS errors

## Common Issues

### Issue: "Network Error" or "ERR_NETWORK"
**Cause**: CORS not configured
**Fix**: Set `CORS_ORIGINS` in Railway to your Vercel URL

### Issue: "404 Not Found"
**Cause**: Wrong API URL
**Fix**: Check `VITE_API_BASE_URL` includes `/api/v1`

### Issue: "Connection Refused"
**Cause**: Backend not running
**Fix**: Check Railway logs, ensure service is deployed

### Issue: Works in browser but not from frontend
**Cause**: CORS blocking the request
**Fix**: Add Vercel URL to `CORS_ORIGINS` in Railway

## Step-by-Step Fix

1. **Test Backend**: Visit `https://massar-production.up.railway.app/api/v1/health`
   - ✅ Works? Backend is fine
   - ❌ Fails? Check Railway logs

2. **Set CORS in Railway**:
   - Variables → Add `CORS_ORIGINS`
   - Value: `https://massar-pearl.vercel.app` (your exact Vercel URL)
   - Wait for redeploy

3. **Verify Vercel Environment Variable**:
   - Settings → Environment Variables
   - `VITE_API_BASE_URL` = `https://massar-production.up.railway.app/api/v1`
   - Redeploy Vercel

4. **Test Again**: Visit your Vercel site and check browser console

## Still Not Working?

Check Railway logs for:
- CORS errors
- Server startup errors
- Database connection errors

Check browser console (F12) for:
- Network tab → See the actual request/response
- Console tab → See error messages
- Check if request is being blocked by CORS

