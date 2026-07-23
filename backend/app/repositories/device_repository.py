import uuid

from sqlalchemy import delete, select, update

from app.models.device import Device
from app.repositories.base import BaseRepository


class DeviceRepository(BaseRepository[Device]):
    model_class = Device

    async def find_by_user_id(self, user_id: uuid.UUID) -> Device | None:
        stmt = select(Device).where(Device.user_id == user_id).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_id(self, device_id: uuid.UUID) -> Device | None:
        return await self.get(device_id)

    async def create_device(
        self,
        user_id: uuid.UUID,
        refresh_token_hash: str,
        device_name: str | None = None,
    ) -> Device:
        return await self.create(
            user_id=user_id,
            refresh_token_hash=refresh_token_hash,
            device_name=device_name,
        )

    async def update_refresh_token(self, device_id: uuid.UUID, new_hash: str) -> None:
        stmt = update(Device).where(Device.id == device_id).values(
            refresh_token_hash=new_hash,
        )
        await self.session.execute(stmt)

    async def deactivate_all_for_user(self, user_id: uuid.UUID) -> None:
        stmt = delete(Device).where(Device.user_id == user_id)
        await self.session.execute(stmt)
