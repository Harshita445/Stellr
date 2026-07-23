"""Shared Pydantic schemas used across modules."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., description="'healthy', 'degraded', or 'unhealthy'")
    version: str = Field(..., description="Application version")
    uptime_seconds: float = Field(..., description="Seconds since process start")
    database: dict = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    error: dict = Field(..., description="Error details with 'code' and 'message'")


class PaginationParams(BaseModel):
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)
