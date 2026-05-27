from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api import api_router
from app.core.config import settings
from app.db.session import engine

app = FastAPI(title="Field Sample Management API")

DEFAULT_CORS_ORIGINS = [
    "https://lims-system-neon.vercel.app",
    "https://lims-systems-dv95.vercel.app",
    "https://lims-system-dv95-205a4ic7p-victor-ndunyus-projects.vercel.app",
    "http://localhost:3000",
    "http://localhost:3001",
]

# CORS Configuration
# Uses CORS_ORIGINS environment variable (comma-separated list) plus known
# deployment origins so an incomplete Render env var does not break login.
cors_origins = list(dict.fromkeys([*settings.cors_origin_list, *DEFAULT_CORS_ORIGINS]))

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers under /api prefix
# Auth, samples, and admin endpoints available at /api/auth, /api/samples, /api/admin, etc.
app.include_router(api_router, prefix="/api")


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Field Sample Management API scaffold"}


@app.get("/healthz")
def health_check():
    return {"status": "ok", "environment": settings.environment}


@app.get("/health")
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "database": "unavailable",
                "error": exc.__class__.__name__,
            },
        ) from exc

    return {
        "status": "healthy",
        "environment": settings.environment,
        "database": "available",
    }
