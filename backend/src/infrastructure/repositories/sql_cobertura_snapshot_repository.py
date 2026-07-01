from sqlmodel import Session, select

from domain.entities.cobertura_snapshot import CoberturaSnapshot
from infrastructure.database.models.cobertura_snapshot_model import (
    CoberturaSnapshotModel,
)


class SQLCoberturaSnapshotRepository:
    """Repositório SQL para snapshots de cobertura.

    A chave de upsert leva em conta `(ano, tipo_proposicao, fonte)`.
    Snapshots legados (sem `fonte`) são identificados por `fonte=""`.
    """

    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: CoberturaSnapshotModel) -> CoberturaSnapshot:
        return CoberturaSnapshot.model_validate(model.model_dump())

    def _to_model(self, entity: CoberturaSnapshot) -> CoberturaSnapshotModel:
        return CoberturaSnapshotModel.model_validate(entity.model_dump())

    def salvar(self, snapshot: CoberturaSnapshot) -> CoberturaSnapshot:
        """Salva ou atualiza um snapshot no banco (upsert por ano + tipo + fonte)."""
        model = self._to_model(snapshot)
        if model.id:
            existing = self.session.get(CoberturaSnapshotModel, model.id)
            if existing:
                for key, value in model.model_dump(exclude={"id"}).items():
                    setattr(existing, key, value)
                model = existing
        else:
            # Upsert por (ano, tipo_proposicao, fonte) — chave natural de negócio
            statement = select(CoberturaSnapshotModel).where(
                CoberturaSnapshotModel.ano == model.ano,
                CoberturaSnapshotModel.tipo_proposicao == model.tipo_proposicao,
                CoberturaSnapshotModel.fonte == model.fonte,
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

    def buscar_por_ano_tipo_e_fonte(
        self, ano: int, tipo_proposicao: str, fonte: str
    ) -> CoberturaSnapshot | None:
        """Busca o snapshot de cobertura pelo par (ano, tipo, fonte)."""
        statement = select(CoberturaSnapshotModel).where(
            CoberturaSnapshotModel.ano == ano,
            CoberturaSnapshotModel.tipo_proposicao == tipo_proposicao,
            CoberturaSnapshotModel.fonte == fonte,
        )
        model = self.session.exec(statement).first()
        return self._to_entity(model) if model else None

    def buscar_por_ano_e_tipo(
        self, ano: int, tipo_proposicao: str
    ) -> CoberturaSnapshot | None:
        """Busca o snapshot mais recente pelo ano e tipo (sem distinção de fonte).

        Mantido para retrocompatibilidade com chamadas legadas.
        Prefira `buscar_por_ano_tipo_e_fonte` em código novo.
        """
        statement = (
            select(CoberturaSnapshotModel)
            .where(
                CoberturaSnapshotModel.ano == ano,
                CoberturaSnapshotModel.tipo_proposicao == tipo_proposicao,
            )
            .order_by(CoberturaSnapshotModel.data_atualizacao.desc())
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
