"""Group model — a collection of users (called a Constellation in the UI).

Design decisions (MVP):
- Group creator is stored explicitly and has special privileges (rename, delete).
- Members are stored in a separate join table (group_members).
- The creator is automatically added as a member on creation.
- For MVP, any existing user can be added to a group (friend check not required).
  This keeps initial friction low. If spam becomes an issue, add a friend-gate later.
- Group deletion is creator-only. Non-creator members can leave on their own.
"""

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Group(Base):
    __tablename__ = "groups"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    creator: Mapped["User"] = relationship(  # noqa: F821
        foreign_keys=[created_by],
        lazy="joined",
    )
    members: Mapped[list["GroupMember"]] = relationship(  # noqa: F821
        back_populates="group",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Group {self.name}>"
