from uuid import UUID

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token (15 min expiry)")
    refresh_token: str = Field(..., description="Refresh token for obtaining new access tokens")
    device_id: str = Field(..., description="Device identifier — store client-side and send as X-Device-ID header")
    token_type: str = "bearer"
    expires_in: int = 900  # 15 minutes in seconds


class UserResponse(BaseModel):
    id: UUID = Field(..., description="User UUID — public identifier")
    display_name: str = Field(..., description="Display name")
    section_code: str = Field(..., description="Section code")
    avatar_url: str | None = Field(None, description="Avatar URL")

    @classmethod
    def from_domain(cls, user, section_code: str) -> "UserResponse":
        return cls(
            id=user.id,
            display_name=user.display_name,
            section_code=section_code,
            avatar_url=user.avatar_url,
        )


class RegisterResponse(BaseModel):
    user: UserResponse = Field(..., description="User information")
    tokens: TokenResponse = Field(..., description="Authentication tokens")


class RefreshResponse(BaseModel):
    access_token: str = Field(..., description="New JWT access token")
    refresh_token: str = Field(..., description="New refresh token (rotated)")
    token_type: str = "bearer"
    expires_in: int = 900
