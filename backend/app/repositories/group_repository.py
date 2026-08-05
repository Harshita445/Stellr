from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.group import Group
from app.models.group_member import GroupMember
from app.repositories.base import BaseRepository


class GroupRepository(BaseRepository[Group]):
    model_class = Group

    async def get_group_with_members(self, group_id: UUID) -> Group | None:
        stmt = (
            select(Group)
            .where(Group.id == group_id)
            .options(selectinload(Group.members).selectinload(GroupMember.user))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_groups_for_user(self, user_id: UUID) -> list[Group]:

        stmt = (
            select(Group)
            .join(GroupMember, GroupMember.group_id == Group.id)
            .where(GroupMember.user_id == user_id)
            .options(selectinload(Group.members))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
