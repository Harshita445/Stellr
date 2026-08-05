import uuid

from sqlalchemy import ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class TimetableEntry(Base):
    """Links a section, course, and timeslot together.

    A single row means: "This section studies this course during this timeslot."
    This is the core join table that powers all availability queries.

    The workbook is NEVER queried during normal requests. All data lives here.
    """

    __tablename__ = "timetable_entries"

    section_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )
    timeslot_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("timeslots.id", ondelete="CASCADE"),
        nullable=False,
    )

    section: Mapped["Section"] = relationship(back_populates="timetable_entries")  # noqa: F821
    course: Mapped["Course"] = relationship(back_populates="timetable_entries")    # noqa: F821
    timeslot: Mapped["Timeslot"] = relationship(back_populates="timetable_entries")  # noqa: F821

    __table_args__ = (
        UniqueConstraint(
            "section_id", "timeslot_id",
            name="uq_tt_entry",
        ),
        Index("idx_tt_section_course", "section_id", "course_id"),
    )

    def __repr__(self) -> str:
        return f"<TimetableEntry section={self.section_id} timeslot={self.timeslot_id}>"
