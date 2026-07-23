"""Abstract CRUD repository.

Every repository in the application extends this to get common operations.
Repositories own data access — they execute queries and return ORM models
(or simple dicts for aggregate queries). They never contain business logic.

Design rules:
- Repositories return ORM models or primitives, never Pydantic schemas.
- Repositories never catch domain exceptions (service layer translates).
- Batch operations return dicts keyed by parent ID for O(1) service lookups.
- Repositories do NOT cache — caching is a service concern.
"""

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    model_class: type[T]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: UUID) -> T | None:
        return await self.session.get(self.model_class, id)

    async def get_or_raise(self, id: UUID) -> T:
        instance = await self.get(id)
        if not instance:
            from app.core.exceptions import UserNotFoundError
            raise UserNotFoundError()
        return instance

    async def list(
        self,
        *whereclause,
        limit: int = 100,
        offset: int = 0,
        order_by: str | None = None,
    ) -> list[T]:
        stmt = select(self.model_class)
        if whereclause:
            stmt = stmt.where(*whereclause)
        if order_by:
            stmt = stmt.order_by(order_by)
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, **data) -> T:
        instance = self.model_class(**data)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def update(self, id: UUID, **data) -> T:
        instance = await self.get_or_raise(id)
        for key, value in data.items():
            setattr(instance, key, value)
        await self.session.flush()
        return instance

    async def delete(self, id: UUID) -> None:
        instance = await self.get_or_raise(id)
        await self.session.delete(instance)
        await self.session.flush()

    async def exists(self, **filters) -> bool:
        stmt = select(self.model_class).filter_by(**filters).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def count(self, **filters) -> int:
        stmt = select(func.count()).select_from(self.model_class).filter_by(**filters)
        result = await self.session.execute(stmt)
        return result.scalar_one()
