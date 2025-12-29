# Vercel Environment Variable - Exact Setup

## ⚠️ Common Mistake

The error shows it's trying to connect to:
```
https://massar-production.up.railway.app/
```

But it should be:
```
https://massar-production.up.railway.app/api/v1
```

## ✅ Correct Setup in Vercel

### Step 1: Go to Vercel Dashboard
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click on your project (massar-pearl)
3. Go to **Settings** → **Environment Variables**

### Step 2: Check/Update the Variable

**IMPORTANT**: The value must be EXACTLY:
```
https://massar-production.up.railway.app/api/v1
```

**NOT:**
- ❌ `https://massar-production.up.railway.app/` (missing `/api/v1`)
- ❌ `https://massar-production.up.railway.app/api/v1/` (trailing slash)
- ❌ `http://massar-production.up.railway.app/api/v1` (http instead of https)

### Step 3: Verify the Variable

1. In Vercel, go to **Settings** → **Environment Variables**
2. Find `VITE_API_BASE_URL`
3. Click on it to see the value
4. It should be EXACTLY: `https://massar-production.up.railway.app/api/v1`
5. Make sure all three environments are checked:
   - ✅ Production
   - ✅ Preview
   - ✅ Development

### Step 4: Delete and Re-add (If Needed)

If the variable is wrong:
1. Delete the existing `VITE_API_BASE_URL` variable
2. Click **Add New**
3. Key: `VITE_API_BASE_URL`
4. Value: `https://massar-production.up.railway.app/api/v1` (copy this exactly)
5. Check all three environments
6. Click **Save**

### Step 5: Redeploy (CRITICAL)

**You MUST redeploy after changing environment variables:**

1. Go to **Deployments** tab
2. Click the three dots (⋯) on the latest deployment
3. Click **Redeploy**
4. Wait for deployment to complete

## Verify It's Working

After redeploy, open your Vercel site and in the browser console (F12), run:

```javascript
console.log('API URL:', import.meta.env.VITE_API_BASE_URL);
```

You should see:
```
https://massar-production.up.railway.app/api/v1
```

If you see:
- `undefined` → Variable not set
- `https://massar-production.up.railway.app/` → Missing `/api/v1`
- `http://localhost:8000/api/v1` → Using fallback (variable not set)

## Quick Test

Visit your Railway backend directly:
- ✅ Should work: `https://massar-production.up.railway.app/api/v1/health`
- ✅ Should work: `https://massar-production.up.railway.app/docs`

If these work, the backend is fine. The issue is the Vercel environment variable.




