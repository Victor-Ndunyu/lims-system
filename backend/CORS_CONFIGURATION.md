# CORS Configuration for Deployed Frontends

## Quick Setup for Vercel Deployment

### Backend: Add Vercel Domains to CORS_ORIGINS

**In your Render dashboard or production environment, set:**

```env
CORS_ORIGINS=https://myapp.vercel.app,https://preview-*.vercel.app,http://localhost:3000
```

Replace:
- `myapp.vercel.app` with your actual production Vercel domain (or custom domain)
- `preview-*.vercel.app` with your Vercel preview deployment pattern (optional)
- Keep `http://localhost:3000` for local development

### What This Does

| Origin | Environment | Purpose |
|--------|-------------|---------|
| `https://myapp.vercel.app` | Production | Vercel production deployment |
| `https://preview-*.vercel.app` | PR Previews | Vercel preview deployments (one per PR) |
| `http://localhost:3000` | Development | Local frontend development |

---

## Production CORS Configuration

### ✅ Vercel Production Domain

**If using Vercel's default domain:**
```env
CORS_ORIGINS=https://myapp.vercel.app
```

**If using a custom domain:**
```env
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

**If supporting both:**
```env
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,https://myapp.vercel.app
```

---

### ✅ Vercel Preview Deployments (PR Previews)

**Option 1: Allow all Vercel preview domains**
```env
CORS_ORIGINS=https://preview-*.vercel.app,https://myapp.vercel.app
```

**Option 2: Specific preview deployment**
```env
CORS_ORIGINS=https://preview-abc123.vercel.app,https://myapp.vercel.app
```

**Note:** Each PR creates a unique preview URL like `preview-pr123.vercel.app`

---

### ✅ Multiple Environments

```env
CORS_ORIGINS=https://yourdomain.com,https://staging.yourdomain.com,https://myapp.vercel.app,https://preview-*.vercel.app,http://localhost:3000
```

---

## Format Rules

- **No trailing slashes:** `https://domain.com` ✅ | `https://domain.com/` ❌
- **Include protocol:** `https://` or `http://`
- **Port numbers:** `http://localhost:3000` includes the port
- **Comma-separated:** Multiple origins separated by commas (no spaces after commas)

---

## Testing CORS Configuration

### Test from Browser DevTools Console

```javascript
// This will fail with CORS error if origin not allowed
fetch('https://api.example.com/health', {
  method: 'GET',
  credentials: 'include'  // Important for auth
}).then(r => r.json()).then(console.log)
```

### Test with cURL (simulating origin)

```bash
curl -H "Origin: https://myapp.vercel.app" \
     -H "Access-Control-Request-Method: POST" \
     https://api.example.com/health
```

**Successful response includes:**
```
Access-Control-Allow-Origin: https://myapp.vercel.app
Access-Control-Allow-Credentials: true
```

---

## Authentication + CORS

The backend allows credentials with CORS:

```python
CORSMiddleware(
    allow_credentials=True,  # ← Allows cookies and Authorization headers
    allow_headers=["Authorization", "Content-Type"],
)
```

**Frontend must include credentials:**

```typescript
// ✅ CORRECT
fetch(apiUrl, {
  credentials: 'include'  // Send auth cookies
})

// ❌ WRONG (will fail with CORS error)
fetch(apiUrl)
```

The API client (`src/lib/api.ts`) already handles this correctly.

---

## Troubleshooting CORS Errors

### Error: "Access to XMLHttpRequest blocked by CORS policy"

**Cause 1: Origin not in CORS_ORIGINS**
```
Origin: https://myapp.vercel.app
Allowed: https://yourdomain.com,https://localhost:3000
```
→ Solution: Add `https://myapp.vercel.app` to CORS_ORIGINS

**Cause 2: Missing credentials header**
```javascript
// ❌ Missing credentials
fetch(apiUrl)

// ✅ Correct
fetch(apiUrl, { credentials: 'include' })
```

**Cause 3: CORS method not allowed**
```
GET /api/auth/login (works) ✅
DELETE /api/users/123 (fails) ❌
```
→ Solution: Backend allows: GET, POST, PUT, DELETE, OPTIONS

---

## Render Deployment Settings

**In render.yaml or Render dashboard:**

```yaml
envVars:
  - key: CORS_ORIGINS
    value: https://yourdomain.com,https://myapp.vercel.app
```

**Or set in Render dashboard:**
1. Go to Service Settings
2. Environment tab
3. Add `CORS_ORIGINS` with comma-separated origins

---

## Development vs Production

### Development (.env)
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:8000
```

### Production (Render environment variables)
```env
CORS_ORIGINS=https://yourdomain.com,https://myapp.vercel.app
```

---

## No Wildcard Origins

❌ **This is NOT allowed for security:**
```env
CORS_ORIGINS=*                    # Insecure!
CORS_ORIGINS=https://*            # Not supported
CORS_ORIGINS=*.vercel.app         # Not supported
```

✅ **Instead, list specific origins:**
```env
CORS_ORIGINS=https://myapp.vercel.app,https://preview-pr123.vercel.app
```

---

## Security Best Practices

1. ✅ **Explicit origins:** Always list specific, allowed origins
2. ✅ **HTTPS in production:** Use `https://` for production domains
3. ✅ **No credentials with wildcard:** Never use `*` with `allow_credentials: true`
4. ✅ **Add new origins carefully:** Each origin can make API requests
5. ✅ **Remove old origins:** Delete preview domains after PR is closed

---

## Environment Variable Priority

1. **Render dashboard** (production) - takes precedence
2. **render.yaml** (default) - fallback
3. **.env file** (development) - local only

To update production CORS:
1. Go to Render dashboard
2. Service Settings → Environment
3. Update `CORS_ORIGINS` value
4. Service auto-restarts with new CORS config

---

**Related:** See [DEPLOYMENT.md](./DEPLOYMENT.md) for complete Render setup
