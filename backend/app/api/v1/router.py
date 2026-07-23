"""API v1 router — aggregates all sub-routers under /api/v1."""

from fastapi import APIRouter

from app.api.v1 import admin

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
# Future modules will be added here:
# api_v1_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# api_v1_router.include_router(users.router, prefix="/users", tags=["Users"])
# api_v1_router.include_router(friends.router, prefix="/friends", tags=["Friends"])
# api_v1_router.include_router(groups.router, prefix="/groups", tags=["Groups"])
# api_v1_router.include_router(availability.router, prefix="/availability", tags=["Availability"])
# api_v1_router.include_router(timetables.router, prefix="/timetables", tags=["Timetables"])
# api_v1_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
