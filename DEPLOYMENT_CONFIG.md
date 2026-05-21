# Deployment Configuration for LIMS Systems

## Backend CORS Configuration (Render) ✅

### Set these environment variables in Render dashboard:

```env
CORS_ORIGINS=https://lims-systems-dv95.vercel.app,https://lims-system-dv95-205a4ic7p-victor-ndunyus-projects.vercel.app,http://localhost:3000
```

**Steps:**
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select service: **lims-system-vogc**
3. Settings → Environment
4. Update/Add `CORS_ORIGINS` with the value above
5. Service will auto-restart

---

## Frontend Environment Variables (Vercel) ✅

### Set in Vercel dashboard:

```
NEXT_PUBLIC_API_URL=https://lims-system-vogc.onrender.com
```

**Steps:**
1. Go to [Vercel Dashboard](https://vercel.com)
2. Select project: **lims-systems-dv95**
3. Settings → Environment Variables
4. Add/Update `NEXT_PUBLIC_API_URL` = `https://lims-system-vogc.onrender.com`
5. Apply to: Production, Preview, Development
6. Redeploy

---

## Quick Reference

| Service | Domain |
|---------|--------|
| **Backend (Render)** | `https://lims-system-vogc.onrender.com` |
| **Backend API Base** | `https://lims-system-vogc.onrender.com/api` |
| **Frontend Production** | `https://lims-systems-dv95.vercel.app` |
| **Frontend Preview** | `https://lims-system-dv95-205a4ic7p-victor-ndunyus-projects.vercel.app` |
| **Local Dev Backend** | `http://localhost:8000/api` |
| **Local Dev Frontend** | `http://localhost:3000` |

---

## Verification Tests

### Test 1: Backend Health

```bash
curl https://lims-system-vogc.onrender.com/health
```

Expected response:
```json
{"status": "healthy", "environment": "production", "database": "available"}
```

### Test 2: CORS from Frontend

Open browser console on `https://lims-systems-dv95.vercel.app` and run:

```javascript
fetch('https://lims-system-vogc.onrender.com/health')
  .then(r => r.json())
  .then(d => console.log('✅ CORS works:', d))
```

### Test 3: Login Flow

1. Go to `https://lims-systems-dv95.vercel.app/admin`
2. Try to log in
3. Open DevTools → Network tab
4. Verify POST `/api/auth/login` succeeds (no CORS error)

---

## Configuration Complete ✅

All values are now set. See deployment checklists below.
