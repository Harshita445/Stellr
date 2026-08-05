import uuid

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    roll_number: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    section_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sections.id"), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    stellr_code: Mapped[str | None] = mapped_column(String(10), nullable=True, unique=True)

    section: Mapped["Section"] = relationship(  # noqa: F821
        back_populates="users", lazy="joined"
    )
    devices: Mapped[list["Device"]] = relationship(  # noqa: F821
        back_populates="user", cascade="all, delete-orphan"
    )
    friends_initiated: Mapped[list["Friend"]] = relationship(  # noqa: F821
        foreign_keys="Friend.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    friends_received: Mapped[list["Friend"]] = relationship(  # noqa: F821
        foreign_keys="Friend.friend_id",
        back_populates="friend",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_users_section", "section_id"),
    )

    def __repr__(self) -> str:
        return f"<User {self.display_name}>"
