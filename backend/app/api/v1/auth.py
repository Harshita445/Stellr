"""Authentication routes.

Registration is the only endpoint that accepts a roll number.
All other endpoints use UUIDs only. This is by design:
- Anti-scraping: roll numbers are never exposed in responses, URLs, or query params
- Anti-enumeration: same response shape for new and existing roll numbers
- Device binding: tokens are bound to (user_uuid, device_id) pairs
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Header, Request

from app.api.deps import get_auth_service, get_rate_limit
from app.core.exceptions import AuthenticationError
from app.core.middleware import InMemoryRateLimiter
from app.schemas.auth.requests import (  # noqa: F811
    RefreshRequest,
    RegisterRequest,
)
from app.schemas.auth.responses import RefreshResponse, RegisterResponse, TokenResponse, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=201,
    summary="Register or login with roll number",
    description=(
        "One endpoint for both registration and login. "
        "If the roll number is new, a user is created. "
        "If the roll number exists, the previous device is deactivated "
        "and a new device session is issued (one active device per user). "
        "Roll number is NEVER returned in the response."
    ),
)
async def register(
    body: RegisterRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    rate_limiter: InMemoryRateLimiter = Depends(get_rate_limit),
) -> RegisterResponse:
    client_ip = request.client.host if request.client else "unknown"
    if not rate_limiter.check(f"register:{client_ip}", max_requests=5, window_seconds=60):
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=429,
            content={"error": {"code": "RATE_LIMITED", "message": "Too many requests. Try again in 60 seconds."}},
            headers={"Retry-After": "60"},
        )

    result = await auth_service.register(
        roll_number=body.roll_number,
        display_name=body.display_name,
        section_code=body.section_code,
    )

    return RegisterResponse(
        user=UserResponse(
            id=result.user_id,
            display_name=result.display_name,
            section_code=result.section_code,
        ),
        tokens=TokenResponse(
            access_token=result.tokens.access_token,
            refresh_token=result.tokens.refresh_token,
            device_id=str(result.device_id),
        ),
    )


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    summary="Refresh access token",
    description=(
        "Exchange a refresh token for a new access token. "
        "Refresh tokens are rotated on every use — the old token is invalidated. "
        "The device_id must match the device_id the refresh token was issued to."
    ),
)
async def refresh(
    body: RefreshRequest,
    device_id: str = Header(..., alias="X-Device-ID"),
    auth_service: AuthService = Depends(get_auth_service),
) -> RefreshResponse:
    result = await auth_service.refresh(
        refresh_token=body.refresh_token,
        device_id=UUID(device_id),
    )

    return RefreshResponse(
        access_token=result.tokens.access_token,
        refresh_token=result.tokens.refresh_token,
    )
