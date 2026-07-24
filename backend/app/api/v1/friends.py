"""Friends (Stars) API routes.

Search is by display_name only (never roll number). This is a deliberate
privacy choice — roll numbers are auth-internal only.

Add friend is instant-add (no pending state) for MVP. See FriendService
docstring for assumptions.

Rate limiting on search: 30 requests per 60 seconds per user.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import (
    get_current_user,
    get_friend_service,
    get_rate_limit,
    get_user_repo,
)
from app.core.middleware import InMemoryRateLimiter
from app.repositories.user_repository import UserRepository
from app.schemas.friends.responses import (
    FriendListResponse,
    FriendResponse,
    FriendSearchResponse,
    FriendUserResponse,
)
from app.services.friend_service import FriendService

router = APIRouter(tags=["Friends"])


@router.get("/", response_model=FriendListResponse)
async def list_friends(
    current_user: dict = Depends(get_current_user),
    friend_service: FriendService = Depends(get_friend_service),
):
    friends = await friend_service.list_friends(current_user["user_id"])
    return FriendListResponse(
        friends=[
            FriendResponse(
                id=f["friendship_id"],
                user=FriendUserResponse(
                    id=f["user_id"],
                    display_name=f["display_name"],
                    section_code=f["section_code"],
                ),
            )
            for f in friends
        ]
    )


@router.get("/search", response_model=list[FriendSearchResponse])
async def search_users(
    q: str = Query(..., min_length=3, description="Search by display name (min 3 chars)"),
    current_user: dict = Depends(get_current_user),
    friend_service: FriendService = Depends(get_friend_service),
    rate_limiter: InMemoryRateLimiter = Depends(get_rate_limit),
):
    rate_limiter.check(f"search:{current_user['user_id']}", 30, 60)
    results = await friend_service.search_users(q, current_user["user_id"])
    return [
        FriendSearchResponse(
            id=r["id"],
            display_name=r["display_name"],
            section_code=r["section_code"],
        )
        for r in results
    ]


@router.post("/{user_id}", status_code=201)
async def add_friend(
    user_id: UUID,
    current_user: dict = Depends(get_current_user),
    friend_service: FriendService = Depends(get_friend_service),
):
    result = await friend_service.add_friend(current_user["user_id"], user_id)
    return {
        "friendship_id": result["friendship_id"],
        "user": {
            "id": result["user_id"],
            "display_name": result["display_name"],
            "section_code": result["section_code"],
        },
    }


@router.get("/search-by-code", response_model=list[FriendSearchResponse])
async def search_by_code(
    code: str = Query(..., min_length=4, description="Stellr code to search"),
    current_user: dict = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repo),
):
    user = await user_repo.find_by_stellr_code(code)
    if not user or user.id == current_user["user_id"]:
        return []
    return [
        FriendSearchResponse(
            id=user.id,
            display_name=user.display_name,
            section_code=user.section.name if user.section else None,
        )
    ]


@router.delete("/{user_id}", status_code=204)
async def remove_friend(
    user_id: UUID,
    current_user: dict = Depends(get_current_user),
    friend_service: FriendService = Depends(get_friend_service),
):
    await friend_service.remove_friend(current_user["user_id"], user_id)
