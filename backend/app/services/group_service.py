"""GroupService — business logic for the Groups (Constellations) module.

Design decisions (MVP):
1. Creator is auto-added as a member when the group is created.
2. Initial members (passed via member_ids) are validated — every UUID must
   exist in the users table. Non-existent UUIDs raise UserNotFoundError.
3. No friend-gate: any existing user can be added. This keeps initial
   friction low. If spam becomes an issue, add a friend-only check.
4. Delete is creator-only. Non-creators can leave on their own.
5. Leave vs. remove: DELETE /groups/{id}/members/{uuid} handles both —
   if user_id == current_user, it's self-leave; otherwise only creator can
   remove others. See the API route for logic (the service handles
   the actual removal in both cases).
6. Group name is limited to 100 chars (DB constraint is VARCHAR(100),
   validated at schema level by Pydantic).
"""

from uuid import UUID

from app.core.exceptions import (
    GroupNotFoundError,
    GroupNameTooLongError,
    NotGroupCreatorError,
    NotGroupMemberError,
    UserNotFoundError,
)
from app.repositories.group_member_repository import GroupMemberRepository
from app.repositories.group_repository import GroupRepository
from app.repositories.user_repository import UserRepository


class GroupService:

    def __init__(
        self,
        group_repo: GroupRepository,
        group_member_repo: GroupMemberRepository,
        user_repo: UserRepository,
    ):
        self.group_repo = group_repo
        self.group_member_repo = group_member_repo
        self.user_repo = user_repo

    async def create_group(
        self,
        name: str,
        creator_id: UUID,
        member_ids: list[str],
    ) -> dict:
        if len(name) > 100:
            raise GroupNameTooLongError()

        # Resolve initial member UUIDs and validate they exist
        initial_member_uuids: list[UUID] = []
        for mid in member_ids:
            uid = UUID(mid)
            user = await self.user_repo.find_by_id(uid)
            if not user:
                raise UserNotFoundError()
            initial_member_uuids.append(uid)

        # Create the group
        group = await self.group_repo.create(name=name, created_by=creator_id)

        # Add creator
        await self.group_member_repo.create(group_id=group.id, user_id=creator_id)

        # Add initial members (skip if already the creator)
        seen = {creator_id}
        for uid in initial_member_uuids:
            if uid not in seen:
                await self.group_member_repo.create(group_id=group.id, user_id=uid)
                seen.add(uid)

        return await self._build_group_detail(group.id)

    async def get_group_detail(self, group_id: UUID, current_user_id: UUID) -> dict:
        group = await self.group_repo.get_group_with_members(group_id)
        if not group:
            raise GroupNotFoundError()

        if not await self.group_member_repo.is_member(group_id, current_user_id):
            raise NotGroupMemberError()

        return await self._build_group_detail(group_id)

    async def list_groups(self, user_id: UUID) -> list[dict]:
        groups = await self.group_repo.list_groups_for_user(user_id)
        result: list[dict] = []
        for g in groups:
            result.append({
                "id": g.id,
                "name": g.name,
                "created_by": g.created_by,
                "member_count": len(g.members),
                "created_at": g.created_at,
            })
        return result

    async def rename_group(self, group_id: UUID, name: str, current_user_id: UUID) -> dict:
        if len(name) > 100:
            raise GroupNameTooLongError()

        group = await self.group_repo.get(group_id)
        if not group:
            raise GroupNotFoundError()

        if group.created_by != current_user_id:
            raise NotGroupCreatorError()

        await self.group_repo.update(group_id, name=name)
        return await self._build_group_detail(group_id)

    async def delete_group(self, group_id: UUID, current_user_id: UUID) -> None:
        group = await self.group_repo.get(group_id)
        if not group:
            raise GroupNotFoundError()

        if group.created_by != current_user_id:
            raise NotGroupCreatorError()

        await self.group_repo.delete(group_id)

    async def add_member(self, group_id: UUID, target_user_id: UUID, current_user_id: UUID) -> dict:
        group = await self.group_repo.get(group_id)
        if not group:
            raise GroupNotFoundError()

        if not await self.group_member_repo.is_member(group_id, current_user_id):
            raise NotGroupMemberError()

        target = await self.user_repo.find_by_id(target_user_id)
        if not target:
            raise UserNotFoundError()

        membership = await self.group_member_repo.create(
            group_id=group_id,
            user_id=target_user_id,
        )
        return {
            "id": membership.id,
            "user_id": target_user_id,
            "display_name": target.display_name,
            "section_code": target.section.name if target.section else None,
            "joined_at": membership.created_at,
        }

    async def remove_member(self, group_id: UUID, target_user_id: UUID, current_user_id: UUID) -> None:
        group = await self.group_repo.get(group_id)
        if not group:
            raise GroupNotFoundError()

        # If removing someone else, must be creator
        if target_user_id != current_user_id and group.created_by != current_user_id:
            raise NotGroupCreatorError()

        if not await self.group_member_repo.is_member(group_id, target_user_id):
            raise NotGroupMemberError()

        await self.group_member_repo.remove_member(group_id, target_user_id)

    async def _build_group_detail(self, group_id: UUID) -> dict:
        group = await self.group_repo.get_group_with_members(group_id)
        if not group:
            raise GroupNotFoundError()

        members = []
        for gm in group.members:
            members.append({
                "id": gm.id,
                "user_id": gm.user_id,
                "display_name": gm.user.display_name,
                "section_code": gm.user.section.name if gm.user.section else None,
                "joined_at": gm.created_at,
            })

        return {
            "id": group.id,
            "name": group.name,
            "created_by": group.created_by,
            "member_count": len(members),
            "created_at": group.created_at,
            "members": members,
        }
