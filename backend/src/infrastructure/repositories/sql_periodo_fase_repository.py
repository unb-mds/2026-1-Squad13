from sqlmodel import Session, delete, select

from domain.entities.periodo_fase import PeriodoFase
from infrastructure.database.models.periodo_fase_model import PeriodoFaseModel


class SQLPeriodoFaseRepository:
    """Repositório SQL para períodos de fase."""

    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: PeriodoFaseModel) -> PeriodoFase:
        return PeriodoFase.model_validate(model)

    def _to_model(self, entity: PeriodoFase) -> PeriodoFaseModel:
        return PeriodoFaseModel.model_validate(entity)

    def salvar_lote(self, periodos: list[PeriodoFase]) -> list[PeriodoFase]:
        """Persiste uma lista de períodos em lote."""
        if periodos:
            models = [self._to_model(p) for p in periodos]
            self.session.add_all(models)
            self.session.commit()
            # Retorna a lista original para evitar re-mapeamento de objetos expirados pós-commit
            # O ReconstruirPeriodosService não utiliza o retorno para obter IDs.
            return periodos
        return []

    def buscar_por_proposicao(self, proposicao_id: str) -> list[PeriodoFase]:
        """Retorna todos os períodos de uma proposição ordenados cronologicamente."""
        statement = (
            select(PeriodoFaseModel)
            .where(PeriodoFaseModel.proposicao_id == proposicao_id)
            .order_by(PeriodoFaseModel.data_inicio.asc(), PeriodoFaseModel.id.asc())
        )
        models = self.session.exec(statement).all()
        return [self._to_entity(m) for m in models]

    def deletar_por_proposicao(self, proposicao_id: str) -> None:
        """Deleta todos os períodos de uma proposição."""
        statement = delete(PeriodoFaseModel).where(
            PeriodoFaseModel.proposicao_id == proposicao_id
        )
        self.session.exec(statement)
        self.session.commit()
