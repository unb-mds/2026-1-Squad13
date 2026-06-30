from datetime import UTC, datetime

from sqlmodel import Session, delete, select

from domain.fsm import EventData, House, build_transit_steps
from infrastructure.database.models.evento_tramitacao_model import (
    EventoTramitacaoModel,
)
from infrastructure.database.models.proposicao_model import ProposicaoModel
from infrastructure.database.models.transit_step_model import TransitStepModel


class AtualizarTransitStepsService:
    """
    Serviço de aplicação idempotente encarregado de recomputar a projeção
    de TransitSteps de uma proposição e persisti-la de forma atômica no banco.
    """

    def __init__(self, session: Session):
        self.session = session

    def executar(self, proposicao_id: str) -> None:
        # 1. Busca a proposição
        proposicao = self.session.exec(
            select(ProposicaoModel).where(ProposicaoModel.id == proposicao_id)
        ).first()

        if not proposicao:
            raise ValueError(f"Proposição com ID {proposicao_id} não encontrada.")

        # 2. Busca as movimentações ordenadas cronologicamente
        eventos_model = self.session.exec(
            select(EventoTramitacaoModel)
            .where(EventoTramitacaoModel.proposicao_id == proposicao_id)
            .order_by(
                EventoTramitacaoModel.data_evento, EventoTramitacaoModel.sequencia
            )
        ).all()

        # Determina a casaOrigem com base no ID da proposição
        casa_origem = (
            House.SENADO if proposicao_id.startswith("senado:") else House.CAMARA
        )

        # 3. Converte os eventos do banco em EventData do domínio
        events_domain = []
        for e in eventos_model:
            clean_date = e.data_evento.replace("Z", "")
            try:
                dt = datetime.fromisoformat(clean_date)
            except ValueError:
                parts = clean_date.split("T")[0].split("-")
                if len(parts) == 3:
                    dt = datetime(int(parts[0]), int(parts[1]), int(parts[2]))
                else:
                    dt = datetime.now(UTC)

            events_domain.append(
                EventData(
                    timestamp=dt,
                    sigla_orgao=e.sigla_orgao or "",
                    orgao_nome="",
                    descricao=e.descricao_original,
                    remessa_ou_retorno=e.remessa_ou_retorno,
                )
            )

        # 4. Roda a FSM do domínio
        steps_domain = build_transit_steps(events_domain, casa_origem)

        # 5. Salva de forma atômica no banco de dados (Read Model Projeção)
        # Deleta os passos anteriores
        self.session.execute(
            delete(TransitStepModel).where(
                TransitStepModel.proposicao_id == proposicao_id
            )
        )

        # Salva os novos passos recomputados
        novos_models = [
            TransitStepModel(
                proposicao_id=proposicao_id,
                casa=s.casa.value,
                tipo_passo=s.tipo_passo.value,
                data_entrada=s.data_entrada,
                data_saida=s.data_saida,
                duracao_dias=s.duracao_dias,
            )
            for s in steps_domain
        ]

        self.session.add_all(novos_models)
        self.session.flush()
