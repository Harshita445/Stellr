from uuid import UUID

from pydantic import BaseModel


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str


class RegistrationResult(BaseModel):
    user_id: UUID
    display_name: str
    section_code: str
    device_id: UUID
    tokens: TokenPair


class RefreshResult(BaseModel):
    user_id: UUID
    device_id: UUID
    tokens: TokenPair
