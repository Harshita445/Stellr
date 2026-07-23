"""Timeslot model and slot boundary constants.

SLOT_BOUNDARIES defines the fixed time boundaries for each period in the
academic timetable. These are read from the source workbook's column headers
and validated at import time. The workbook defines slots by column position;
each column represents a specific day-period combination. CLUB hours and
other non-academic periods are treated as free time.

Slot indexing: 0-based relative to each day.
Day indexing: ISO weekday (0=Monday, 6=Sunday).
"""

from sqlalchemy import CheckConstraint, Index, SmallInteger, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


# ── Constants ─────────────────────────────────────────────────────────────

DAYS_OF_WEEK: dict[str, int] = {
    "Monday":    0,
    "Tuesday":   1,
    "Wednesday": 2,
    "Thursday":  3,
    "Friday":    4,
    "Saturday":  5,
    "Sunday":    6,
}

DAYS_REVERSE: dict[int, str] = {v: k for k, v in DAYS_OF_WEEK.items()}

# Number of academic periods (slots) per day as defined by the workbook structure.
# This represents the maximum period index across any day in the timetable.
SLOTS_PER_DAY: int = 9

# Fixed time boundaries for each slot index (0-based).
# These are the standard academic periods used by the institution.
# Slot 0 = 09:00–09:50, Slot 1 = 09:50–10:40, etc.
# Values are (start_hour, start_minute, end_hour, end_minute).
SLOT_BOUNDARIES: dict[int, tuple[int, int, int, int]] = {
    0: (9, 0, 9, 50),
    1: (9, 50, 10, 40),
    2: (11, 0, 11, 50),
    3: (11, 50, 12, 40),
    4: (13, 30, 14, 20),
    5: (14, 20, 15, 10),
    6: (15, 20, 16, 10),
    7: (16, 10, 17, 0),
    8: (17, 0, 17, 50),
}

# ── Model ─────────────────────────────────────────────────────────────────

class Timeslot(Base):
    """A fixed time slot on a specific day of the week.

    This is a reference table populated during timetable import.
    Each row represents one academic period on one day.
    """

    __tablename__ = "timeslots"

    day_of_week: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, comment="ISO weekday: 0=Monday"
    )
    slot_index: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, comment="0-based slot number within the day"
    )
    start_time: Mapped[str] = mapped_column(
        String(5), nullable=False, comment="HH:MM format"
    )
    end_time: Mapped[str] = mapped_column(
        String(5), nullable=False, comment="HH:MM format"
    )
    slot_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="lecture",
        comment="lecture, lab, tutorial, or other"
    )
    venue: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="Room/building"
    )

    timetable_entries: Mapped[list["TimetableEntry"]] = relationship(  # noqa: F821
        back_populates="timeslot", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint(
            "day_of_week", "slot_index", name="uq_timeslot_day_slot",
        ),
        CheckConstraint(
            "day_of_week >= 0 AND day_of_week <= 6",
            name="ck_timeslot_day_range",
        ),
        CheckConstraint(
            "slot_index >= 0 AND slot_index <= 20",
            name="ck_timeslot_slot_range",
        ),
        Index("idx_timeslots_day_slot", "day_of_week", "slot_index"),
    )

    def __repr__(self) -> str:
        return f"<Timeslot day={self.day_of_week} slot={self.slot_index} {self.start_time}-{self.end_time}>"
