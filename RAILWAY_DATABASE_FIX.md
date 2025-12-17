# Fix for Railway DATABASE_URL Error

## The Error
```
sqlalchemy.exc.ArgumentError: Could not parse rfc1738 URL from string ''
```

This means `DATABASE_URL` is set to an empty string in Railway.

## Solution

### Option 1: Remove DATABASE_URL from Railway (Recommended)

Railway might have `DATABASE_URL` set to an empty string. The code now handles this automatically and will use SQLite.

1. Go to Railway Dashboard → Your Service → **Variables** tab
2. Look for `DATABASE_URL`
3. If it exists and is empty or set to an empty string, **delete it**
4. Railway will automatically redeploy
5. The app will use the default SQLite database at `./data/db.sqlite`

### Option 2: Set DATABASE_URL Correctly (If Using PostgreSQL)

If you want to use PostgreSQL instead of SQLite:

1. Go to Railway Dashboard → Your Service → **Variables** tab
2. Add or update `DATABASE_URL`:
   - **Name**: `DATABASE_URL`
   - **Value**: Your PostgreSQL connection string (Railway provides this if you add a PostgreSQL service)
   - Example: `postgresql://user:password@host:port/dbname`

### Current Fix

The code has been updated to:
- Check if `DATABASE_URL` is empty or not set
- Automatically use SQLite (`sqlite:///./data/db.sqlite`) if empty
- Create the `data` directory if it doesn't exist

## Verify

After Railway redeploys, check the logs. You should see:
- No database connection errors
- Server starting successfully
- Model loading correctly

