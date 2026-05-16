"""
Script one-shot para remoção segura da tabela legada `tramitacao`.

Uso:
    cd backend && uv run python src/drop_legacy_tables.py

Pré-condição: a tabela contém apenas dados de seed, sem dados reais
de produção (conforme MIGRATION_SCOPE.md).

Idempotente: pode ser executado múltiplas vezes sem erro.
"""

from sqlmodel import text
from infrastructure.database import engine


def drop_legacy() -> None:
    """Remove a tabela tramitacao se ela existir."""
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS tramitacao CASCADE"))
        conn.commit()
        print("✅ Tabela 'tramitacao' removida (ou já não existia).")


if __name__ == "__main__":
    drop_legacy()
