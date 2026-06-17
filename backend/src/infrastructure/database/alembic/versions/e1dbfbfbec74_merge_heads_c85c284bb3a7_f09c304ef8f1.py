"""merge heads c85c284bb3a7 f09c304ef8f1

Revision ID: e1dbfbfbec74
Revises: c85c284bb3a7, f09c304ef8f1
Create Date: 2026-06-17 12:25:43.603271

"""
from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = 'e1dbfbfbec74'
down_revision: str | Sequence[str] | None = ('c85c284bb3a7', 'f09c304ef8f1')
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
