import asyncio
import uuid

from app.core.config import settings
from app.core.exceptions import AuthenticationError, DeviceNotFoundError, UserNotFoundError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    hash_token,
    verify_token,
)
from app.repositories.device_repository import DeviceRepository
from app.repositories.section_repository import SectionRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth.internal import RefreshResult, RegistrationResult, TokenPair


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        device_repo: DeviceRepository,
        section_repo: SectionRepository,
    ):
        self.user_repo = user_repo
        self.device_repo = device_repo
        self.section_repo = section_repo

    async def register(
        self,
        roll_number: str,
        display_name: str,
        section_code: str,
    ) -> RegistrationResult:
        section = await self.section_repo.find_by_name(section_code.upper())
        if not section:
            dept, sem = _derive_department_semester_plain(section_code)
            section = await self.section_repo.upsert(
                name=section_code.upper(),
                department=dept,
                semester=sem,
                academic_year="2025-2026",
            )

        user = await self.user_repo.find_by_roll_number(roll_number)
        if user:
            return RegistrationResult(
                user_id=user.id,
                display_name=user.display_name,
                section_code=section.name,
                stellr_code=user.stellr_code,
                device_id=None,
                tokens=None,
                is_new_account=False,
            )

        await asyncio.sleep(settings.AUTH.ENUMERATION_PREVENTION_DELAY)
        user = await self.user_repo.create_user(
            roll_number=roll_number,
            display_name=display_name,
            section_id=section.id,
        )

        refresh_token = create_refresh_token()
        refresh_hash = hash_token(refresh_token)
        device = await self.device_repo.create_device(
            user_id=user.id,
            refresh_token_hash=refresh_hash,
        )

        access_token = create_access_token(user.id, device.id)

        return RegistrationResult(
            user_id=user.id,
            display_name=user.display_name,
            section_code=section.name,
            stellr_code=user.stellr_code,
            device_id=device.id,
            tokens=TokenPair(
                access_token=access_token,
                refresh_token=refresh_token,
            ),
            is_new_account=True,
        )

    async def claim(
        self,
        roll_number: str,
        section_code: str,
    ) -> RegistrationResult:
        section = await self.section_repo.find_by_name(section_code.upper())
        if not section:
            dept, sem = _derive_department_semester_plain(section_code)
            section = await self.section_repo.upsert(
                name=section_code.upper(),
                department=dept,
                semester=sem,
                academic_year="2025-2026",
            )

        user = await self.user_repo.find_by_roll_number(roll_number)
        if not user:
            raise UserNotFoundError()

        await self.device_repo.deactivate_all_for_user(user.id)

        refresh_token = create_refresh_token()
        refresh_hash = hash_token(refresh_token)
        device = await self.device_repo.create_device(
            user_id=user.id,
            refresh_token_hash=refresh_hash,
        )

        access_token = create_access_token(user.id, device.id)

        return RegistrationResult(
            user_id=user.id,
            display_name=user.display_name,
            section_code=section.name,
            stellr_code=user.stellr_code,
            device_id=device.id,
            tokens=TokenPair(
                access_token=access_token,
                refresh_token=refresh_token,
            ),
            is_new_account=False,
        )

    async def refresh(self, refresh_token: str, device_id: uuid.UUID) -> RefreshResult:
        device = await self.device_repo.find_by_id(device_id)
        if not device:
            raise DeviceNotFoundError()

        if not verify_token(refresh_token, device.refresh_token_hash):
            raise AuthenticationError("Invalid refresh token")

        new_refresh_token = create_refresh_token()
        new_hash = hash_token(new_refresh_token)
        await self.device_repo.update_refresh_token(device.id, new_hash)

        access_token = create_access_token(device.user_id, device.id)

        return RefreshResult(
            user_id=device.user_id,
            device_id=device.id,
            tokens=TokenPair(
                access_token=access_token,
                refresh_token=new_refresh_token,
            ),
        )


def _derive_department_semester_plain(section_code: str) -> tuple[str, int]:
    code = section_code.upper().strip()
    import re
    match = re.match(r"([A-Z]+)(\d+)([A-Z]?)", code)
    if match:
        department = match.group(1)
        year = int(match.group(2))
        semester = year * 2 - 1
        return department, semester
    return "General", 1
