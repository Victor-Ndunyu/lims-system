# Backend Deployment Guide

## Overview

The Field Sample Management backend is configured for production deployment on **Render** with automatic database migrations and health monitoring.

## Pre-Deployment Checklist

### 1. Generate Production Secrets

Generate a new, cryptographically secure SECRET_KEY:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Prepare Environment Variables

You'll need to set these in Render's environment variables dashboard:

| Variable | Value | Example |
|----------|-------|---------|
| `ENVIRONMENT` | `production` | production |
| `DATABASE_URL` | Supabase PostgreSQL connection string | `postgresql+psycopg://user:password@host:port/db?sslmode=require` |
| `SECRET_KEY` | Generated secret key (64+ characters) | From step 1 above |
| `CORS_ORIGINS` | Your frontend domain(s), comma-separated | `https://samples.example.com,https://admin.samples.example.com` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Session timeout in minutes (optional) | `60` |
| `PYTHON_VERSION` | Python version | `3.12.7` (already set) |

### 3. Database Connection String Format

For Supabase PostgreSQL (recommended):

```
postgresql+psycopg://postgres.PROJECT_ID:PASSWORD@aws-0-REGION.pooler.supabase.com:5432/postgres?sslmode=require
```

**To find your connection string:**
1. Go to Supabase Dashboard → Project Settings
2. Under "Database", copy the connection string
3. Replace `[YOUR-PASSWORD]` with your actual password
4. Ensure URL includes `?sslmode=require` at the end

---

## Deployment Steps

### Step 1: Connect Render to Git Repository

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Create new **Web Service**
3. Connect your GitHub repository
4. Select the repository and choose main branch

### Step 2: Configure Build & Start Commands

**Already configured in `render.yaml`:**

- **Build Command:** `pip install -r requirements.txt`
- **Pre-Deploy Command:** `python -m alembic upgrade head` (runs migrations automatically)
- **Start Command:** `./scripts/start.sh`

These are automatically applied from the `render.yaml` file.

### Step 3: Set Environment Variables

In Render dashboard, set the following environment variables:

```
ENVIRONMENT=production
DATABASE_URL=postgresql+psycopg://[your-connection-string-with-password]
SECRET_KEY=[your-generated-secret-key]
CORS_ORIGINS=https://yourdomain.com,https://admin.yourdomain.com
```

**Security Note:** Keep `DATABASE_URL` and `SECRET_KEY` secret. Never commit these to git.

### Step 4: Deploy

1. Click **Deploy** in Render dashboard
2. Monitor logs for any errors
3. Verify health endpoints after deployment

---

## Post-Deployment Verification

### 1. Check Health Endpoints

After deployment completes, verify the API is running:

```bash
# Basic health check
curl https://your-render-app.onrender.com/healthz

# Full health check with database verification
curl https://your-render-app.onrender.com/health
```

**Expected responses:**

```json
# /healthz
{"status": "ok", "environment": "production"}

# /health
{"status": "healthy", "environment": "production", "database": "available"}
```

### 2. Verify Database Connection

Check Render logs to confirm migrations ran successfully:

```bash
# Look for output like:
# "Running migrations..."
# "Done with alembic upgrade head"
```

### 3. Check CORS Configuration

Test from your frontend domain:

```bash
curl -H "Origin: https://yourdomain.com" \
     -H "Access-Control-Request-Method: POST" \
     https://your-render-app.onrender.com/api/auth/login
```

Should include `Access-Control-Allow-Origin: https://yourdomain.com` in response headers.

---

## Troubleshooting

### Issue: "DATABASE_URL is required"

**Solution:** Verify the environment variable is set in Render dashboard:
1. Go to your service in Render
2. Settings → Environment
3. Check `DATABASE_URL` is present and not empty

### Issue: "Connection refused" or "Cannot connect to database"

**Solution:** Check your Supabase connection string:
1. Verify URL format: `postgresql+psycopg://[user]:[password]@[host]:[port]/[database]?sslmode=require`
2. Verify credentials are correct
3. Check Supabase firewall allows Render IP (usually automatic)

### Issue: "401 Unauthorized" on API calls

**Solution:** Verify `SECRET_KEY` is set and matches in production:
1. Check environment variable exists in Render
2. Regenerate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`
3. Update Render environment and redeploy

### Issue: CORS errors in browser

**Solution:** Update `CORS_ORIGINS`:
1. Go to Render environment variables
2. Update `CORS_ORIGINS` to include your frontend domain
3. Trigger redeploy to restart server

### Issue: Migrations fail on deploy

**Solution:** Check pre-deploy logs:
1. Click **Logs** in Render service dashboard
2. Look for migration errors
3. Verify database schema is valid
4. Manually run locally: `python -m alembic upgrade head`

---

## Useful Commands for Local Testing

### Test Build Locally

```bash
cd backend
pip install -r requirements.txt
```

### Test Start Script

```bash
# Set PORT manually
export PORT=8000
./scripts/start.sh

# Or on Windows PowerShell:
$env:PORT=8000; ./scripts/start.sh
```

### Run Migrations Locally

```bash
# Requires valid DATABASE_URL in .env
python -m alembic upgrade head
```

### Seed Database (Creates admin users, roles, permissions)

```bash
# Optional: pre-populate database with default roles and permissions
python -m app.db.seed
```

### Validate Database Connection

```bash
python -m app.db.validate
```

---

## Production Security Checklist

- [ ] `SECRET_KEY` changed from default dev key
- [ ] `DATABASE_URL` uses strong password
- [ ] `DATABASE_URL` not committed to git (verify .gitignore has `backend/.env`)
- [ ] `CORS_ORIGINS` updated to actual production domain(s)
- [ ] HTTPS enabled for all API calls
- [ ] Database backups configured in Supabase
- [ ] Logs monitored for errors (Render dashboard → Logs)
- [ ] Health endpoints tested and working
- [ ] ENVIRONMENT set to `production`

---

## Scaling & Monitoring

### Monitor in Render Dashboard

- **Metrics:** CPU, Memory, Build time
- **Logs:** Real-time application logs
- **Health:** Automatic health checks via `/health` endpoint

### Auto-Recovery

Render automatically restarts the service if:
- Process crashes (non-zero exit code)
- Health check fails (if configured)

### Manual Restart

If needed, click **Restart Service** in Render dashboard.

---

## Continuous Deployment

Every git push to `main` branch will:

1. Trigger a new build
2. Install dependencies via `pip install -r requirements.txt`
3. Run migrations via `python -m alembic upgrade head`
4. Start the service via `./scripts/start.sh`

To disable auto-deploy, toggle **Auto-Deploy** in Render service settings.

---

## Support Resources

- [Render Documentation](https://render.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Supabase Connection Strings](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [Alembic Migration Guide](https://alembic.sqlalchemy.org)

---

**Last Updated:** May 20, 2026
