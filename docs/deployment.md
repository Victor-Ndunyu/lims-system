# Deployment Guide

This project has three deployable surfaces:

- Backend API: FastAPI service under `backend/`
- Public portal: Next.js deployment serving `/public` only
- Admin portal: Next.js deployment serving `/admin` only

The public and admin portals can be deployed separately from the same `frontend/` codebase by setting `NEXT_PUBLIC_PORTAL_MODE`.

## Production Environment

Backend required secrets:

- `DATABASE_URL`: PostgreSQL connection string, for example `postgresql+psycopg://user:password@host:5432/dbname`
- `SECRET_KEY`: at least 64 random characters, generated outside the repository
- `ENVIRONMENT=production`
- `ACCESS_TOKEN_EXPIRE_MINUTES=60`
- `CORS_ORIGINS`: comma-separated frontend origins, for example `https://samples.example.com,https://admin.samples.example.com`

Frontend public portal:

- `NEXT_PUBLIC_PORTAL_MODE=public`
- `NEXT_PUBLIC_PUBLIC_API_URL=https://api.samples.example.com/api`
- `NEXT_PUBLIC_ADMIN_API_URL=https://api.samples.example.com/api`

Frontend admin portal:

- `NEXT_PUBLIC_PORTAL_MODE=admin`
- `NEXT_PUBLIC_ADMIN_API_URL=https://api.samples.example.com/api`
- `NEXT_PUBLIC_PUBLIC_API_URL=https://api.samples.example.com/api`

Use `backend/.env.example`, `frontend/.env.public.example`, and `frontend/.env.admin.example` as templates. Do not commit real `.env` files.

## Secure Secrets Handling

- Store production secrets in the deployment platform secret manager, not in Git.
- Generate `SECRET_KEY` with a cryptographically secure generator, such as:
  `python -c "import secrets; print(secrets.token_urlsafe(64))"`
- Use a dedicated database user for the app with the least privileges needed for runtime.
- Use a separate migration/deployment database credential if your platform supports it.
- Rotate `SECRET_KEY`, database passwords, and admin credentials on a regular schedule and after staff changes.
- Keep backup storage credentials separate from application runtime credentials.

## Backend Deployment

1. Provision PostgreSQL 15+.
2. Create the application database and app database user.
3. Set backend environment variables from `backend/.env.example`.
4. Install dependencies:
   `pip install -r backend/requirements.txt`
5. Run migrations from `backend/`:
   `.\scripts\migrate.ps1`
6. Start the API:
   `uvicorn app.main:app --host 0.0.0.0 --port 8000`
7. Confirm health:
   `GET https://api.samples.example.com/healthz`

## Database Migrations

Migrations live in `backend/alembic/versions`.

Common commands from `backend/`:

- Upgrade to latest: `alembic upgrade head`
- Check current revision: `alembic current`
- Create a new migration after model changes: `alembic revision --autogenerate -m "describe change"`
- Roll back one revision in a non-production environment: `alembic downgrade -1`

Production migration rule: back up first, run migrations once, verify health and key workflows, then deploy application instances.

## Backups

Create an on-demand PostgreSQL backup:

```powershell
.\scripts\backup-postgres.ps1 -DatabaseUrl $env:DATABASE_URL -OutputDirectory .\backups
```

Restore into a target database:

```powershell
.\scripts\restore-postgres.ps1 -DatabaseUrl $env:DATABASE_URL -BackupPath .\backups\field-sample-management-YYYYMMDD-HHMMSS.dump
```

Recommended production backup policy:

- Daily automated `pg_dump --format=custom` backups.
- Point-in-time recovery enabled if the managed database supports it.
- Encrypted backup storage with access limited to operators.
- At least 30 days retention for daily backups.
- Monthly restore drill into a non-production database.

## Separate Public and Admin Deployments

Public deployment:

1. Deploy `frontend/` as `samples.example.com`.
2. Set env from `frontend/.env.public.example`.
3. Build with `npm run build:public` or set `NEXT_PUBLIC_PORTAL_MODE=public` and run `npm run build`.
4. The root path redirects to `/public`; `/admin/*` redirects to `/public`.
5. The local build artifact is written to `frontend/.next-public`.

Admin deployment:

1. Deploy the same `frontend/` codebase as `admin.samples.example.com`.
2. Set env from `frontend/.env.admin.example`.
3. Build with `npm run build:admin` or set `NEXT_PUBLIC_PORTAL_MODE=admin` and run `npm run build`.
4. The root path redirects to `/admin`; `/public/*` redirects to `/admin`.
5. The local build artifact is written to `frontend/.next-admin`.

If your hosting platform cannot run two frontend deployments, deploy one frontend with no `NEXT_PUBLIC_PORTAL_MODE`; both `/public` and `/admin` remain available in the same app.

## Deployment Checklist

- Backend env vars are set in the platform secret manager.
- Frontend public and admin env vars point at the production API.
- `CORS_ORIGINS` includes both deployed frontend origins.
- PostgreSQL is reachable only from approved networks/services.
- A fresh database backup exists before migrations.
- `alembic upgrade head` completed successfully.
- `GET /healthz` returns `{"status":"ok"}`.
- Public portal shows only approved records.
- Admin portal login, sample creation, submission, review, and audit trail work.
- Public domain cannot browse `/admin/*` in public-only deployment mode.
- Admin domain redirects `/public/*` in admin-only deployment mode.
- TLS is enabled for API, public portal, and admin portal.
- Logs and error alerts are configured for API and frontend deployments.
- Backup automation and restore instructions are documented for operators.
