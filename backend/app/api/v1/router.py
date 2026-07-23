"""API v1 router — aggregates all sub-routers under /api/v1."""

from fastapi import APIRouter

from app.api.v1 import admin, auth

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_v1_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
