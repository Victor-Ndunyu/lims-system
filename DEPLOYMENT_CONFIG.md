# Deployment Configuration for LIMS Systems

## Backend CORS Configuration (Render)

### Set these environment variables in Render dashboard:

```env
CORS_ORIGINS=https://lims-systems-dv95.vercel.app,https://lims-system-dv95-205a4ic7p-victor-ndunyus-projects.vercel.app,http://localhost:3000
```

**Steps:**
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select your API service
3. Settings → Environment
4. Update `CORS_ORIGINS` with the value above
5. Service will auto-restart

---

## Frontend Environment Variables (Vercel)

### Set in Vercel dashboard:

**You need your backend URL from Render.** 

If your Render service is deployed at: `https://field-sample-api.onrender.com`

Then set in Vercel:

```
NEXT_PUBLIC_API_URL=https://field-sample-api.onrender.com/api
```

### Steps:
1. Go to [Vercel Dashboard](https://vercel.com)
2. Select project: **lims-systems-dv95**
3. Settings → Environment Variables
4. Add/Update `NEXT_PUBLIC_API_URL` = `https://YOUR-RENDER-URL.onrender.com/api`
5. Apply to: Production, Preview, Development
6. Redeploy

---

## Quick Reference

| Service | Domain |
|---------|--------|
| **Backend (Render)** | `https://YOUR-RENDER-URL.onrender.com` |
| **Frontend Production** | `https://lims-systems-dv95.vercel.app` |
| **Frontend Preview** | `https://lims-system-dv95-205a4ic7p-victor-ndunyus-projects.vercel.app` |
| **Local Dev** | `http://localhost:3000` and `http://localhost:8000/api` |

---

## CORS Verification

After setting both configs, test from browser console:

```javascript
// Test backend health and CORS
fetch('https://YOUR-RENDER-URL.onrender.com/health')
  .then(r => r.json())
  .then(d => console.log('Backend healthy:', d))
```

---

## What I Need From You

**What is your Render backend URL?**

Once you provide it, I'll:
1. ✅ Update backend/.env.example with exact CORS values
2. ✅ Update frontend/.env.example with exact API URL
3. ✅ Create final deployment verification script
4. ✅ Commit to git

**Format:** `https://YOUR-SERVICE-NAME.onrender.com` or `https://YOUR-CUSTOM-DOMAIN.com`

---

**Vercel domains are configured in CORS above. Just waiting for your Render URL!**
