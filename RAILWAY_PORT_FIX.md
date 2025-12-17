# Fix for Railway PORT Validation Error

## The Error
```
PORT variable must be integer between 0 and 65535
```

## Solution

Railway automatically sets the `PORT` environment variable. If you're seeing this error, it might be because:

1. **Railway is validating PORT before container starts** - This is a Railway validation issue
2. **PORT variable is not set correctly** - Railway should set this automatically

### Option 1: Check Railway Variables

1. Go to Railway Dashboard → Your Service → **Variables** tab
2. Check if `PORT` is listed (Railway sets this automatically, you shouldn't need to add it)
3. If `PORT` is there and has a non-integer value, delete it and let Railway set it automatically

### Option 2: Manual Fix in Railway Dashboard

1. Go to Railway Dashboard → Your Service → **Settings**
2. Look for **Start Command** or **Deploy** settings
3. If there's a start command with `${PORT:-8000}`, remove it
4. Let Railway use the Dockerfile CMD instead

### Option 3: Verify Dockerfile is Being Used

The Dockerfile uses `CMD ./start.sh` which handles PORT correctly. Make sure:
- Railway is using the Dockerfile (check build logs)
- The `backend/Dockerfile` is being detected
- The `railway.json` points to `backend/Dockerfile`

## Current Configuration

- **Dockerfile CMD**: Uses `./start.sh` which handles PORT validation
- **start.sh**: Converts PORT to integer and validates range
- **railway.json**: No startCommand (uses Dockerfile CMD)

The configuration should work. If the error persists, it's likely a Railway platform issue with PORT validation.

