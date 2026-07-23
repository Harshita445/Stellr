"""Shared FastAPI dependencies.

All dependencies are request-scoped — instantiated once per request.
No global singletons. This keeps the dependency graph explicit and testable.
"""

from collections.abc import AsyncGenerator
from uuid import UUID

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.core.exceptions import AuthenticationError
from app.core.middleware import get_rate_limiter, InMemoryRateLimiter
from app.core.security import decode_access_token
from app.repositories.course_repository import CourseRepository
from app.repositories.device_repository import DeviceRepository
from app.repositories.friend_repository import FriendRepository
from app.repositories.group_member_repository import GroupMemberRepository
from app.repositories.group_repository import GroupRepository
from app.repositories.section_repository import SectionRepository
from app.repositories.timetable_entry_repository import TimetableEntryRepository
from app.repositories.timeslot_repository import TimeslotRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.dashboard_service import DashboardService
from app.services.friend_service import FriendService
from app.services.group_service import GroupService
from app.services.timetable_import_service import TimetableImportService
from app.services.timetable_parser_service import TimetableParserService
from app.services.timetable_query_service import TimetableQueryService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ── Rate Limiter ─────────────────────────────────────────────────────

def get_rate_limit() -> InMemoryRateLimiter:
    return get_rate_limiter()


# ── Repository Dependencies ──────────────────────────────────────────

def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_device_repo(db: AsyncSession = Depends(get_db)) -> DeviceRepository:
    return DeviceRepository(db)


def get_section_repo(db: AsyncSession = Depends(get_db)) -> SectionRepository:
    return SectionRepository(db)


def get_course_repo(db: AsyncSession = Depends(get_db)) -> CourseRepository:
    return CourseRepository(db)


def get_timeslot_repo(db: AsyncSession = Depends(get_db)) -> TimeslotRepository:
    return TimeslotRepository(db)


def get_tt_entry_repo(db: AsyncSession = Depends(get_db)) -> TimetableEntryRepository:
    return TimetableEntryRepository(db)


def get_friend_repo(db: AsyncSession = Depends(get_db)) -> FriendRepository:
    return FriendRepository(db)


# ── Service Dependencies ─────────────────────────────────────────────

def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repo),
    device_repo: DeviceRepository = Depends(get_device_repo),
    section_repo: SectionRepository = Depends(get_section_repo),
) -> AuthService:
    return AuthService(
        user_repo=user_repo,
        device_repo=device_repo,
        section_repo=section_repo,
    )


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


def get_friend_service(
    friend_repo: FriendRepository = Depends(get_friend_repo),
    user_repo: UserRepository = Depends(get_user_repo),
) -> FriendService:
    return FriendService(
        friend_repo=friend_repo,
        user_repo=user_repo,
    )


# ── Repository Dependencies (Groups) ─────────────────────────────────

def get_group_repo(db: AsyncSession = Depends(get_db)) -> GroupRepository:
    return GroupRepository(db)


def get_group_member_repo(db: AsyncSession = Depends(get_db)) -> GroupMemberRepository:
    return GroupMemberRepository(db)


def get_group_service(
    group_repo: GroupRepository = Depends(get_group_repo),
    group_member_repo: GroupMemberRepository = Depends(get_group_member_repo),
    user_repo: UserRepository = Depends(get_user_repo),
) -> GroupService:
    return GroupService(
        group_repo=group_repo,
        group_member_repo=group_member_repo,
        user_repo=user_repo,
    )


# ── Dashboard Service Dependencies ────────────────────────────────────

def get_dashboard_service(
    user_repo: UserRepository = Depends(get_user_repo),
    tt_entry_repo: TimetableEntryRepository = Depends(get_tt_entry_repo),
    timeslot_repo: TimeslotRepository = Depends(get_timeslot_repo),
) -> DashboardService:
    return DashboardService(
        user_repo=user_repo,
        tt_entry_repo=tt_entry_repo,
        timeslot_repo=timeslot_repo,
    )


# ── Auth Dependencies ────────────────────────────────────────────────

async def get_current_user(
    authorization: str = Header(..., description="Bearer <jwt>"),
    device_id: str = Header(..., alias="X-Device-ID", description="Device UUID from registration"),
):
    if not authorization.startswith("Bearer "):
        raise AuthenticationError("Invalid authorization header")
    token = authorization.removeprefix("Bearer ")
    payload = decode_access_token(token)
    token_device_id = payload.get("did")
    token_user_id = payload.get("sub")
    if not token_device_id or not token_user_id:
        raise AuthenticationError("Invalid token payload")
    if token_device_id != device_id:
        raise AuthenticationError("Device mismatch — token is bound to a different device")
    return {
        "user_id": UUID(token_user_id),
        "device_id": UUID(token_device_id),
    }
