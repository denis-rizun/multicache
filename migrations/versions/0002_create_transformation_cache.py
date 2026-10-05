"""create transformation cache

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-05

"""

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "transformation_cache",
        sa.Column("input_hash", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("input", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("output", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("input_hash"),
    )


def downgrade() -> None:
    op.drop_table("transformation_cache")
