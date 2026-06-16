"""add bloco_legislativo and parecer_ccj to proposicao

Revision ID: c85c284bb3a7
Revises: 86d18f3dcdb0
Create Date: 2026-06-15 22:54:47.445616

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c85c284bb3a7'
down_revision: Union[str, Sequence[str], None] = '86d18f3dcdb0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("proposicao", sa.Column("bloco_legislativo", sa.String(), nullable=True))
    op.add_column("proposicao", sa.Column("parecer_ccj_favoravel", sa.Boolean(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("proposicao", "parecer_ccj_favoravel")
    op.drop_column("proposicao", "bloco_legislativo")
