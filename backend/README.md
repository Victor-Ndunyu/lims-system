# Backend

This directory contains the FastAPI backend scaffold for the field sample management system.

## Setup

1. Create a Python environment (`python -m venv .venv`)
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and update values.

## Migrations

- `alembic revision --autogenerate -m "init"`
- `alembic upgrade head`

## Notes

This scaffold includes the minimal app structure, configuration, and migration setup. Business logic and models are not implemented yet.
