from uuid import UUID

from pydantic import BaseModel


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str


class RegistrationResult(BaseModel):
    user_id: UUID
    display_name: str
    section_code: str
    stellr_code: str | None
    device_id: UUID | None
    tokens: TokenPair | None
    is_new_account: bool


class RefreshResult(BaseModel):
    user_id: UUID
    device_id: UUID
    tokens: TokenPair
