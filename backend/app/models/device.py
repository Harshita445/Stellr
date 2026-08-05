import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Device(Base):
    __tablename__ = "devices"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    device_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    refresh_token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    last_used_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="devices")

    __table_args__ = (
        Index("idx_devices_user", "user_id"),
    )

    def __repr__(self) -> str:
        return f"<Device {self.id} for user {self.user_id}>"
