from uuid import UUID

from sqlalchemy import delete, select

from app.models.group_member import GroupMember
from app.repositories.base import BaseRepository


class GroupMemberRepository(BaseRepository[GroupMember]):
    model_class = GroupMember

    async def list_by_group(self, group_id: UUID) -> list[GroupMember]:
        stmt = select(GroupMember).where(GroupMember.group_id == group_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_membership(self, group_id: UUID, user_id: UUID) -> GroupMember | None:
        stmt = select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def is_member(self, group_id: UUID, user_id: UUID) -> bool:
        return await self.exists(group_id=group_id, user_id=user_id)

    async def remove_member(self, group_id: UUID, user_id: UUID) -> None:
        stmt = delete(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id,
        )
        await self.session.execute(stmt)

    async def count_members(self, group_id: UUID) -> int:
        return await self.count(group_id=group_id)
