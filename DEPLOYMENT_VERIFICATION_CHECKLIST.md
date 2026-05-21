# Vercel Frontend Deployment Verification Guide

**Created:** May 21, 2026  
**Purpose:** Verify live Vercel deployment after environment variables are set  
**Status:** Pre-deployment analysis complete

---

## Code Analysis Summary

### ✅ No Hardcoded URLs Found

**Scan Results:**
```
Search: localhost, 127.0.0.1, hardcoded ports
Result: 0 hardcoded references in production code
        2 references in documentation/comments (safe)
```

**Verified Files:**
- ✅ `frontend/src/lib/api-config.ts` - Uses process.env.NEXT_PUBLIC_API_URL only
- ✅ `frontend/src/lib/api.ts` - All API calls use getApiBaseUrl()
- ✅ All page components - Use imported API functions (no direct fetch calls)
- ✅ No remaining Vite patterns (import.meta.env)

---

## Pre-Deployment Checklist

### Environment Variables Set in Vercel

Before proceeding, verify in Vercel Dashboard → Settings → Environment Variables:

- [ ] `NEXT_PUBLIC_API_URL` = `https://lims-system-vogc.onrender.com`
  - [ ] Applied to: Production
  - [ ] Applied to: Preview
  - [ ] Applied to: Development
  
- [ ] `NEXT_PUBLIC_SUPABASE_URL` = `https://eijdouvaritqyiohautb.supabase.co`
  - [ ] Applied to: All environments

- [ ] `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` = `sb_publishable_EcxIvsfXi_XTknBomt2kYw_DV-Co_sm`
  - [ ] Applied to: All environments

### Project Configuration

- [ ] Root Directory: `frontend`
- [ ] Build Command: `npm run build` (auto-detected)
- [ ] Output Directory: `.next` (auto-detected)
- [ ] Production Branch: `main`
- [ ] Framework: Next.js (auto-detected)

---

## Live Deployment Verification

### Step 1: Access the Live URL

**URL:** `https://lims-systems-dv95.vercel.app`

- [ ] Page loads (no white screen)
- [ ] No error messages visible
- [ ] Navigation menu appears
- [ ] Layout renders correctly

### Step 2: Check Browser Console

**Open DevTools:** Press `F12` → Console tab

**✅ Should NOT See:**
- ❌ "NEXT_PUBLIC_API_URL environment variable is not set"
- ❌ "Cannot find module" or import errors
- ❌ Localhost references (http://localhost:8000)
- ❌ Vite environment errors (import.meta)

**✅ Should See (in development only):**
- Log: `[API Config] Using API Base URL: https://lims-system-vogc.onrender.com`

### Step 3: Verify Public Pages Load

**Home Page:** `https://lims-systems-dv95.vercel.app/`
- [ ] Loads without errors
- [ ] Shows "Welcome to LIMS" or hero section
- [ ] No authentication required

**Public Portal:** `https://lims-systems-dv95.vercel.app/public`
- [ ] Loads without login
- [ ] Shows public samples (if available)
- [ ] No authentication errors

**Test Page:** `https://lims-systems-dv95.vercel.app/test`
- [ ] Page loads
- [ ] Displays test content

### Step 4: Verify Protected Pages Require Login

**Admin Portal:** `https://lims-systems-dv95.vercel.app/admin`
- [ ] Redirects to login page (if not authenticated)
- [ ] Shows login form
- [ ] Does NOT display admin content

**Staff Portal:** `https://lims-systems-dv95.vercel.app/staff`
- [ ] Redirects to login page (if not authenticated)
- [ ] Shows login form
- [ ] Does NOT display staff content

### Step 5: Verify API Connectivity

**Test Login:**
1. Go to login page
2. Open DevTools → Network tab
3. Enter test credentials:
   ```
   Email: admin@example.com
   Password: testadmin123
   ```
4. Click "Sign In"

**Check Network Tab:**
- [ ] Request URL: `https://lims-system-vogc.onrender.com/auth/login` (NOT localhost)
- [ ] Status: `200` or `401` (request completed, not 404)
- [ ] Headers: Contains `Content-Type: application/json`
- [ ] Response: JSON with user data or error message

**Expected Outcomes:**
- ✅ **Success:** User logs in, redirected to admin/staff portal
- ✅ **Auth Error:** Shows "Invalid credentials" (API responded)
- ❌ **Failure:** 404 error, CORS error, or timeout

### Step 6: Check for CORS Errors

**In Browser Console:**
- [ ] No "Access to XMLHttpRequest blocked by CORS policy" errors
- [ ] No "No 'Access-Control-Allow-Origin' header" errors
- [ ] API requests show proper `Access-Control-Allow-Origin` headers

**If CORS Error Appears:**
1. Backend CORS not configured for Vercel domain
2. Check: `backend/app/main.py` CORSMiddleware
3. Should include: `https://lims-systems-dv95.vercel.app`
4. Fix: Update backend CORS and redeploy

### Step 7: Check Network Requests

**Open DevTools → Network tab → XHR filter**

**Verify all API calls:**
- ✅ Go to `/api/auth/me` → `https://lims-system-vogc.onrender.com/auth/me`
- ✅ Go to `/api/admin/stats` → `https://lims-system-vogc.onrender.com/admin/stats`
- ✅ Go to `/api/staff/samples` → `https://lims-system-vogc.onrender.com/staff/samples`

**All should:**
- Use HTTPS (not HTTP)
- Go to `lims-system-vogc.onrender.com` (not localhost)
- Return JSON responses (not 404)
- Include `Authorization` header (if authenticated)

---

## Pass/Fail Test Matrix

### Public Access Tests

| Test | Expected | Status | Notes |
|------|----------|--------|-------|
| Home page loads | ✅ Loads | [ ] Pass / [ ] Fail | No auth required |
| Public portal loads | ✅ Loads | [ ] Pass / [ ] Fail | No auth required |
| Console: No missing env var errors | ✅ Clean | [ ] Pass / [ ] Fail | Must not see "NEXT_PUBLIC_API_URL" error |
| No localhost in requests | ✅ All HTTPS | [ ] Pass / [ ] Fail | Network tab shows `lims-system-vogc.onrender.com` |

### Authentication Tests

| Test | Expected | Status | Notes |
|------|----------|--------|-------|
| Admin portal requires login | ✅ Redirects | [ ] Pass / [ ] Fail | Protected route |
| Staff portal requires login | ✅ Redirects | [ ] Pass / [ ] Fail | Protected route |
| Login page loads | ✅ Shows form | [ ] Pass / [ ] Fail | `https://lims-systems-dv95.vercel.app/login` |

### API Connectivity Tests

| Test | Expected | Status | Notes |
|------|----------|--------|-------|
| Login API call succeeds | ✅ 200 or 401 | [ ] Pass / [ ] Fail | Not 404, has response |
| API URL is correct | ✅ `lims-system-vogc.onrender.com` | [ ] Pass / [ ] Fail | No localhost |
| No CORS errors | ✅ Clean console | [ ] Pass / [ ] Fail | No CORS blocked messages |
| Auth header sent | ✅ `Authorization: Bearer ...` | [ ] Pass / [ ] Fail | After login, requests have token |

### Build Configuration Tests

| Test | Expected | Status | Notes |
|------|----------|--------|-------|
| TypeScript compilation | ✅ No errors | [ ] Pass / [ ] Fail | Vercel build logs show success |
| All pages generated | ✅ 14 routes | [ ] Pass / [ ] Fail | Admin, public, staff, login, etc. |
| `.next` directory created | ✅ Present | [ ] Pass / [ ] Fail | Production build output |
| Environment vars embedded | ✅ In bundle | [ ] Pass / [ ] Fail | Check Network tab → JS file |

---

## Troubleshooting Guide

### Issue: "NEXT_PUBLIC_API_URL is not set" Error

**Cause:** Environment variable not set in Vercel dashboard  
**Fix:**
1. Vercel Dashboard → Settings → Environment Variables
2. Add `NEXT_PUBLIC_API_URL` = `https://lims-system-vogc.onrender.com`
3. Apply to Production, Preview, Development
4. Redeploy

### Issue: API Calls Return 404

**Cause 1:** NEXT_PUBLIC_API_URL pointing to wrong backend  
**Fix:** Verify value is exactly `https://lims-system-vogc.onrender.com` (no trailing slash)

**Cause 2:** Backend not running on Render  
**Fix:** Check Render dashboard that `lims-system-vogc` service is running

**Verification:**
```bash
# From any terminal, test backend directly:
curl https://lims-system-vogc.onrender.com/health
# Should return: {"status":"ok"} or similar JSON
```

### Issue: CORS Errors

**Error:** `Access to XMLHttpRequest blocked by CORS policy`

**Cause:** Backend CORS not configured for Vercel domain  
**Fix:**
1. Check `backend/app/main.py` CORSMiddleware
2. Verify it includes `https://lims-systems-dv95.vercel.app`
3. Redeploy backend to Render

**Verify CORS is working:**
```bash
# Test CORS headers from browser console:
fetch('https://lims-system-vogc.onrender.com/health', {
  credentials: 'include',
  headers: { 'Content-Type': 'application/json' }
}).then(r => r.json()).then(console.log)
# Should work without CORS error
```

### Issue: Login Fails with Validation Error

**Likely:** Authentication working correctly (API responded)  
**Next:** Use correct test credentials for your backend

**Check available users:**
```bash
# Verify admin user exists in database:
# Backend logs or database query
```

### Issue: All API Calls Fail

**Check:**
1. Is backend running? `curl https://lims-system-vogc.onrender.com/health`
2. Is frontend on correct URL? Check browser address bar
3. Are environment variables set? Check browser DevTools

---

## Deployment Status Decision Tree

```
Does app load?
├─ YES → Frontend build successful ✅
│  └─ Do public pages load?
│     ├─ YES ✅ → Go to API test
│     └─ NO ❌ → Check TypeScript errors in Vercel logs
│
├─ NO → Frontend build failed
│  └─ Check Vercel build logs for errors
│     └─ Run: npm run build locally to debug
│
API connectivity test:
├─ Requests go to backend? (Network tab)
│  ├─ YES, backend URL correct ✅
│  │  └─ Is backend responding?
│  │     ├─ YES ✅ → DEPLOYMENT SUCCESSFUL
│  │     └─ NO ❌ → Check backend on Render
│  │
│  └─ NO, requests to localhost ❌
│     └─ NEXT_PUBLIC_API_URL not set properly
│        └─ Redeploy with env vars
```

---

## Redeploy Decision Matrix

| Scenario | Redeploy Needed | Action |
|----------|-----------------|--------|
| Env vars not set | ✅ YES | Set in dashboard, redeploy |
| Requests to localhost | ✅ YES | Verify env vars, rebuild |
| API returns 404 | ❌ NO (backend issue) | Check backend on Render |
| CORS errors | ❌ NO (backend CORS) | Fix backend CORS config |
| Page not loading | ✅ YES | Check build logs, rebuild |
| Login works | ❌ NO (working correctly) | Use correct credentials |

---

## Final Checklist

### Before Declaring Success

- [ ] Home page loads without errors
- [ ] Browser console: No missing env var errors
- [ ] Network tab: All API requests go to `https://lims-system-vogc.onrender.com`
- [ ] Protected pages require login (redirect works)
- [ ] Login page shows
- [ ] No CORS errors in console
- [ ] API calls return responses (200 or auth error, not 404)

### If Any Fail

1. **Check environment variables in Vercel**
   - All 3 required vars set?
   - Applied to correct environments?

2. **Check Vercel build logs**
   - Compilation succeeded?
   - Routes generated?
   - Any TypeScript errors?

3. **Check backend on Render**
   - Service running?
   - Health check responds?
   - CORS configured?

4. **Redeploy if needed**
   - Vercel: Push commit or click Redeploy
   - Render: Check service status, restart if needed

---

## Success Criteria

✅ **DEPLOYMENT SUCCESS** when:
- App loads at `https://lims-systems-dv95.vercel.app`
- No "NEXT_PUBLIC_API_URL" errors in console
- API requests go to `https://lims-system-vogc.onrender.com`
- Public pages load without login
- Protected pages require authentication
- No CORS errors
- Login form works (may fail with credentials, but no 404)

---

**Use this guide to verify deployment after Vercel environment variables are set.**
