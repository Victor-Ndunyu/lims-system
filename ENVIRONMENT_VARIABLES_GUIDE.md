## ENVIRONMENT VARIABLES AUDIT & DEPLOYMENT GUIDE

### OVERVIEW
```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (Next.js)                     │
│              Deployed to: Vercel                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
            API Calls via process.env.NEXT_PUBLIC_API_URL
                    (https://backend.onrender.com)
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                      │
│              Deployed to: Render                            │
│          Database: Supabase PostgreSQL                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. VERCEL FRONTEND ENVIRONMENT VARIABLES

These go in: **Vercel Dashboard → Settings → Environment Variables**

Apply to: **Production, Preview, Development**

```
NAME:                       NEXT_PUBLIC_API_URL
VALUE:                      https://lims-system-vogc.onrender.com
TYPE:                       Plain text (public)
REQUIRED:                   ✅ YES - App will error in production without it
PURPOSE:                    Backend API base URL
SECURITY:                   🟢 Safe to expose (no credentials)
DEV VALUE:                  http://localhost:8000
PRODUCTION VALUE:           https://lims-system-vogc.onrender.com
```

**Note:** Supabase public variables (NEXT_PUBLIC_SUPABASE_*) are currently configured but NOT ACTIVELY USED since all data access goes through backend API. They can remain for legacy compatibility but are not required.

---

## 2. RENDER BACKEND ENVIRONMENT VARIABLES

These go in: **Render Dashboard → Environment → lims-system-vogc**

```
NAME:                       DATABASE_URL
TYPE:                       Private environment variable
REQUIRED:                   ✅ YES - App will not start without it
VALUE (from Supabase):      postgresql+psycopg://postgres.PROJECT_REF:PASSWORD@aws-0-eu-west-1.pooler.supabase.com:5432/postgres?sslmode=require
SECURITY:                   🔴 HIGHLY SENSITIVE - Never expose to frontend
SOURCE:                     Supabase Dashboard → Settings → Database → Connection String (Pooler)
```

```
NAME:                       SECRET_KEY
TYPE:                       Private environment variable
REQUIRED:                   ✅ YES - App will not start without it
VALUE:                      (Generate: python -c "import secrets; print(secrets.token_urlsafe(32))")
SECURITY:                   🔴 HIGHLY SENSITIVE - Never expose to frontend
PURPOSE:                    JWT token signing key for authentication
ROTATION:                   Change annually or after security audit
CURRENT VALUE:              [Stored in Render only - never commit to git]
```

```
NAME:                       CORS_ORIGINS
TYPE:                       Plain text
REQUIRED:                   ✅ YES - Controls which domains can call the API
VALUE:                      https://lims-system-neon.vercel.app,http://localhost:3000
FORMAT:                     Comma-separated, no trailing slashes
SECURITY:                   🟡 Sensitive - Whitelist only trusted domains
PRODUCTION VALUE:           https://lims-system-neon.vercel.app
DEVELOPMENT VALUE:          http://localhost:3000
PREVIEW VALUE:              https://lims-system-neon-*.vercel.app (add if using preview deployments)
```

```
NAME:                       ENVIRONMENT
TYPE:                       Plain text
REQUIRED:                   ⚪ Optional (default: "development")
VALUE:                      production
OPTIONS:                    development, staging, production
PURPOSE:                    Controls logging verbosity and error detail exposure
```

```
NAME:                       ACCESS_TOKEN_EXPIRE_MINUTES
TYPE:                       Plain text
REQUIRED:                   ⚪ Optional (default: 60)
VALUE:                      1440
PURPOSE:                    JWT token lifetime (1440 = 24 hours)
SECURITY:                   Balances security vs convenience
```

**Optional (for initial setup only):**
```
NAME:                       FIRST_ADMIN_EMAIL
VALUE:                      vndunyu@gmail.com
REQUIRED:                   ⚪ Only needed to run seed script once
```

```
NAME:                       FIRST_ADMIN_PASSWORD
VALUE:                      Animalhealth123
REQUIRED:                   ⚪ Only needed to run seed script once
SECURITY:                   🔴 Should be changed immediately after first login
```

```
NAME:                       FIRST_ADMIN_FULL_NAME
VALUE:                      Victor Ndunyu
REQUIRED:                   ⚪ Optional
```

---

## 3. SUPABASE PUBLIC VARIABLES

Source: **Supabase Dashboard → Settings → API**

These are **safe to expose** in the frontend and are read-only public credentials.

**Currently used by:** Frontend Supabase utilities (auth middleware, optional - not actively used)

```
NEXT_PUBLIC_SUPABASE_URL
URL:                        https://eijdouvaritqyiohautb.supabase.co
SECURITY:                   🟢 Public - Safe to expose
SOURCE:                     Supabase Dashboard → Settings → API → URL
PURPOSE:                    Supabase project endpoint (used by legacy auth code)
```

```
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY
VALUE:                      sb_publishable_EcxIvsfXi_XTknBomt2kYw_DV-Co_sm
SECURITY:                   🟢 Public - Safe to expose
SOURCE:                     Supabase Dashboard → Settings → API → Publishable Key
PURPOSE:                    Read-only Supabase API key
SCOPE:                      JWT generation, session management only
```

---

## 4. SUPABASE PRIVATE VARIABLES (BACKEND ONLY)

⚠️ **NEVER EXPOSE TO FRONTEND**

```
SUPABASE_SERVICE_ROLE_KEY
SECURITY:                   🔴 HIGHLY SENSITIVE
SCOPE:                      Full database admin access - backend only
CURRENT STATUS:             Not used (would be for admin operations)
IF NEEDED:                  Available at Supabase Dashboard → Settings → API
```

---

## 5. CURRENT ARCHITECTURE

### Frontend API Usage
✅ **CENTRALIZED** - All API calls go through:
- `frontend/src/lib/api-config.ts` - Configuration & endpoints
- `frontend/src/lib/api.ts` - HTTP client with auth

### Environment Variables in Frontend
- ✅ `NEXT_PUBLIC_API_URL` - Backend URL (REQUIRED)
- ✅ `NEXT_PUBLIC_SUPABASE_URL` - Optional, not actively used
- ✅ `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` - Optional, not actively used
- ❌ No hardcoded localhost URLs
- ❌ No backend secrets
- ❌ No service-role keys

### Backend API Endpoints
All under `/api/` prefix:
- `/api/auth/login` - Login
- `/api/auth/logout` - Logout
- `/api/auth/me` - Current user
- `/api/admin/*` - Admin operations
- `/api/staff/*` - Staff operations
- `/api/public/*` - Public data

---

## DEPLOYMENT CHECKLIST

### ✅ Frontend (Vercel)
```
[ ] Set NEXT_PUBLIC_API_URL = https://lims-system-vogc.onrender.com
[ ] Run: npm run build (verify 0 errors, 14 routes generated)
[ ] Deploy to Vercel
[ ] Test login endpoint response
```

### ✅ Backend (Render)
```
[ ] DATABASE_URL is set from Supabase
[ ] SECRET_KEY is set (unique, 32+ chars)
[ ] CORS_ORIGINS includes https://lims-system-neon.vercel.app (no trailing slash)
[ ] ENVIRONMENT = production
[ ] Run migrations: npm run migrate (or python -m alembic upgrade head)
[ ] Deploy to Render
[ ] Test GET /health endpoint
[ ] Verify database connection
```

### ✅ Supabase
```
[ ] Database created and initialized
[ ] Migrations applied
[ ] Roles and permissions seeded
[ ] SSL mode enabled (sslmode=require in connection string)
[ ] Row security policies configured (if needed)
```

---

## SUMMARY TABLE

| Variable | Platform | Type | Required | Security |
|----------|----------|------|----------|----------|
| NEXT_PUBLIC_API_URL | Vercel | String | ✅ YES | 🟢 Safe |
| DATABASE_URL | Render | String | ✅ YES | 🔴 Secret |
| SECRET_KEY | Render | String | ✅ YES | 🔴 Secret |
| CORS_ORIGINS | Render | String | ✅ YES | 🟡 Sensitive |
| ENVIRONMENT | Render | String | ⚪ Optional | 🟢 Safe |
| ACCESS_TOKEN_EXPIRE_MINUTES | Render | Number | ⚪ Optional | 🟢 Safe |
| NEXT_PUBLIC_SUPABASE_URL | Vercel | String | ⚪ Optional | 🟢 Safe |
| NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY | Vercel | String | ⚪ Optional | 🟢 Safe |

---

## FILES TO UPDATE FOR NEW DEPLOYMENTS

1. `frontend/.env.local` - Local development
2. `frontend/.env.example` - Git-tracked template
3. Vercel Dashboard → Environment Variables
4. Render Dashboard → Environment Variables
5. `backend/.env` - Local development (not committed)
6. `backend/.env.example` - Git-tracked template

---

## CURRENT IMPLEMENTATION STATUS

✅ Central API client implemented
✅ Environment variables configured
✅ CORS headers properly set
✅ No hardcoded URLs in production code
✅ No Supabase direct database access from frontend
✅ All API calls authenticated via JWT
✅ Backend enforces authorization

🔧 Ready for: Login testing, dashboard development, RBAC enforcement
