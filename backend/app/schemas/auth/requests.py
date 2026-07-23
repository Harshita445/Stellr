from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=100, description="User's display name")
    roll_number: str = Field(..., min_length=1, max_length=20, description="Institutional roll number")
    section_code: str = Field(..., min_length=1, max_length=20, description="Section code (e.g. CSE3A)")


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token issued during registration")
