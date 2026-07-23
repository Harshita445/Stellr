import uuid

from sqlalchemy import Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Section(Base):
    __tablename__ = "sections"

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    semester: Mapped[int] = mapped_column(nullable=False)
    academic_year: Mapped[str] = mapped_column(String(20), nullable=False)

    timetable_entries: Mapped[list["TimetableEntry"]] = relationship(  # noqa: F821
        back_populates="section", cascade="all, delete-orphan"
    )
    users: Mapped[list["User"]] = relationship(back_populates="section")  # noqa: F821

    __table_args__ = (
        UniqueConstraint(
            "name", "department", "semester", "academic_year",
            name="uq_section",
        ),
        Index("idx_sections_name", "name"),
    )

    def __repr__(self) -> str:
        return f"<Section {self.department} {self.name} ({self.academic_year})>"
