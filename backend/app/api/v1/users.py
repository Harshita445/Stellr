"""Users API routes.

Profile information for the current authenticated user.
"""

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_user_repo
from app.repositories.user_repository import UserRepository
from app.schemas.auth.responses import UserResponse

router = APIRouter(tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: dict = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repo),
):
    user = await user_repo.find_by_id(current_user["user_id"])
    return UserResponse(
        id=user.id,
        display_name=user.display_name,
        section_code=user.section.name if user.section else None,
        stellr_code=user.stellr_code,
        avatar_url=user.avatar_url,
    )
