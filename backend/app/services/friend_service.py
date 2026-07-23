"""FriendService — business logic for the friends (Stars) module.

Assumptions for MVP (documented for future revisit):
1. Instant-add: adding a friend creates the friendship immediately with no
   pending state or request/accept flow. The UI calls it "send request" but
   the backend completes it atomically. If a pending state is needed later,
   add a `status` column (pending/accepted/blocked) to the friends table.
2. Search is by display_name only (never roll_number). This is a deliberate
   privacy choice — roll numbers are exposed only during auth/onboarding.
3. Friendship is bidirectional — either user can remove the other.
4. No self-friending.
"""

from uuid import UUID

from app.core.exceptions import (
    CannotFriendSelfError,
    FriendAlreadyExistsError,
    FriendNotFoundError,
    UserNotFoundError,
)
from app.repositories.friend_repository import FriendRepository
from app.repositories.user_repository import UserRepository


class FriendService:

    def __init__(
        self,
        friend_repo: FriendRepository,
        user_repo: UserRepository,
    ):
        self.friend_repo = friend_repo
        self.user_repo = user_repo

    async def add_friend(self, current_user_id: UUID, target_user_id: UUID) -> dict:
        if current_user_id == target_user_id:
            raise CannotFriendSelfError()

        target = await self.user_repo.find_by_id(target_user_id)
        if not target:
            raise UserNotFoundError()

        if await self.friend_repo.are_friends(current_user_id, target_user_id):
            raise FriendAlreadyExistsError()

        friendship = await self.friend_repo.add_friend(current_user_id, target_user_id)
        return {
            "friendship_id": friendship.id,
            "user_id": target.id,
            "display_name": target.display_name,
            "section_code": target.section.name if target.section else None,
        }

    async def remove_friend(self, current_user_id: UUID, target_user_id: UUID) -> None:
        if not await self.friend_repo.are_friends(current_user_id, target_user_id):
            raise FriendNotFoundError()
        await self.friend_repo.remove_friend(current_user_id, target_user_id)

    async def list_friends(self, user_id: UUID) -> list[dict]:
        return await self.friend_repo.get_friends_with_details(user_id)

    async def search_users(self, query: str, current_user_id: UUID) -> list[dict]:
        results = await self.user_repo.search_by_name(query, exclude_user_id=current_user_id)
        return [
            {
                "id": u.id,
                "display_name": u.display_name,
                "section_code": u.section.name if u.section else None,
            }
            for u in results
        ]
