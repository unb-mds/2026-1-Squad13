from sqlmodel import Session, select

from domain.entities.cobertura_snapshot import CoberturaSnapshot
from infrastructure.database.models.cobertura_snapshot_model import (
    CoberturaSnapshotModel,
)


class SQLCoberturaSnapshotRepository:
    """Repositório SQL para snapshots de cobertura."""

    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: CoberturaSnapshotModel) -> CoberturaSnapshot:
        return CoberturaSnapshot.model_validate(model.model_dump())

    def _to_model(self, entity: CoberturaSnapshot) -> CoberturaSnapshotModel:
        return CoberturaSnapshotModel.model_validate(entity.model_dump())

    def salvar(self, snapshot: CoberturaSnapshot) -> CoberturaSnapshot:
        """Salva ou atualiza um snapshot no banco."""
        model = self._to_model(snapshot)
        if model.id:
            existing = self.session.get(CoberturaSnapshotModel, model.id)
            if existing:
                for key, value in model.model_dump(exclude={"id"}).items():
                    setattr(existing, key, value)
                model = existing
        else:
            statement = select(CoberturaSnapshotModel).where(
                CoberturaSnapshotModel.ano == model.ano,
                CoberturaSnapshotModel.tipo_proposicao == model.tipo_proposicao,
            )
            existing = self.session.exec(statement).first()
            if existing:
                for key, value in model.model_dump(exclude={"id"}).items():
                    setattr(existing, key, value)
                model = existing

        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def buscar_por_ano_e_tipo(
        self, ano: int, tipo_proposicao: str
    ) -> CoberturaSnapshot | None:
        """Busca o snapshot de cobertura correspondente ao ano e tipo."""
        statement = select(CoberturaSnapshotModel).where(
            CoberturaSnapshotModel.ano == ano,
            CoberturaSnapshotModel.tipo_proposicao == tipo_proposicao,
        )
        model = self.session.exec(statement).first()
        return self._to_entity(model) if model else None

    def buscar_todos(self) -> list[CoberturaSnapshot]:
        """Retorna todos os snapshots ordenados por data de atualização descrescente."""
        statement = select(CoberturaSnapshotModel).order_by(
            CoberturaSnapshotModel.data_atualizacao.desc()
        )
        models = self.session.exec(statement).all()
        return [self._to_entity(m) for m in models]
