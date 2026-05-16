"""API router package."""

from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.public import router as public_router
from app.api.staff import router as staff_router
from app.api.admin import router as admin_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(public_router)
api_router.include_router(staff_router)
api_router.include_router(admin_router)
