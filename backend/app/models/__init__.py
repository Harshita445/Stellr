"""SQLAlchemy ORM models.

Import order matters: base first, then models with FK references.
"""

from app.models.base import Base
from app.models.section import Section
from app.models.course import Course
from app.models.timeslot import Timeslot, DAYS_OF_WEEK, SLOT_BOUNDARIES, SLOTS_PER_DAY
from app.models.timetable_entry import TimetableEntry
from app.models.user import User
from app.models.device import Device

__all__ = [
    "Base",
    "Section",
    "Course",
    "Timeslot",
    "TimetableEntry",
    "User",
    "Device",
    "DAYS_OF_WEEK",
    "SLOT_BOUNDARIES",
    "SLOTS_PER_DAY",
]
