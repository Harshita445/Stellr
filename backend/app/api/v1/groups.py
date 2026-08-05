"""Groups (Constellations) API routes.

Design:
- Creating a group auto-adds the creator as a member.
- Any existing user can be added as a member (no friend-gate for MVP).
- Delete is creator-only. Leave/remove is handled via the same endpoint
  (DELETE /groups/{id}/members/{uuid}) — if the UUID matches the current
  user it's a self-leave; otherwise only the creator can remove.
- Rename is creator-only.
"""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import (
    get_current_user,
    get_group_service,
)
from app.schemas.groups.requests import (
    AddGroupMemberRequest,
    CreateGroupRequest,
    RenameGroupRequest,
)
from app.schemas.groups.responses import (
    GroupDetailResponse,
    GroupListResponse,
    GroupMemberResponse,
    GroupResponse,
)
from app.services.group_service import GroupService

router = APIRouter(tags=["Groups"])


@router.get("/", response_model=GroupListResponse)
async def list_groups(
    current_user: dict = Depends(get_current_user),
    group_service: GroupService = Depends(get_group_service),
):
    groups = await group_service.list_groups(current_user["user_id"])
    return GroupListResponse(
        groups=[
            GroupResponse(
                id=g["id"],
                name=g["name"],
                created_by=g["created_by"],
                member_count=g["member_count"],
                created_at=g["created_at"],
            )
            for g in groups
        ]
    )


@router.post("/", response_model=GroupDetailResponse, status_code=201)
async def create_group(
    body: CreateGroupRequest,
    current_user: dict = Depends(get_current_user),
    group_service: GroupService = Depends(get_group_service),
):
    result = await group_service.create_group(
        name=body.name,
        creator_id=current_user["user_id"],
        member_ids=body.member_ids,
    )
    return GroupDetailResponse(
        id=result["id"],
        name=result["name"],
        created_by=result["created_by"],
        member_count=result["member_count"],
        created_at=result["created_at"],
        members=[
            GroupMemberResponse(
                id=m["id"],
                user_id=m["user_id"],
                display_name=m["display_name"],
                section_code=m["section_code"],
                joined_at=m["joined_at"],
            )
            for m in result["members"]
        ],
    )


@router.get("/{group_id}", response_model=GroupDetailResponse)
async def get_group_detail(
    group_id: UUID,
    current_user: dict = Depends(get_current_user),
    group_service: GroupService = Depends(get_group_service),
):
    result = await group_service.get_group_detail(group_id, current_user["user_id"])
    return GroupDetailResponse(
        id=result["id"],
        name=result["name"],
        created_by=result["created_by"],
        member_count=result["member_count"],
        created_at=result["created_at"],
        members=[
            GroupMemberResponse(
                id=m["id"],
                user_id=m["user_id"],
                display_name=m["display_name"],
                section_code=m["section_code"],
                joined_at=m["joined_at"],
            )
            for m in result["members"]
        ],
    )


@router.patch("/{group_id}", response_model=GroupDetailResponse)
async def rename_group(
    group_id: UUID,
    body: RenameGroupRequest,
    current_user: dict = Depends(get_current_user),
    group_service: GroupService = Depends(get_group_service),
):
    result = await group_service.rename_group(
        group_id=group_id,
        name=body.name,
        current_user_id=current_user["user_id"],
    )
    return GroupDetailResponse(
        id=result["id"],
        name=result["name"],
        created_by=result["created_by"],
        member_count=result["member_count"],
        created_at=result["created_at"],
        members=[
            GroupMemberResponse(
                id=m["id"],
                user_id=m["user_id"],
                display_name=m["display_name"],
                section_code=m["section_code"],
                joined_at=m["joined_at"],
            )
            for m in result["members"]
        ],
    )


@router.delete("/{group_id}", status_code=204)
async def delete_group(
    group_id: UUID,
    current_user: dict = Depends(get_current_user),
    group_service: GroupService = Depends(get_group_service),
):
    await group_service.delete_group(group_id, current_user["user_id"])


@router.post("/{group_id}/members", response_model=GroupMemberResponse, status_code=201)
async def add_member(
    group_id: UUID,
    body: AddGroupMemberRequest,
    current_user: dict = Depends(get_current_user),
    group_service: GroupService = Depends(get_group_service),
):
    result = await group_service.add_member(
        group_id=group_id,
        target_user_id=UUID(body.user_id),
        current_user_id=current_user["user_id"],
    )
    return GroupMemberResponse(
        id=result["id"],
        user_id=result["user_id"],
        display_name=result["display_name"],
        section_code=result["section_code"],
        joined_at=result["joined_at"],
    )


@router.delete("/{group_id}/members/{user_id}", status_code=204)
async def remove_member(
    group_id: UUID,
    user_id: UUID,
    current_user: dict = Depends(get_current_user),
    group_service: GroupService = Depends(get_group_service),
):
    await group_service.remove_member(
        group_id=group_id,
        target_user_id=user_id,
        current_user_id=current_user["user_id"],
    )
