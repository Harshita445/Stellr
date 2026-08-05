"""Add friends table

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-23

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "friends",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("friend_id", sa.Uuid(), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["friend_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.CheckConstraint(
            "user_id <> friend_id", name="ck_friend_not_self"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_friends_user", "friends", ["user_id"])
    op.create_index("idx_friends_friend", "friends", ["friend_id"])
    op.create_index(
        "uq_friendship",
        "friends",
        [sa.text("LEAST(user_id, friend_id)"),
         sa.text("GREATEST(user_id, friend_id)")],
        unique=True,
    )


def downgrade() -> None:
    op.drop_table("friends")
