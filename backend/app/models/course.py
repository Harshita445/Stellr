from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Course(Base):
    __tablename__ = "courses"

    code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)

    timetable_entries: Mapped[list["TimetableEntry"]] = relationship(  # noqa: F821
        back_populates="course", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("code", "department", name="uq_course"),
    )

    def __repr__(self) -> str:
        return f"<Course {self.code}: {self.name}>"
