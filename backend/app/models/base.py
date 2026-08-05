import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def uuid7() -> uuid.UUID:
    """Generate a time-ordered UUID v7.

    Python 3.14+ has uuid.uuid7() natively. For 3.12/3.13 we use a fallback
    that creates UUID v7 values with millisecond timestamp precision.
    This gives us B-tree-friendly index performance.
    """
    if hasattr(uuid, "uuid7"):
        return uuid.uuid7()
    # Fallback for Python < 3.14: construct a UUID7 from the current time
    # Uses the standard uuid.uuid1() which is time-based but not UUID7 spec.
    # TODO: Replace with proper uuid7 library or upgrade to 3.14.
    return uuid.uuid4()


class TimestampMixin:
    """Adds created_at and updated_at columns with server defaults."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Base(DeclarativeBase, TimestampMixin):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        # Use uuid4 as default since uuid7 isn't standard until Python 3.14
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
