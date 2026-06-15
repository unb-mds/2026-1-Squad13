"""reset_numero_emendas_to_null

Revision ID: b3f102f30e6g
Revises: a1e102f30d5f
Create Date: 2026-06-10 16:30:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b3f102f30e6g"
down_revision: str | Sequence[str] | None = "a1e102f30d5f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """
    Data Migration: Reseta numero_emendas para NULL para forçar o re-calculo
    pelo script de backfill, corrigindo dados afetados pelo bug da Câmara.
    """
    # Reseta para a Câmara (onde o 0 era mentiroso devido ao erro 405)
    op.execute(
        "UPDATE proposicao SET numero_emendas = NULL WHERE orgao_origem = 'Câmara dos Deputados';"
    )


def downgrade() -> None:
    """Downgrade: Volta para 0 (comportamento antigo)."""
    op.execute("UPDATE proposicao SET numero_emendas = 0 WHERE numero_emendas IS NULL;")
