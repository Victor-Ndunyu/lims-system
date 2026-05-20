# Backend

This directory contains the FastAPI backend scaffold for the field sample management system.

## Setup

1. Create a Python environment (`python -m venv .venv`)
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and update values.

## Migrations

- `alembic revision --autogenerate -m "init"`
- `alembic upgrade head`
- Production helper: `.\scripts\migrate.ps1`

## Seed data

Set `FIRST_ADMIN_EMAIL`, `FIRST_ADMIN_PASSWORD`, and optionally `FIRST_ADMIN_FULL_NAME`, then run:

`python -m app.db.seed`

The seed script creates default roles, permissions, role-permission mappings, and the first `super_admin` user. It does not hardcode credentials.

## Backups

- Create a PostgreSQL backup: `.\scripts\backup-postgres.ps1 -DatabaseUrl $env:DATABASE_URL`
- Restore a PostgreSQL backup: `.\scripts\restore-postgres.ps1 -DatabaseUrl $env:DATABASE_URL -BackupPath .\backups\backup.dump`

## Notes

This scaffold includes the minimal app structure, configuration, and migration setup. Business logic and models are not implemented yet.

Production deployment details are in `../docs/deployment.md`.
