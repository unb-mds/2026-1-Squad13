"""
Repositório para a tabela de lookup fase_analitica.

As 8 fases são inseridas via seed e nunca criadas em runtime.
Este repositório oferece consulta e seed idempotente.
"""

from typing import List, Optional

from sqlmodel import Session, select

from domain.entities.fase_analitica import FASES_SEED, FaseAnalitica
from infrastructure.database.models.fase_analitica_model import FaseAnaliticaModel


class SQLFaseAnaliticaRepository:
    """Repositório SQL para fases analíticas."""

    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: FaseAnaliticaModel) -> FaseAnalitica:
        return FaseAnalitica.model_validate(model.model_dump())

    def _to_model(self, entity: FaseAnalitica) -> FaseAnaliticaModel:
        return FaseAnaliticaModel.model_validate(entity.model_dump())

    def buscar_por_codigo(self, codigo: str) -> Optional[FaseAnalitica]:
        """Busca uma fase pelo seu código único."""
        statement = select(FaseAnaliticaModel).where(
            FaseAnaliticaModel.codigo == codigo
        )
        model = self.session.exec(statement).first()
        return self._to_entity(model) if model else None

    def buscar_todas(self) -> List[FaseAnalitica]:
        """Lista todas as fases ordenadas por ordem_logica."""
        statement = select(FaseAnaliticaModel).order_by(
            FaseAnaliticaModel.ordem_logica.asc()
        )
        models = self.session.exec(statement).all()
        return [self._to_entity(m) for m in models]

    def seed_fases(self) -> None:
        """
        Upsert idempotente das 8 fases a partir de FASES_SEED.
        """
        for fase_data in FASES_SEED:
            existente = self.buscar_por_codigo(fase_data["codigo"])
            if existente is None:
                model = FaseAnaliticaModel(**fase_data)
                self.session.add(model)
        self.session.commit()
