from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class GroupMemberResponse(BaseModel):
    id: UUID = Field(..., description="Membership UUID")
    user_id: UUID = Field(..., description="User UUID")
    display_name: str = Field(..., description="Display name")
    section_code: str | None = Field(None, description="Section code e.g. CSE3A")
    joined_at: datetime = Field(..., description="When the member joined")


class GroupResponse(BaseModel):
    id: UUID = Field(..., description="Group UUID")
    name: str = Field(..., description="Group name")
    created_by: UUID | None = Field(None, description="Creator user UUID")
    member_count: int = Field(0, description="Number of members")
    created_at: datetime = Field(..., description="When the group was created")


class GroupDetailResponse(GroupResponse):
    members: list[GroupMemberResponse] = Field(
        default_factory=list,
        description="Group members",
    )


class GroupListResponse(BaseModel):
    groups: list[GroupResponse]
