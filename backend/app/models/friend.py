"""Friend model.

Design decision: single bidirectional row per friendship.
- A friendship between A and B is stored as one row (user_id=A, friend_id=B).
- The unique constraint uses LEAST(user_id, friend_id), GREATEST(user_id, friend_id)
  to enforce only one row regardless of who initiated.
- Querying a user's friends requires checking both columns via UNION.

Why single row instead of two directional rows:
- Half the storage for N friendships
- No risk of inconsistent state (row exists in one direction but not the other)
- Simpler deletion (one row to remove)
- LEAST/GREATEST index ensures O(log N) lookup in both directions

This is an MVP assumption. If a request/accept flow is needed later,
add a `status` column (pending/accepted/blocked) and keep the same table structure.
"""

import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Friend(Base):
    __tablename__ = "friends"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    friend_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    user: Mapped["User"] = relationship(  # noqa: F821
        foreign_keys=[user_id],
        back_populates="friends_initiated",
    )
    friend: Mapped["User"] = relationship(  # noqa: F821
        foreign_keys=[friend_id],
        back_populates="friends_received",
    )

    __table_args__ = (
        CheckConstraint("user_id <> friend_id", name="ck_friend_not_self"),
        Index("idx_friends_user", "user_id"),
        Index("idx_friends_friend", "friend_id"),
        Index(
            "uq_friendship",
            func.least(user_id, friend_id),
            func.greatest(user_id, friend_id),
            unique=True,
        ),
    )

    def __repr__(self) -> str:
        return f"<Friend {self.user_id} ↔ {self.friend_id}>"
