"""Add stellr_code to users table

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-24

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("stellr_code", sa.String(10), nullable=True))
    op.create_index("idx_users_stellr_code", "users", ["stellr_code"], unique=True)


def downgrade() -> None:
    op.drop_index("idx_users_stellr_code", table_name="users")
    op.drop_column("users", "stellr_code")
