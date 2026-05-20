# Backend Environment Variables Reference

## Quick Summary

| Variable | Required | Backend Only | Production Value |
|----------|----------|--------------|------------------|
| `DATABASE_URL` | ✅ Yes | 🔒 Yes | Supabase PostgreSQL URL |
| `SECRET_KEY` | ✅ Yes | 🔒 Yes | 64+ random characters |
| `ENVIRONMENT` | ❌ No | 🔒 Yes | `production` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ❌ No | 🔒 Yes | `1440` (24 hours) |
| `CORS_ORIGINS` | ❌ No | ✅ No* | Your frontend domain(s) |
| `FIRST_ADMIN_EMAIL` | ❌ No** | 🔒 Yes | admin email for seeding |
| `FIRST_ADMIN_PASSWORD` | ❌ No** | 🔒 Yes | Strong unique password |
| `FIRST_ADMIN_FULL_NAME` | ❌ No | 🔒 Yes | "System Administrator" |

*CORS_ORIGINS is technical (domain names only), not sensitive  
**Only needed when running `python -m app.db.seed` script

---

## Variable Details

### REQUIRED VARIABLES ✅

#### `DATABASE_URL`
- **Type:** Connection String
- **Required:** Yes
- **Backend Only:** 🔒 Yes
- **Purpose:** PostgreSQL database connection from Supabase
- **Format:** `postgresql+psycopg://user:password@host:port/database?sslmode=require`
- **Example:** `postgresql+psycopg://postgres.abc123def456:MyPassword123@aws-0-eu-west-1.pooler.supabase.com:5432/postgres?sslmode=require`
- **Get From:** Supabase Dashboard → Project Settings → Database
- **Security:** Contains database credentials - NEVER expose to frontend
- **Missing Error:** "DATABASE_URL is required. Set it in the environment or backend/.env before starting the backend."

#### `SECRET_KEY`
- **Type:** Cryptographic Key
- **Required:** Yes
- **Backend Only:** 🔒 Yes
- **Purpose:** Signing JWT authentication tokens
- **Format:** 32+ random URL-safe characters
- **Generate:** `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- **Example:** `N_FecgYz-btmBI1g-tC8105xsqo_EH7_8-wfNDjTrOo`
- **Security:** If leaked, attackers can forge user sessions - NEVER expose to frontend
- **Missing Error:** "SECRET_KEY is required. Set it in the environment or backend/.env before starting the backend."

---

### OPTIONAL VARIABLES (with Defaults)

#### `ENVIRONMENT`
- **Type:** String (enum)
- **Required:** No
- **Default:** `development`
- **Backend Only:** 🔒 Yes
- **Valid Values:** `development`, `staging`, `production`
- **Purpose:** Controls logging level and error detail verbosity
- **Render:** Set to `production`
- **Example:** `ENVIRONMENT=production`

#### `ACCESS_TOKEN_EXPIRE_MINUTES`
- **Type:** Integer
- **Required:** No
- **Default:** `60` (1 hour)
- **Backend Only:** 🔒 Yes
- **Purpose:** How long user sessions remain valid
- **Recommended:** `1440` (24 hours) for production
- **Example:** `ACCESS_TOKEN_EXPIRE_MINUTES=1440`
- **Note:** User will need to log in again after expiry

#### `CORS_ORIGINS`
- **Type:** Comma-separated String
- **Required:** No
- **Default:** Empty (no CORS allowed)
- **Backend Only:** No (but sensitive for security)
- **Purpose:** Which domains can call the API from browsers
- **Format:** `https://domain1.com,https://domain2.com` (no trailing slashes)
- **Example:** `CORS_ORIGINS=https://samples.example.com,https://admin.samples.example.com`
- **Security:** Controls browser access - set to EXACT frontend domain(s)
- **Local Testing:** `http://localhost:3000,http://localhost:3001`
- **Important:** Without this, frontend cannot call API due to browser CORS policy

---

### OPTIONAL VARIABLES (Initial Admin Setup)

These are only needed when running the database seeding script:
```bash
python -m app.db.seed
```

#### `FIRST_ADMIN_EMAIL`
- **Type:** Email String
- **Required:** No (unless seeding)
- **Backend Only:** 🔒 Yes
- **Purpose:** Email for the first admin user created during setup
- **Example:** `FIRST_ADMIN_EMAIL=admin@example.com`
- **Note:** User is created only once; duplicate emails are skipped

#### `FIRST_ADMIN_PASSWORD`
- **Type:** Password String
- **Required:** No (unless seeding)
- **Backend Only:** 🔒 Yes
- **Purpose:** Password for the first admin user
- **Example:** `FIRST_ADMIN_PASSWORD=Change123!@SecurePassword`
- **Security:** Should be strong, unique, and changed immediately after first login
- **Recommendation:** Use a password generator - minimum 12 characters with uppercase, lowercase, numbers, symbols

#### `FIRST_ADMIN_FULL_NAME`
- **Type:** String
- **Required:** No
- **Default:** `System Administrator`
- **Backend Only:** 🔒 Yes
- **Purpose:** Display name for the first admin user
- **Example:** `FIRST_ADMIN_FULL_NAME=Victor Admin`

---

## ⚠️ Security Rules

### 🔒 BACKEND ONLY (Never expose to frontend)
These contain secrets and sensitive information:
- `DATABASE_URL` - Contains database password
- `SECRET_KEY` - Can forge user sessions
- `FIRST_ADMIN_PASSWORD` - Leaks admin credentials
- Any environment variable without `NEXT_PUBLIC_` prefix

### ❌ NEVER Put in Frontend
```javascript
// ❌ WRONG - These are secrets!
const dbUrl = process.env.DATABASE_URL;
const secret = process.env.SECRET_KEY;
const adminPass = process.env.FIRST_ADMIN_PASSWORD;
```

### ✅ Safe for Frontend (Supabase)
These are safe to expose (read-only keys):
```javascript
// ✅ CORRECT - These are read-only public keys
const NEXT_PUBLIC_SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL;
const NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;
const NEXT_PUBLIC_API_URL = process.env.NEXT_PUBLIC_API_URL;
```

---

## Configuration by Environment

### Local Development
```env
ENVIRONMENT=development
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/field_sample_dev?sslmode=disable
SECRET_KEY=dev-secret-key-change-in-production-do-not-use-this
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:8000
```

### Staging/Testing
```env
ENVIRONMENT=staging
DATABASE_URL=postgresql+psycopg://postgres.STAGING_ID:PASSWORD@aws-0-eu-west-1.pooler.supabase.com:5432/postgres?sslmode=require
SECRET_KEY=[Generated 64+ char secret]
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=https://staging-samples.example.com,https://staging-admin.example.com
```

### Production (Render)
```env
ENVIRONMENT=production
DATABASE_URL=postgresql+psycopg://postgres.PROD_ID:PASSWORD@aws-0-eu-west-1.pooler.supabase.com:5432/postgres?sslmode=require
SECRET_KEY=[Generated 64+ char secret]
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=https://samples.example.com,https://admin.samples.example.com
```

---

## Validation & Startup

### On Startup
The backend validates:
1. ✅ `DATABASE_URL` is set (not empty)
2. ✅ `SECRET_KEY` is set (not empty)
3. ✅ `DATABASE_URL` is a valid PostgreSQL connection
4. ✅ Can connect to the database

If validation fails, the application will **not start** and will show an error.

### Common Startup Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "DATABASE_URL is required" | Not set in env | Set in .env or Render dashboard |
| "SECRET_KEY is required" | Not set in env | Set in .env or Render dashboard |
| "could not connect to server" | Wrong DB credentials | Verify DATABASE_URL in Supabase |
| "password authentication failed" | Wrong password in URL | Check password in Supabase dashboard |

---

## Usage Examples

### Get Current Settings (in Python)
```python
from app.core.config import settings

print(settings.environment)
print(settings.access_token_expire_minutes)
print(settings.cors_origin_list)  # Returns list instead of string
```

### Read a Variable (in Python)
```python
import os

email = os.getenv("FIRST_ADMIN_EMAIL")
password = os.getenv("FIRST_ADMIN_PASSWORD")
```

---

## Related Documentation

- See [.env.example](.env.example) for template with all variables
- See [DEPLOYMENT.md](./DEPLOYMENT.md) for Render-specific setup
- See [RENDER_VERIFICATION.md](./RENDER_VERIFICATION.md) for deployment checklist
