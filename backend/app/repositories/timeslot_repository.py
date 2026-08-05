from sqlalchemy import select

from app.models.timeslot import Timeslot
from app.repositories.base import BaseRepository


class TimeslotRepository(BaseRepository[Timeslot]):
    model_class = Timeslot

    async def find_by_day_and_slot(self, day_of_week: int, slot_index: int) -> Timeslot | None:
        stmt = select(Timeslot).where(
            Timeslot.day_of_week == day_of_week,
            Timeslot.slot_index == slot_index,
        )
        return await self.session.scalar(stmt)

    async def upsert(
        self,
        day_of_week: int,
        slot_index: int,
        start_time: str,
        end_time: str,
        slot_type: str = "lecture",
        venue: str | None = None,
    ) -> Timeslot:
        existing = await self.find_by_day_and_slot(day_of_week, slot_index)
        if existing:
            return existing
        return await self.create(
            day_of_week=day_of_week,
            slot_index=slot_index,
            start_time=start_time,
            end_time=end_time,
            slot_type=slot_type,
            venue=venue,
        )

    async def get_all(self) -> list[Timeslot]:
        stmt = select(Timeslot).order_by(Timeslot.day_of_week, Timeslot.slot_index)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_all(self) -> None:
        from sqlalchemy import delete
        await self.session.execute(delete(Timeslot))
