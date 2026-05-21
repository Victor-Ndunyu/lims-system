# Frontend Vercel Deployment Guide

## Environment Variable Configuration

### ✅ Exact Variable Name and Value

**Set in Vercel dashboard:**

| Variable | Value | Example |
|----------|-------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `https://api.example.com` |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL | `https://your-project.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` | Supabase public key | `sb_publishable_...` |

### Setup in Vercel Dashboard

1. **Go to:** Project Settings → Environment Variables
2. **Add variable:** `NEXT_PUBLIC_API_URL`
3. **Value:** `https://api.example.com` (or your actual backend URL)
4. **Apply to:** Production, Preview, Development
5. **Save and redeploy**

---

## Confirming Configuration

### ✅ App Reads NEXT_PUBLIC_API_URL Correctly

**How it works:**
```typescript
// frontend/src/lib/api-config.ts
export function getApiBaseUrl(): string {
  // Checks process.env.NEXT_PUBLIC_API_URL (set by Vercel)
  if (typeof process !== "undefined" && process.env?.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  return "/api";  // Fallback to relative URL
}
```

**Verification:**
```bash
# During build, Vercel logs the environment variables:
# ✓ NEXT_PUBLIC_API_URL=https://api.example.com
# ✓ NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
```

### ✅ No Localhost Calls in Production

**Confirmed:**
- ✅ All hardcoded `http://localhost:8000` removed
- ✅ All `localhost` references use `getApiBaseUrl()`
- ✅ Fallback is `/api` (relative URL, works with same-origin proxy)
- ✅ Production builds use `NEXT_PUBLIC_API_URL` from environment

**Files updated:**
- `frontend/src/lib/api-config.ts` - Central configuration
- `frontend/src/lib/api.ts` - All 16 API calls use `getApiBaseUrl()`

---

## Vercel Build Process

### What Happens at Build Time

1. **Vercel reads** `NEXT_PUBLIC_API_URL` from environment variables
2. **Builds the app** with the value embedded in JavaScript (because of `NEXT_PUBLIC_` prefix)
3. **Static compilation** - the URL is baked into the bundle at build time
4. **No runtime lookup** - the value is fixed for that deployment

### Build Output

```bash
# Vercel build log:
> next build
  ✓ Compiled successfully
  ✓ Created optimized production build
  ✓ Precompressed .next/static files (1.2 MB gzip)
  
# Your .env value is embedded:
# src/lib/api-config.ts → "https://api.example.com"
```

---

## Do You Need Extra Variables for Public Client Use?

### ✅ Current Setup is Complete

You already have everything needed:

```typescript
// Public/unauthenticated requests
export async function fetchPublicSamples() {
  return publicRequest(API_ENDPOINTS.PUBLIC_SAMPLES);
}

// Authenticated requests
export async function fetchAdminStats() {
  return request(API_ENDPOINTS.ADMIN_STATS);
}
```

Both use the same `NEXT_PUBLIC_API_URL` (one API base for everything).

### No Extra Variables Needed If:
- ✅ Backend serves both public and authenticated endpoints from same URL
- ✅ Public endpoints don't require authentication
- ✅ CORS allows the frontend origin

### Additional Variables Only If:
- You have a separate public API at a different domain
- You need feature flags or A/B testing
- You want environment-specific behavior

---

## Vercel Deployment Checklist

### ✅ Pre-Deployment

- [ ] Backend deployed to Render (or other platform)
- [ ] Backend API URL is live and healthy
- [ ] CORS configured on backend to include Vercel domain
- [ ] `NEXT_PUBLIC_API_URL` determined (ask: what is your backend URL?)
- [ ] `NEXT_PUBLIC_SUPABASE_URL` and key ready
- [ ] Local `.env.local` NOT committed to git (verify .gitignore)

### ✅ Vercel Setup

- [ ] Vercel account created and project connected
- [ ] Repository authorization granted
- [ ] Production branch set to `main`

### ✅ Environment Variables in Vercel Dashboard

1. **Go to:** Project Settings → Environment Variables
2. **Add these variables** (All Environments):

```
NEXT_PUBLIC_API_URL=https://api.example.com
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=sb_publishable_xxxxx
```

- [ ] All three variables added
- [ ] Applied to: Production, Preview, Development
- [ ] Saved

### ✅ Build & Deploy

- [ ] Trigger deploy (manual or auto on git push)
- [ ] Wait for build to complete (~2-3 minutes)
- [ ] Verify no build errors in logs

### ✅ Post-Deployment Verification

```bash
# Test 1: Check if frontend loads
curl https://myapp.vercel.app/

# Test 2: Check if API config is correct
# (Open browser DevTools Console and run:)
console.log(window.__NEXT_DATA__.buildId)  # Confirms build

# Test 3: Try login
# 1. Open https://myapp.vercel.app/admin (or /staff, /public)
# 2. Open DevTools → Network tab
# 3. Try to log in
# 4. Verify POST /api/auth/login succeeds (no CORS error)
```

### ✅ Monitoring

- [ ] Set up Vercel analytics (optional)
- [ ] Enable error tracking
- [ ] Test health endpoint from frontend:

```javascript
// In browser console:
fetch('https://myapp.vercel.app/api/health')
  .then(r => r.json())
  .then(console.log)

// Should return:
// {status: "healthy", environment: "production", database: "available"}
```

---

## Environment Variables by Deployment Type

### Local Development
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Vercel Preview (PR Deployments)
```env
NEXT_PUBLIC_API_URL=https://api.example.com
```

### Vercel Production
```env
NEXT_PUBLIC_API_URL=https://api.example.com
```

**All use the same backend API.** Difference is the frontend domain.

---

## Troubleshooting

### Issue: "Cannot GET /api/health"

**Cause:** `NEXT_PUBLIC_API_URL` not set or incorrect  
**Solution:** 
1. Check Vercel dashboard for environment variable
2. Verify exact URL is correct (no trailing slash)
3. Trigger new deploy

### Issue: CORS errors in browser

**Cause:** Backend CORS not configured for Vercel domain  
**Solution:**
1. Get your Vercel URL (check Vercel dashboard)
2. Add to backend `CORS_ORIGINS` environment variable
3. Backend will need restart/redeploy

### Issue: API calls return 401 Unauthorized

**Cause:** Token not being sent in headers  
**Solution:** Already handled - `src/lib/api.ts` sends Bearer token from localStorage

### Issue: Build passes but app shows API URL error

**Cause:** `NEXT_PUBLIC_` prefix missing from variable name  
**Solution:** Must be exactly: `NEXT_PUBLIC_API_URL` (not `NEXT_API_URL` or `API_URL`)

---

## Advanced: Separate Domains (Admin vs Public)

If you later want separate frontends for admin and public:

**Admin Frontend**
```env
NEXT_PUBLIC_PORTAL_MODE=admin
NEXT_PUBLIC_API_URL=https://api.example.com
```

**Public Frontend**
```env
NEXT_PUBLIC_PORTAL_MODE=public
NEXT_PUBLIC_API_URL=https://api.example.com
```

Both use same backend API (routes are role-based on backend).

---

## Quick Deployment Command

If deploying from command line:

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy with environment variables
vercel --prod \
  --env NEXT_PUBLIC_API_URL=https://api.example.com \
  --env NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co \
  --env NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=sb_publishable_xxxxx
```

---

## What Gets Built Into the Bundle

**Embedded in JavaScript** (because of `NEXT_PUBLIC_` prefix):
```javascript
// In browser, this is visible:
window.__NEXT_DATA__.buildId
window.__NEXT_DATA__.runtimeConfig.publicRuntimeConfig.NEXT_PUBLIC_API_URL
```

**NOT embedded** (backend secrets):
- Database credentials
- API signing keys
- Admin passwords

---

## Related Documentation

- [Backend Deployment Guide](./backend/DEPLOYMENT.md)
- [CORS Configuration](./backend/CORS_CONFIGURATION.md)
- [Environment Variables Reference](./backend/ENV_VARIABLES.md)
- [API Configuration Module](./frontend/src/lib/api-config.ts)

---

**Ready to deploy? [Open Vercel Dashboard](https://vercel.com)**
