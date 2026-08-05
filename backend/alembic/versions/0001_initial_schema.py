"""initial_schema

Revision ID: 0001
Revises:
Create Date: 2026-07-23

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── sections ─────────────────────────────────────────────────────────
    op.create_table(
        "sections",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("department", sa.String(length=100), nullable=False),
        sa.Column("semester", sa.Integer(), nullable=False),
        sa.Column("academic_year", sa.String(length=20), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "name", "department", "semester", "academic_year",
            name="uq_section",
        ),
    )
    op.create_index("idx_sections_name", "sections", ["name"])

    # ── courses ──────────────────────────────────────────────────────────
    op.create_table(
        "courses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("department", sa.String(length=100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", "department", name="uq_course"),
    )
    op.create_index("idx_courses_code", "courses", ["code"])

    # ── timeslots ────────────────────────────────────────────────────────
    op.create_table(
        "timeslots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("day_of_week", sa.SmallInteger(), nullable=False),
        sa.Column("slot_index", sa.SmallInteger(), nullable=False),
        sa.Column("start_time", sa.String(length=5), nullable=False),
        sa.Column("end_time", sa.String(length=5), nullable=False),
        sa.Column("slot_type", sa.String(length=20), nullable=False, server_default="lecture"),
        sa.Column("venue", sa.String(length=100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "day_of_week", "slot_index",
            name="uq_timeslot_day_slot",
        ),
        sa.CheckConstraint(
            "day_of_week >= 0 AND day_of_week <= 6",
            name="ck_timeslot_day_range",
        ),
        sa.CheckConstraint(
            "slot_index >= 0 AND slot_index <= 20",
            name="ck_timeslot_slot_range",
        ),
    )
    op.create_index("idx_timeslots_day_slot", "timeslots", ["day_of_week", "slot_index"])

    # ── timetable_entries ────────────────────────────────────────────────
    op.create_table(
        "timetable_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("section_id", sa.Uuid(), nullable=False),
        sa.Column("course_id", sa.Uuid(), nullable=False),
        sa.Column("timeslot_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["section_id"], ["sections.id"],
            name="fk_tt_section", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["course_id"], ["courses.id"],
            name="fk_tt_course", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["timeslot_id"], ["timeslots.id"],
            name="fk_tt_timeslot", ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "section_id", "timeslot_id",
            name="uq_tt_entry",
        ),
    )
    op.create_index("idx_tt_section", "timetable_entries", ["section_id"])
    op.create_index("idx_tt_section_course", "timetable_entries", ["section_id", "course_id"])


def downgrade() -> None:
    op.drop_table("timetable_entries")
    op.drop_table("timeslots")
    op.drop_table("courses")
    op.drop_table("sections")
