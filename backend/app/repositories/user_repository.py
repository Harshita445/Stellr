import uuid
import secrets
import string

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model_class = User

    async def find_by_roll_number(self, roll_number: str) -> User | None:
        stmt = select(User).where(User.roll_number == roll_number)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_id(self, user_id: uuid.UUID) -> User | None:
        return await self.get(user_id)

    async def find_by_stellr_code(self, code: str) -> User | None:
        stmt = select(User).where(User.stellr_code == code.upper())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(
        self,
        roll_number: str,
        display_name: str,
        section_id: uuid.UUID,
    ) -> User:
        stellr_code = await self._generate_unique_code(display_name)
        return await self.create(
            roll_number=roll_number,
            display_name=display_name,
            section_id=section_id,
            stellr_code=stellr_code,
        )

    async def search_by_name(
        self, query: str, exclude_user_id: uuid.UUID | None = None, limit: int = 20
    ) -> list[User]:
        stmt = (
            select(User)
            .options(selectinload(User.section))
            .where(User.display_name.ilike(f"%{query}%"))
            .limit(limit)
        )
        if exclude_user_id is not None:
            stmt = stmt.where(User.id != exclude_user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def _generate_unique_code(self, display_name: str) -> str:
        prefix = "".join(c for c in display_name.upper() if c.isalpha())[:4]
        if not prefix:
            prefix = "STAR"
        for _ in range(10):
            suffix = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
            code = f"{prefix}-{suffix}"
            existing = await self.find_by_stellr_code(code)
            if not existing:
                return code
        suffix = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        return f"STR-{suffix}"
