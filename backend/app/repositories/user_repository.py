import uuid

from sqlalchemy import select

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

    async def create_user(
        self,
        roll_number: str,
        display_name: str,
        section_id: uuid.UUID,
    ) -> User:
        return await self.create(
            roll_number=roll_number,
            display_name=display_name,
            section_id=section_id,
        )
