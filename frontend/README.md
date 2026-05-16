# Frontend

This directory contains the Next.js scaffold for the public and admin portals.

## Setup

1. Install dependencies: `npm install`
2. Run development server: `npm run dev`
3. Copy `.env.public.example` or `.env.admin.example` to `.env.local` and update values.

## Production builds

- Public-only portal: `npm run build:public`
- Admin-only portal: `npm run build:admin`
- Combined local/default app: `npm run build`

## Notes

- Public pages should remain read-only.
- Admin pages require authentication and role checks in the future.
- Full deployment details are in `../docs/deployment.md`.
