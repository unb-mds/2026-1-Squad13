from typing import List, Optional

from sqlmodel import Session, select

from domain.entities.apensamento import Apensamento
from infrastructure.database.models.apensamento_model import ApensamentoModel


class SQLApensamentoRepository:
    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: ApensamentoModel) -> Apensamento:
        return Apensamento.model_validate(model.model_dump())

    def _to_model(self, entity: Apensamento) -> ApensamentoModel:
        return ApensamentoModel.model_validate(entity.model_dump())

    def salvar(self, apensamento: Apensamento) -> Apensamento:
        model = self._to_model(apensamento)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def buscar_por_materia_apensada(self, materia_id: str) -> Optional[Apensamento]:
        statement = select(ApensamentoModel).where(
            ApensamentoModel.materia_apensada_id == materia_id
        )
        model = self.session.exec(statement).first()
        return self._to_entity(model) if model else None

    def buscar_por_materia_principal(self, materia_id: str) -> List[Apensamento]:
        statement = select(ApensamentoModel).where(
            ApensamentoModel.materia_principal_id == materia_id
        )
        models = self.session.exec(statement).all()
        return [self._to_entity(m) for m in models]
