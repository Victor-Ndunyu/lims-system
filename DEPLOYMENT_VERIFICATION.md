# LIMS System Deployment Verification Checklist

**Project:** LIMS Systems  
**Vercel:** lims-systems-dv95  
**Render:** lims-system-vogc  
**Date:** May 21, 2026

---

## ✅ Backend (Render) Configuration

### Environment Variables to Set

**Service:** lims-system-vogc  
**Location:** Render Dashboard → Settings → Environment

```
ENVIRONMENT=production
DATABASE_URL=postgresql+psycopg://[supabase-connection-string]
SECRET_KEY=[64-char-generated-key]
CORS_ORIGINS=https://lims-systems-dv95.vercel.app,https://lims-system-dv95-205a4ic7p-victor-ndunyus-projects.vercel.app,http://localhost:3000
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

**Steps:**
- [ ] Open [Render Dashboard](https://dashboard.render.com)
- [ ] Go to service: lims-system-vogc
- [ ] Settings → Environment Variables
- [ ] Update each variable
- [ ] Service auto-restarts

---

## ✅ Frontend (Vercel) Configuration

### Environment Variables to Set

**Project:** lims-systems-dv95  
**Location:** Vercel Dashboard → Settings → Environment Variables

```
NEXT_PUBLIC_API_URL=https://lims-system-vogc.onrender.com
NEXT_PUBLIC_SUPABASE_URL=https://eijdouvaritqyiohautb.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=sb_publishable_xxxxx
```

**Steps:**
- [ ] Open [Vercel Dashboard](https://vercel.com)
- [ ] Select project: lims-systems-dv95
- [ ] Settings → Environment Variables
- [ ] Add/Update each variable
- [ ] Apply to: Production, Preview, Development
- [ ] Trigger redeploy

---

## 🧪 Post-Deployment Verification

### Test 1: Backend Health (5 min)

```bash
curl https://lims-system-vogc.onrender.com/health
```

**Expected:**
```json
{"status": "healthy", "environment": "production", "database": "available"}
```

- [ ] Backend responds with healthy status
- [ ] Database connection confirmed

### Test 2: CORS from Frontend (5 min)

**Open browser console on Vercel frontend:**

```javascript
fetch('https://lims-system-vogc.onrender.com/health')
  .then(r => r.json())
  .then(d => console.log('✅ CORS works:', d))
  .catch(e => console.error('❌ CORS error:', e))
```

- [ ] No CORS error in console
- [ ] Response shows database available

### Test 3: Frontend Loads (2 min)

```
https://lims-systems-dv95.vercel.app
```

- [ ] Page loads without errors
- [ ] Admin portal accessible
- [ ] Staff portal accessible
- [ ] Public portal accessible

### Test 4: Login Flow (10 min)

**At https://lims-systems-dv95.vercel.app/admin:**

1. Open DevTools → Network tab
2. Enter test credentials
3. Click Login

**Verification:**
- [ ] POST `/api/auth/login` succeeds
- [ ] No CORS errors
- [ ] Status: 200 OK
- [ ] Response includes access token
- [ ] Redirects to admin dashboard

### Test 5: API Calls (5 min)

**In browser console on admin dashboard:**

```javascript
// Check if API calls work
fetch('https://lims-system-vogc.onrender.com/api/admin/stats', {
  headers: {'Authorization': `Bearer ${localStorage.getItem('access_token')}`}
}).then(r => r.json()).then(console.log)
```

- [ ] API call succeeds
- [ ] No 401/403 errors
- [ ] Data returns correctly

---

## 📋 Configuration Summary

| Variable | Value |
|----------|-------|
| **Backend URL** | `https://lims-system-vogc.onrender.com` |
| **API Base** | `https://lims-system-vogc.onrender.com/api` |
| **Frontend Prod** | `https://lims-systems-dv95.vercel.app` |
| **Frontend Preview** | `https://lims-system-dv95-205a4ic7p-victor-ndunyus-projects.vercel.app` |
| **CORS Allowed** | All Vercel domains + localhost:3000 |
| **Auth** | Bearer token in Authorization header |
| **Session** | 1440 minutes (24 hours) |

---

## 🐛 Troubleshooting

### "Cannot connect to backend"
- [ ] Check backend health: `curl https://lims-system-vogc.onrender.com/health`
- [ ] Verify `NEXT_PUBLIC_API_URL` is set in Vercel
- [ ] Check Render logs for errors

### "CORS error: Access blocked"
- [ ] Verify Vercel domain in backend `CORS_ORIGINS`
- [ ] Check exact domain (production vs preview)
- [ ] Verify `allow_credentials=true` in CORS config

### "401 Unauthorized on login"
- [ ] Check if database connection works: `curl https://lims-system-vogc.onrender.com/health`
- [ ] Verify credentials are correct
- [ ] Check Render logs for auth errors

### "Frontend shows API as /api"
- [ ] Verify `NEXT_PUBLIC_API_URL` is set in Vercel environment
- [ ] Trigger new deploy
- [ ] Check build logs for environment variable

---

## 📞 Support

**Documentation:**
- [Backend Deployment Guide](./backend/DEPLOYMENT.md)
- [Frontend Vercel Guide](./frontend/VERCEL_DEPLOYMENT.md)
- [CORS Configuration](./backend/CORS_CONFIGURATION.md)
- [Environment Variables Reference](./backend/ENV_VARIABLES.md)

**Useful Links:**
- [Render Dashboard](https://dashboard.render.com)
- [Vercel Dashboard](https://vercel.com)
- [Supabase Dashboard](https://app.supabase.com)

---

## ✅ Deployment Complete

Once all verification tests pass, your system is fully deployed and production-ready:

- ✅ Backend running on Render
- ✅ Frontend deployed on Vercel
- ✅ Database connected to Supabase
- ✅ CORS configured
- ✅ Authentication working
- ✅ API calls functional

**System is live!**
