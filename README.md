# Field Sample Management & Public Data Portal

This repository contains the scaffold for a two-part system:

- `backend/` — FastAPI backend with PostgreSQL, role-based authentication, and audit logging.
- `frontend/` — Next.js public and admin interfaces with separate routes and read-only public pages.

## Structure

- `backend/`
  - `app/` — FastAPI application skeleton
  - `alembic/` — database migration setup
  - `.env.example` — environment variable template

- `frontend/`
  - `src/pages/public/` — public portal pages
  - `src/pages/admin/` — admin portal pages
  - `.env.example` — public environment template

## Notes

This scaffold is intentionally minimal. No business logic or data models are implemented yet, only configuration and folder structure.
