"""FriendRepository — data access for the friends table.

Bidirectional single-row design: a friendship between A and B is stored
as one row. Queries use UNION to find friends in both directions.
"""

from uuid import UUID

from sqlalchemy import delete, or_, select, union
from sqlalchemy.orm import selectinload

from app.models.friend import Friend
from app.repositories.base import BaseRepository


class FriendRepository(BaseRepository[Friend]):
    model_class = Friend

    async def add_friend(self, user_id: UUID, friend_id: UUID) -> Friend:
        return await self.create(user_id=user_id, friend_id=friend_id)

    async def remove_friend(self, user_id: UUID, friend_id: UUID) -> None:
        stmt = delete(Friend).where(
            or_(
                (Friend.user_id == user_id) & (Friend.friend_id == friend_id),
                (Friend.user_id == friend_id) & (Friend.friend_id == user_id),
            )
        )
        await self.session.execute(stmt)

    async def are_friends(self, user_id: UUID, friend_id: UUID) -> bool:
        stmt = select(Friend).where(
            or_(
                (Friend.user_id == user_id) & (Friend.friend_id == friend_id),
                (Friend.user_id == friend_id) & (Friend.friend_id == user_id),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_friend_ids(self, user_id: UUID) -> list[UUID]:
        q1 = select(Friend.friend_id).where(Friend.user_id == user_id)
        q2 = select(Friend.user_id).where(Friend.friend_id == user_id)
        stmt = union(q1, q2)
        result = await self.session.execute(stmt)
        return [row[0] for row in result.all()]

    async def get_friends_with_details(self, user_id: UUID) -> list[dict]:
        q1 = (
            select(Friend)
            .where(Friend.user_id == user_id)
            .options(selectinload(Friend.friend))
        )
        q2 = (
            select(Friend)
            .where(Friend.friend_id == user_id)
            .options(selectinload(Friend.user))
        )
        r1 = await self.session.execute(q1)
        r2 = await self.session.execute(q2)
        results: list[dict] = []
        for row in r1.scalars().all():
            u = row.friend
            results.append({
                "friendship_id": row.id,
                "user_id": u.id,
                "display_name": u.display_name,
                "section_code": u.section.name if u.section else None,
            })
        for row in r2.scalars().all():
            u = row.user
            results.append({
                "friendship_id": row.id,
                "user_id": u.id,
                "display_name": u.display_name,
                "section_code": u.section.name if u.section else None,
            })
        return results
