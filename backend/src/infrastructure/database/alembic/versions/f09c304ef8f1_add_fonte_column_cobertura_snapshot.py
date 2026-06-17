"""add_fonte_column_cobertura_snapshot

Revision ID: f09c304ef8f1
Revises: 86d18f3dcdb0
Create Date: 2026-06-16 17:52:00.140438

"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f09c304ef8f1"
down_revision: str | Sequence[str] | None = "86d18f3dcdb0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "cobertura_snapshot",
        sa.Column(
            "fonte",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
            server_default="",
        ),
    )
    op.create_index(
        op.f("ix_cobertura_snapshot_fonte"),
        "cobertura_snapshot",
        ["fonte"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_cobertura_snapshot_fonte"), table_name="cobertura_snapshot")
    op.drop_column("cobertura_snapshot", "fonte")
