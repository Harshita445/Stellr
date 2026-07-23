import uuid

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class GroupMember(Base):
    __tablename__ = "group_members"

    group_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    group: Mapped["Group"] = relationship(back_populates="members")  # noqa: F821
    user: Mapped["User"] = relationship(lazy="joined")  # noqa: F821

    __table_args__ = (
        UniqueConstraint("group_id", "user_id", name="uq_group_member"),
    )

    def __repr__(self) -> str:
        return f"<GroupMember group={self.group_id} user={self.user_id}>"
