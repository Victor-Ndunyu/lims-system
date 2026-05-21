# Frontend Architecture Audit

**Date:** May 21, 2026  
**Analysis Type:** API Call Inventory & Security Review  
**Status:** Pre-changes architectural analysis

---

## Executive Summary

**Current State:** Frontend has a mixed architecture with both FastAPI backend calls AND direct Supabase browser access.

**Recommendation:** **Consolidate to backend-only for protected operations.** Direct Supabase browser access should be removed or restricted to documentation/testing only.

---

## API Call Inventory

### Protected Operations (Require Authentication)

All calls go through `frontend/src/lib/api.ts` using the `request()` function with auth headers.

| Operation | Endpoint | HTTP Method | Auth Required | Description |
|-----------|----------|-------------|---|---|
| Login | POST `/auth/login` | POST | ❌ No | User authentication |
| Logout | POST `/auth/logout` | POST | ✅ Yes | Session termination |
| Fetch Current User | GET `/auth/me` | GET | ✅ Yes | Get authenticated user info |
| **Admin: Get Stats** | GET `/admin/stats` | GET | ✅ Yes | Dashboard statistics |
| **Admin: Get Charts** | GET `/admin/charts` | GET | ✅ Yes | Data visualization |
| **Admin: List Users** | GET `/admin/users` | GET | ✅ Yes | User management |
| **Admin: List Roles** | GET `/admin/roles` | GET | ✅ Yes | Role configuration |
| **Admin: List Permissions** | GET `/admin/permissions` | GET | ✅ Yes | Permission configuration |
| **Admin: Assign Permissions** | POST `/admin/roles/{id}/permissions` | POST | ✅ Yes | Update role permissions |
| **Admin: Create User** | POST `/admin/users` | POST | ✅ Yes | Create new staff user |
| **Staff: List Samples** | GET `/staff/samples` | GET | ✅ Yes | User's submitted samples |
| **Staff: Get Lookups** | GET `/staff/lookups` | GET | ✅ Yes | Form data (dropdowns, etc) |
| **Staff: Create Sample** | POST `/staff/samples` | POST | ✅ Yes | Submit new sample |
| **Staff: Update Sample** | PUT `/staff/samples/{id}` | PUT | ✅ Yes | Modify sample |
| **Staff: Review Sample** | POST `/staff/samples/{id}/review` | POST | ✅ Yes | Approve/reject sample |
| **Staff: Get Sample** | GET `/staff/samples/{id}` | GET | ✅ Yes | View sample details |

**Total Protected Calls:** 16 operations

**All correctly use:**
- ✅ `request()` function with auth headers
- ✅ Bearer token from localStorage
- ✅ Backend authentication enforcement

---

### Public Operations (No Authentication Required)

| Operation | Endpoint | HTTP Method | Auth Required | Description |
|-----------|----------|-------------|---|---|
| Get Public Samples | GET `/public/samples` | GET | ❌ No | Publicly visible samples |

**Implementation:** Uses `publicRequest()` function - no auth headers added.

**Status:** ✅ Correct - No authentication bypass risk.

---

## Direct Supabase Browser Access

### Files Using Direct Supabase Calls

#### 1. **frontend/src/utils/supabase/client.ts** ✅
- **Purpose:** Browser client factory
- **Usage:** Creates Supabase client instance
- **Current Use:** Only in test.ts (non-production)
- **Risk Level:** 🟡 Medium - Only test code uses it
- **Action:** Keep, but ensure test code is removed from production

#### 2. **frontend/src/utils/supabase/test.ts** ⚠️
- **Purpose:** Connection testing
- **Line 8:** `supabase.from('todos').select('*').limit(1)`
- **Issue:** Direct database query from browser
- **Risk Level:** 🔴 High - Production code should NOT query DB directly
- **Recommendation:** Remove from production build or restrict to development only

#### 3. **frontend/src/utils/supabase/server.ts** ✅
- **Purpose:** Server-side Supabase client (Next.js server)
- **Current Use:** Not actively used in analyzed code
- **Risk Level:** 🟢 Low - Server-side is appropriate if used for backend logic
- **Note:** Server-side access is better than browser access

#### 4. **frontend/src/utils/supabase/middleware.ts** ⚠️
- **Purpose:** Auth cookie management
- **Usage:** In proxy.ts middleware - `supabase.auth.getUser()`
- **Risk Level:** 🟡 Medium - Uses auth, but only for cookie refresh
- **Issue:** Mixing Supabase auth with backend JWT auth
- **Recommendation:** Evaluate if still needed with backend auth

#### 5. **frontend/src/proxy.ts** ⚠️
- **Purpose:** Next.js middleware
- **Line 5:** Calls `supabase.auth.getUser()`
- **Issue:** Supabase auth cookie refresh happens here
- **Risk Level:** 🟡 Medium - Supabase cookies persist even with backend auth
- **Current Impact:** May conflict with backend JWT tokens
- **Recommendation:** Decide if Supabase auth is still needed

---

## Security Analysis

### ✅ What's Correct

```
Frontend → Backend (FastAPI)
  ├─ All protected operations use backend auth ✅
  ├─ JWT tokens in localStorage ✅
  ├─ Auth headers sent with every request ✅
  ├─ Backend validates every request ✅
  └─ API_ENDPOINTS centralized in api-config.ts ✅

Public operations:
  └─ No auth bypass, direct public reads ✅

Secrets:
  └─ No API keys or secrets in frontend ✅
```

### ⚠️ What Needs Review

```
Supabase in Frontend:
  ├─ client.ts - Creates browser Supabase client
  │    └─ Only used in test.ts (non-production)
  │
  ├─ middleware.ts - Supabase auth in middleware
  │    └─ Manages auth cookies (may not be needed)
  │
  └─ test.ts - Direct database query from browser ❌
       └─ Should be removed or test-only
```

### 🔴 What's Wrong

```
frontend/src/utils/supabase/test.ts:
  └─ Line 8: supabase.from('todos').select('*')
       ├─ Direct database query from browser
       ├─ Bypasses backend authorization
       ├─ Not using backend API at all
       └─ SHOULD BE REMOVED or restricted to development
```

---

## Architectural Decision: Backend-Only for Protected Data

### Current Architecture

```
Frontend Components
  ├─ Authenticated requests → Backend (FastAPI) ✅
  ├─ Public requests → Backend (FastAPI) ✅
  └─ Test/direct queries → Supabase Browser ❌
```

### Recommended Architecture

```
Frontend Components
  ├─ Authenticated requests → Backend (FastAPI) ✅
  ├─ Public requests → Backend (FastAPI) ✅
  ├─ Supabase auth cookies → Backend handles
  └─ Direct DB queries → REMOVED (use backend instead)
```

### Why This Matters

| Scenario | With Backend-Only | With Direct Supabase |
|----------|---|---|
| **Access Control** | Backend enforces roles/permissions | Browser can bypass |
| **Audit Trail** | All operations logged by backend | Browser operations untracked |
| **Data Filtering** | Backend filters per user | Frontend could expose all data |
| **Secrets Safety** | No DB credentials in frontend | Publishable key in browser |
| **Rate Limiting** | Backend enforces limits | Browser requests unlimited |
| **Business Logic** | Centralized in backend | Scattered in frontend |

---

## Recommendations

### Priority 1: Remove Direct Supabase Queries ⚠️

**File:** `frontend/src/utils/supabase/test.ts`

**Action:** Delete this file

**Reason:** 
- Direct database queries from browser bypass backend auth
- No business logic validation
- Security risk if left in production

**Replacement:** If testing is needed, add backend API endpoint for test data.

---

### Priority 2: Review Supabase Auth Middleware 🟡

**Files:** 
- `frontend/src/proxy.ts`
- `frontend/src/utils/supabase/middleware.ts`

**Analysis Needed:**
- Is Supabase auth still needed?
- Are we using Supabase tokens or backend JWT?
- Can this be removed if using only backend auth?

**Current State:**
```typescript
// proxy.ts line 6:
await supabase.auth.getUser();  // Refreshes Supabase auth cookies
```

**Decision:**
- If using FastAPI JWT only → Remove Supabase auth code
- If still using Supabase auth → Keep but ensure no privilege escalation

---

### Priority 3: Keep Supabase Client Libraries ✅

**Files:**
- `frontend/src/utils/supabase/client.ts`
- `frontend/src/utils/supabase/server.ts`

**Status:** Keep these for now (may be used by other parts of app not analyzed)

**Ensure:** They never bypass backend auth for protected data

---

## Final Architecture Checklist

Before making changes, confirm:

- [ ] All 16 API operations use `request()` function
- [ ] All use auth headers from localStorage
- [ ] Backend validates every request
- [ ] No direct Supabase database queries in production code
- [ ] No Supabase service-role keys in frontend
- [ ] Public operations use `publicRequest()` only
- [ ] Test files are excluded from production builds

---

## Approval Gate

**Before proceeding with code changes:**

1. Confirm you want to remove `test.ts` direct Supabase queries
2. Decide if Supabase auth middleware is still needed
3. Verify all protected operations go through backend

**Current Status:** ✅ Ready for implementation after approval

---

## Implementation Plan

If approved, next steps:

1. **Remove** `frontend/src/utils/supabase/test.ts`
2. **Review** `frontend/src/proxy.ts` and `frontend/src/utils/supabase/middleware.ts`
3. **Optionally Remove** Supabase auth if using only backend JWT
4. **Verify** all API calls still work correctly
5. **Deploy** to Vercel with cleaner architecture

---

**Conclusion:** Frontend is mostly correctly designed (backend-first), but has legacy Supabase direct query code that should be removed. Otherwise, security posture is solid.
