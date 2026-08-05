from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.models.timeslot import Timeslot
from app.models.timetable_entry import TimetableEntry
from app.repositories.base import BaseRepository


class TimetableEntryRepository(BaseRepository[TimetableEntry]):
    model_class = TimetableEntry

    async def get_by_section(self, section_id: UUID, day_of_week: int | None = None) -> list[TimetableEntry]:
        stmt = (
            select(TimetableEntry)
            .options(selectinload(TimetableEntry.course), selectinload(TimetableEntry.timeslot))
            .where(TimetableEntry.section_id == section_id)
        )
        if day_of_week is not None:
            stmt = stmt.join(TimetableEntry.timeslot).where(
                TimetableEntry.timeslot.has(day_of_week=day_of_week)
            )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_sections(self, section_ids: list[UUID], day_of_week: int) -> dict[UUID, list[TimetableEntry]]:
        stmt = (
            select(TimetableEntry)
            .options(selectinload(TimetableEntry.timeslot))
            .where(TimetableEntry.section_id.in_(section_ids))
            .join(TimetableEntry.timeslot)
            .where(Timeslot.day_of_week == day_of_week)
        )
        result = await self.session.execute(stmt)
        entries: dict[UUID, list[TimetableEntry]] = {sid: [] for sid in section_ids}
        for entry in result.scalars().all():
            entries[entry.section_id].append(entry)
        return entries

    async def delete_by_section(self, section_id: UUID) -> None:
        stmt = delete(TimetableEntry).where(TimetableEntry.section_id == section_id)
        await self.session.execute(stmt)

    async def bulk_insert(self, entries: list[dict]) -> list[TimetableEntry]:
        instances = [TimetableEntry(**data) for data in entries]
        self.session.add_all(instances)
        await self.session.flush()
        return instances

    async def count_by_section(self, section_id: UUID) -> int:
        stmt = select(TimetableEntry).where(TimetableEntry.section_id == section_id)
        result = await self.session.execute(stmt)
        return len(result.scalars().all())
