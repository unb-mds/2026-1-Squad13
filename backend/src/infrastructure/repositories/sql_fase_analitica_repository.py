"""
Repositório para a tabela de lookup fase_analitica.

As 8 fases são inseridas via seed e nunca criadas em runtime.
Este repositório oferece consulta e seed idempotente.
"""

from typing import List, Optional

from sqlmodel import Session, select

from domain.entities.fase_analitica import FASES_SEED, FaseAnalitica


class SQLFaseAnaliticaRepository:
    """Repositório SQL para fases analíticas."""

    def __init__(self, session: Session):
        self.session = session

    def buscar_por_codigo(self, codigo: str) -> Optional[FaseAnalitica]:
        """Busca uma fase pelo seu código único."""
        statement = select(FaseAnalitica).where(
            FaseAnalitica.codigo == codigo
        )
        return self.session.exec(statement).first()

    def buscar_todas(self) -> List[FaseAnalitica]:
        """Lista todas as fases ordenadas por ordem_logica."""
        statement = select(FaseAnalitica).order_by(
            FaseAnalitica.ordem_logica.asc()
        )
        return list(self.session.exec(statement).all())

    def seed_fases(self) -> None:
        """
        Upsert idempotente das 8 fases a partir de FASES_SEED.

        Se a fase já existe (por codigo), pula. Se não existe, insere.
        Isso permite rodar o seed múltiplas vezes sem duplicar dados.
        """
        for fase_data in FASES_SEED:
            existente = self.buscar_por_codigo(fase_data["codigo"])
            if existente is None:
                fase = FaseAnalitica(**fase_data)
                self.session.add(fase)
        self.session.commit()
