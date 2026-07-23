"""Shared FastAPI dependencies.

All dependencies are request-scoped — instantiated once per request.
No global singletons. This keeps the dependency graph explicit and testable.
"""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.repositories.course_repository import CourseRepository
from app.repositories.section_repository import SectionRepository
from app.repositories.timetable_entry_repository import TimetableEntryRepository
from app.repositories.timeslot_repository import TimeslotRepository
from app.services.timetable_import_service import TimetableImportService
from app.services.timetable_parser_service import TimetableParserService
from app.services.timetable_query_service import TimetableQueryService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for the request.

    Session is auto-committed on success, rolled back on exception.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ── Service Dependencies ─────────────────────────────────────────────────

def get_timetable_parser() -> TimetableParserService:
    return TimetableParserService()


def get_timetable_import_service(
    db: AsyncSession = Depends(get_db),
) -> TimetableImportService:
    section_repo = SectionRepository(db)
    course_repo = CourseRepository(db)
    timeslot_repo = TimeslotRepository(db)
    tt_entry_repo = TimetableEntryRepository(db)
    parser = TimetableParserService()
    return TimetableImportService(
        section_repo=section_repo,
        course_repo=course_repo,
        timeslot_repo=timeslot_repo,
        tt_entry_repo=tt_entry_repo,
        parser=parser,
    )


def get_timetable_query_service(
    db: AsyncSession = Depends(get_db),
) -> TimetableQueryService:
    tt_entry_repo = TimetableEntryRepository(db)
    timeslot_repo = TimeslotRepository(db)
    return TimetableQueryService(
        tt_entry_repo=tt_entry_repo,
        timeslot_repo=timeslot_repo,
    )
