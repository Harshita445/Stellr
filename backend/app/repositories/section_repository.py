from uuid import UUID

from sqlalchemy import select

from app.models.section import Section
from app.repositories.base import BaseRepository


class SectionRepository(BaseRepository[Section]):
    model_class = Section

    async def find_by_name_and_department(
        self, name: str, department: str, semester: int, academic_year: str
    ) -> Section | None:
        stmt = select(Section).where(
            Section.name == name,
            Section.department == department,
            Section.semester == semester,
            Section.academic_year == academic_year,
        )
        return await self.session.scalar(stmt)

    async def upsert(self, name: str, department: str, semester: int, academic_year: str) -> Section:
        existing = await self.find_by_name_and_department(name, department, semester, academic_year)
        if existing:
            return existing
        return await self.create(
            name=name,
            department=department,
            semester=semester,
            academic_year=academic_year,
        )

    async def find_by_ids(self, ids: list[UUID]) -> dict[UUID, Section]:
        stmt = select(Section).where(Section.id.in_(ids))
        result = await self.session.execute(stmt)
        return {row.id: row for row in result.scalars().all()}
