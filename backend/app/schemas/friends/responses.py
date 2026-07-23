from uuid import UUID

from pydantic import BaseModel, Field


class FriendUserResponse(BaseModel):
    id: UUID = Field(..., description="User UUID")
    display_name: str = Field(..., description="Display name")
    section_code: str | None = Field(None, description="Section code e.g. CSE3A")


class FriendResponse(BaseModel):
    id: UUID = Field(..., description="Friend relationship UUID")
    user: FriendUserResponse


class FriendListResponse(BaseModel):
    friends: list[FriendResponse]


class FriendSearchResponse(BaseModel):
    id: UUID = Field(..., description="User UUID")
    display_name: str = Field(..., description="Display name")
    section_code: str | None = Field(None, description="Section code e.g. CSE3A")
