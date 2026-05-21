# Vercel Import Preparation Guide

## Repository Structure

| Item | Value | Details |
|------|-------|---------|
| **Monorepo Type** | Yes | Backend + Frontend in single repo |
| **Frontend Location** | `/frontend` | Root: `field-sample-management/frontend` |
| **Production Branch** | `main` | Only branch currently exists |
| **Framework** | Next.js 16.2.6 | React 18.3.1, TypeScript 5.6.2 |

---

## Vercel Project Configuration

### Quick Settings

| Setting | Value | 
|---------|-------|
| **Root Directory** | `frontend` |
| **Framework Preset** | Next.js |
| **Build Command** | `npm run build` |
| **Output Directory** | `.next` |
| **Install Command** | `npm ci` |
| **Production Branch** | `main` |

### Step-by-Step Import

1. **Connect GitHub Repository**
   - Repo: `field-sample-management`
   - Choose "Monorepo" if asked

2. **Configure Project**
   - Root Directory: `frontend`
   - Framework: Next.js (auto-detect)
   - Build Command: Leave as auto-detected
   - Install Command: Leave as auto-detected

3. **Set Environment Variables** (Required)
   ```
   NEXT_PUBLIC_API_URL = https://lims-system-vogc.onrender.com
   NEXT_PUBLIC_SUPABASE_URL = https://eijdouvaritqyiohautb.supabase.co
   NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY = sb_publicable_EcxIvsfXi_XTknBomt2kYw_DV-Co_sm
   ```
   - **Apply to:** Production, Preview, Development

4. **Deploy**
   - Click "Deploy"
   - Wait for build to complete

---

## Git Branch Strategy

### For This Project

| Branch | Behavior | Notes |
|--------|----------|-------|
| `main` | **Production** | Only production branch; Vercel auto-deploys on push |
| `develop` | Not yet created | Optional: create for staging if needed |
| Feature branches | **Preview** | Auto-create preview on PR if enabled |

### Recommended Setup

- **Production:** `main` (auto-deploy to production URL)
- **Preview:** All pull requests (auto-create preview deployments)
- **Exclude:** None (no branches need exclusion)

### To Enable Preview Deployments

1. Vercel Dashboard → Settings → Git
2. Enable "Preview Deployment for Pull Requests"
3. New PRs will auto-create temporary preview URLs

---

## Environment Variables

### Browser-Safe Variables (NEXT_PUBLIC_)

These are **embedded in the JavaScript bundle** and visible to users. Use only for public data.

| Variable | Value | Purpose | Required |
|----------|-------|---------|----------|
| `NEXT_PUBLIC_API_URL` | `https://lims-system-vogc.onrender.com` | Backend API base URL | ✅ Yes |
| `NEXT_PUBLIC_SUPABASE_URL` | `https://eijdouvaritqyiohautb.supabase.co` | Supabase project endpoint | ✅ Yes |
| `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` | `sb_publishable_EcxIvsfXi_XTknBomt2kYw_DV-Co_sm` | Supabase public key | ✅ Yes |
| `NEXT_PUBLIC_PORTAL_MODE` | `admin` or `public` | Optional: build variant | ❌ No |

### Server-Only Variables

None required for this frontend. All auth is handled client-side via localStorage.

### Development (.env.local)

```env
# Frontend API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://eijdouvaritqyiohautb.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=sb_publishable_EcxIvsfXi_XTknBomt2kYw_DV-Co_sm
```

**Note:** `.env.local` is Git-ignored and never committed.

---

## .env.example Template

Create `frontend/.env.example` for documentation:

```env
# ============================================
# FRONTEND ENVIRONMENT VARIABLES
# ============================================
# This file documents all required environment variables.
# Copy to .env.local and fill in actual values.
# NEVER commit .env.local to Git!

# ============================================
# REQUIRED FOR ALL ENVIRONMENTS
# ============================================

# Backend API base URL
# Development: http://localhost:8000
# Production: https://lims-system-vogc.onrender.com
NEXT_PUBLIC_API_URL=https://lims-system-vogc.onrender.com

# Supabase project URL
NEXT_PUBLIC_SUPABASE_URL=https://eijdouvaritqyiohautb.supabase.co

# Supabase public API key (safe to expose to browser)
# Never use the Supabase secret key in a public environment
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=sb_publishable_EcxIvsfXi_XTknBomt2kYw_DV-Co_sm

# ============================================
# OPTIONAL - PORTAL MODE
# ============================================
# Set to 'admin' or 'public' to build portal-specific variant
# Leave unset for default build (includes all portals)
# NEXT_PUBLIC_PORTAL_MODE=admin

# ============================================
# AUTO-SET BY VERCEL (DO NOT SET MANUALLY)
# ============================================
# NODE_ENV - Set automatically by deployment platform
# - "development" for local dev
# - "production" for Vercel production
```

---

## Deployment Checklist

### Pre-Import ✓

- [x] Repository connected to GitHub
- [x] `frontend/package.json` exists with Next.js 16.2.6
- [x] `frontend/next.config.js` configured
- [x] TypeScript strict mode enabled
- [x] All API calls use centralized configuration
- [x] Environment variable validation implemented
- [x] Production build passes locally

### Import Configuration

- [ ] Vercel project created
- [ ] Root Directory set to `frontend`
- [ ] Framework preset: Next.js (auto-detect)
- [ ] Build Command: `npm run build` (auto-detect)
- [ ] Install Command: `npm ci` (auto-detect)

### Environment Variables

- [ ] `NEXT_PUBLIC_API_URL` = `https://lims-system-vogc.onrender.com`
  - [ ] Applied to Production
  - [ ] Applied to Preview
  - [ ] Applied to Development
- [ ] `NEXT_PUBLIC_SUPABASE_URL` = `https://eijdouvaritqyiohautb.supabase.co`
  - [ ] Applied to all environments
- [ ] `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` = `sb_publishable_EcxIvsfXi_XTknBomt2kYw_DV-Co_sm`
  - [ ] Applied to all environments

### Git Strategy

- [ ] Production branch: `main`
- [ ] Preview deployments: Enabled for pull requests
- [ ] No branches excluded from deployment

### Post-Deploy Verification

- [ ] App loads at production URL
- [ ] Browser console: No "NEXT_PUBLIC_API_URL is not set" errors
- [ ] Admin portal: `/admin`
- [ ] Public portal: `/public`
- [ ] Staff portal: `/staff`
- [ ] Login page loads
- [ ] API calls go to correct backend URL
- [ ] No CORS errors in browser console
- [ ] Authentication works

---

## Quick Import Summary

```
1. Go to vercel.com/dashboard → Add New → Project
2. Select field-sample-management repository
3. Set Root Directory: frontend
4. Add 3 environment variables (see table above)
5. Click Deploy
6. Wait 3-5 minutes for build
7. Verify app loads without errors
```

---

## Troubleshooting

### Build Fails: "No Next.js version detected"
- ✅ **Fix:** Root Directory must be set to `frontend`
- Check: Vercel Settings → Root Directory = `frontend`

### Build Passes but App Doesn't Load
- ✅ **Fix:** Set `NEXT_PUBLIC_API_URL` environment variable
- Check: Vercel Settings → Environment Variables

### API Calls Fail with 404
- ✅ **Fix:** Verify `NEXT_PUBLIC_API_URL` is correct
- Check: Should be `https://lims-system-vogc.onrender.com` (no trailing slash)

### CORS Errors in Browser Console
- ✅ **Fix:** Backend must have CORS configured for Vercel domain
- Check: Backend CORS settings include Vercel production URL

---

## Environment Variable Security

### ⚠️ NEXT_PUBLIC_ Variables ARE Public

**These variables are embedded in JavaScript and visible to anyone:**
- View in browser: `window.__NEXT_DATA__`
- View in Network tab: JavaScript bundles
- View in source code: Check production site

**Safe to expose:**
- API URLs (backend already validates requests)
- Supabase public keys (designed for public exposure)
- Feature flags for UI

**NEVER expose publicly:**
- API secrets/keys
- Database passwords
- Private tokens
- Sensitive configurations

### Current Variables: ✅ All Safe

```
NEXT_PUBLIC_API_URL         → Backend URL (public)
NEXT_PUBLIC_SUPABASE_URL    → Supabase endpoint (public)
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY → Public key (designed for browser)
```

---

## Next Steps

1. **Create Vercel Project**
   - Import from GitHub
   - Configure as described above

2. **Set Environment Variables**
   - In Vercel dashboard
   - Apply to all environments

3. **Deploy**
   - Click Deploy button
   - Monitor build logs

4. **Verify**
   - Check app loads
   - Verify API calls work
   - Monitor browser console

---

**Status: READY FOR VERCEL IMPORT** ✅

All code changes complete. Repository is configured and ready for import into Vercel.
