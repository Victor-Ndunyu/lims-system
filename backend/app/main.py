from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import settings

app = FastAPI(title="Field Sample Management API")

if settings.cors_origin_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Forwarded-For"],
    )

app.include_router(api_router, prefix="/api")


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Field Sample Management API scaffold"}


@app.get("/healthz")
def health_check():
    return {"status": "ok", "environment": settings.environment}
