"""create payload

Revision ID: 0001
Revises:
Create Date: 2026-10-05

"""

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "payload",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("input_hash", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("output", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_payload_input_hash"), "payload", ["input_hash"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_payload_input_hash"), table_name="payload")
    op.drop_table("payload")
