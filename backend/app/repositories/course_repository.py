from sqlalchemy import select

from app.models.course import Course
from app.repositories.base import BaseRepository


class CourseRepository(BaseRepository[Course]):
    model_class = Course

    async def find_by_code(self, code: str, department: str | None = None) -> Course | None:
        stmt = select(Course).where(Course.code == code)
        if department:
            stmt = stmt.where(Course.department == department)
        return await self.session.scalar(stmt)

    async def upsert(self, code: str, name: str, department: str | None = None) -> Course:
        existing = await self.find_by_code(code, department)
        if existing:
            return existing
        return await self.create(code=code, name=name, department=department)
