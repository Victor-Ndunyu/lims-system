from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api import api_router
from app.core.config import settings
from app.db.session import engine

app = FastAPI(title="Field Sample Management API")

# CORS Configuration
# Reads allowed origins from CORS_ORIGINS environment variable
# Format: comma-separated list of full origins (e.g., https://myapp.com,https://preview-123.vercel.app)
# Supports credentials and auth headers for authenticated requests
if settings.cors_origin_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Forwarded-For"],
    )

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
