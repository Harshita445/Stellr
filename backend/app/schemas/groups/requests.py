from pydantic import BaseModel, Field


class CreateGroupRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Group name (1-100 characters)",
    )
    member_ids: list[str] = Field(
        default_factory=list,
        description="Initial member UUIDs (creator is always included)",
    )


class AddGroupMemberRequest(BaseModel):
    user_id: str = Field(..., description="User UUID to add")


class RenameGroupRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="New group name (1-100 characters)",
    )
