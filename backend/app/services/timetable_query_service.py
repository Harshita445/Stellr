"""Timetable Query Service

Read-only timetable lookups for normal user requests.
This is the ONLY timetable service used outside of the admin import flow.
The workbook is NEVER touched here — data comes exclusively from PostgreSQL.

Caching strategy (Phase 2+):
- Results cached by (section_id, day_of_week) with TTL up to 1 hour
- Cache invalidated on timetable import
"""

from datetime import date, datetime, time, timedelta
from uuid import UUID

from app.models.timeslot import DAYS_OF_WEEK
from app.repositories.timetable_entry_repository import TimetableEntryRepository
from app.repositories.timeslot_repository import TimeslotRepository


class TimetableQueryService:
    """Read-only timetable lookups. Used by AvailabilityService."""

    def __init__(
        self,
        tt_entry_repo: TimetableEntryRepository,
        timeslot_repo: TimeslotRepository,
    ):
        self.tt_entry_repo = tt_entry_repo
        self.timeslot_repo = timeslot_repo

    async def get_section_schedule(
        self, section_id: UUID, day_of_week: int
    ) -> list[dict]:
        """Get all timetable entries for a section on a given day."""
        entries = await self.tt_entry_repo.get_by_section(section_id, day_of_week)
        return [
            {
                "timeslot_id": e.timeslot_id,
                "course_id": e.course_id,
                "course_code": e.course.code if e.course else None,
                "course_name": e.course.name if e.course else None,
                "day_of_week": e.timeslot.day_of_week if e.timeslot else None,
                "start_time": e.timeslot.start_time if e.timeslot else None,
                "end_time": e.timeslot.end_time if e.timeslot else None,
                "slot_index": e.timeslot.slot_index if e.timeslot else None,
            }
            for e in entries
        ]

    async def get_section_schedules(
        self, section_ids: list[UUID], day_of_week: int
    ) -> dict[UUID, list[dict]]:
        """Batch schedule lookup for multiple sections."""
        by_section = await self.tt_entry_repo.get_by_sections(section_ids, day_of_week)
        return {
            sid: [
                {
                    "timeslot_id": e.timeslot_id,
                    "course_id": e.course_id,
                    "course_code": e.course.code if e.course else None,
                    "course_name": e.course.name if e.course else None,
                    "start_time": e.timeslot.start_time if e.timeslot else None,
                    "end_time": e.timeslot.end_time if e.timeslot else None,
                    "slot_index": e.timeslot.slot_index if e.timeslot else None,
                }
                for e in entries
            ]
            for sid, entries in by_section.items()
        }
