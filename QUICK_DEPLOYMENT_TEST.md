# Quick Deployment Test Summary

**After environment variables are set in Vercel, run these 5 tests:**

---

## Test 1: App Loads

```
URL: https://lims-systems-dv95.vercel.app
Expected: Page loads, no errors
Status: [ ] PASS / [ ] FAIL
```

**Check:**
- Browser shows content (not blank white page)
- No red error boxes
- DevTools Console: No errors showing

---

## Test 2: No Environment Variable Errors

```
Open: DevTools (F12) → Console tab
Search: "NEXT_PUBLIC_API_URL"
Expected: NOT found (no error message)
Status: [ ] PASS / [ ] FAIL
```

**If FAIL:** Set env var in Vercel dashboard and redeploy

---

## Test 3: API Calls Go to Backend

```
Open: DevTools → Network tab
Filter: XHR (API calls only)
Go to: https://lims-systems-dv95.vercel.app/login

Expected URL shown: https://lims-system-vogc.onrender.com/auth/*
NOT: http://localhost:8000/*
Status: [ ] PASS / [ ] FAIL
```

**If FAIL:** Verify NEXT_PUBLIC_API_URL is set correctly in Vercel

---

## Test 4: Public Pages Load

```
URL: https://lims-systems-dv95.vercel.app/public
Expected: Page loads WITHOUT login required
Status: [ ] PASS / [ ] FAIL

URL: https://lims-systems-dv95.vercel.app/admin
Expected: Redirects to login page
Status: [ ] PASS / [ ] FAIL
```

---

## Test 5: Login Flow

```
1. Go to login page
2. Try login with test credentials
3. Check Network tab for request

Expected: 
- Request URL: https://lims-system-vogc.onrender.com/auth/login
- Response: JSON (200 success or 401 auth error, NOT 404)
- No CORS error in console

Status: [ ] PASS / [ ] FAIL
```

---

## Quick Verdict

| All Tests Pass | Action |
|---|---|
| ✅ YES | **DEPLOYMENT SUCCESSFUL** - No redeploy needed |
| ❌ NO | See which test failed, fix issue, redeploy |

---

## Most Common Issues & Fixes

| Error | Fix | Redeploy? |
|-------|-----|-----------|
| "NEXT_PUBLIC_API_URL not set" | Set in Vercel dashboard | ✅ YES |
| API requests to localhost | Set NEXT_PUBLIC_API_URL | ✅ YES |
| API returns 404 | Backend not running on Render | ❌ NO |
| CORS error | Backend CORS not configured | ❌ NO |
| Page doesn't load | Check Vercel build logs | ✅ YES |

---

**Next:** Follow [DEPLOYMENT_VERIFICATION_CHECKLIST.md](DEPLOYMENT_VERIFICATION_CHECKLIST.md) for detailed verification steps.
