"""API v1 router — aggregates all sub-routers under /api/v1."""

from fastapi import APIRouter

from app.api.v1 import admin, auth, availability, dashboard, friends, groups, sections, users

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_v1_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(availability.router, prefix="/availability", tags=["Availability"])
api_v1_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_v1_router.include_router(friends.router, prefix="/friends", tags=["Friends"])
api_v1_router.include_router(groups.router, prefix="/groups", tags=["Groups"])
api_v1_router.include_router(sections.router, prefix="/sections", tags=["Sections"])
api_v1_router.include_router(users.router, prefix="/users", tags=["Users"])
