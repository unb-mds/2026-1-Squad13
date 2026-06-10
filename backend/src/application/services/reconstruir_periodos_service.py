import logging
from datetime import date, datetime

from application.ports.evento_tramitacao_repository import (
    EventoTramitacaoRepositoryPort,
)
from application.ports.fase_analitica_repository import FaseAnaliticaRepositoryPort
from application.ports.periodo_fase_repository import PeriodoFaseRepositoryPort
from application.ports.proposicao_repository import ProposicaoRepositoryPort
from domain.entities.evento_tramitacao import EventoTramitacao
from domain.entities.periodo_fase import PeriodoFase
from domain.services.heuristica_travamento_service import HeuristicaTravamentoService

logger = logging.getLogger(__name__)


class ReconstruirPeriodosService:
    """
    Serviço que reconstrói os períodos de fase (periodo_fase) para proposições.
    Garante a integridade do histórico por meio da classificação e consolidação de eventos.
    """

    def __init__(
        self,
        periodo_repo: PeriodoFaseRepositoryPort,
        evento_repo: EventoTramitacaoRepositoryPort,
        fase_repo: FaseAnaliticaRepositoryPort,
        proposicao_repo: ProposicaoRepositoryPort,
    ):
        self.periodo_repo = periodo_repo
        self.evento_repo = evento_repo
        self.fase_repo = fase_repo
        self.proposicao_repo = proposicao_repo

    def reconstruir_para_proposicao(self, proposicao_id: str) -> list[PeriodoFase]:
        """
        Consolida a linha do tempo de eventos de uma proposição em períodos de fase.
        Retorna a lista de períodos reconstruídos.
        """
        proposicao = self.proposicao_repo.buscar_por_id(proposicao_id)
        if not proposicao:
            logger.error(
                f"Proposição {proposicao_id} não encontrada para reconstrução de períodos."
            )
            return []

        todas_fases = self.fase_repo.buscar_todas()
        if not todas_fases:
            logger.warning(
                f"Nenhuma fase analítica encontrada no banco para reconstruir proposição {proposicao_id}. "
                "Certifique-se de que o seed de fases foi executado."
            )
            return []

        fase_codigo_to_id = {f.codigo: f.id for f in todas_fases}
        fase_id_to_codigo = {f.id: f.codigo for f in todas_fases}
        default_fase_id = fase_codigo_to_id.get("PROTOCOLO_INICIAL")

        # Se mesmo com fases, não houver o PROTOCOLO_INICIAL, usamos o ID da primeira fase disponível como fallback extremo
        if default_fase_id is None and todas_fases:
            default_fase_id = todas_fases[0].id

        eventos = self.evento_repo.buscar_por_proposicao(proposicao_id)

        periodos = []

        if not eventos:
            # Fallback robusto se não houver eventos
            fase_codigo = self._status_to_fase_codigo(proposicao.status)
            fase_id = fase_codigo_to_id.get(fase_codigo, default_fase_id)
            data_inicio = (
                datetime.fromisoformat(proposicao.data_apresentacao[:10]).date()
                if proposicao.data_apresentacao
                else date.today()
            )

            periodo = PeriodoFase(
                proposicao_id=proposicao_id,
                fase_analitica_id=fase_id,
                data_inicio=data_inicio,
                data_fim=None,
                duracao_dias=None,
                recorrencia_numero=1,
                eh_fase_atual=True,
                motivo_travamento=None,
                tipo_proposicao=proposicao.tipo or "PL",
                rito=proposicao.regime_tramitacao or "ORDINARIO",
                numero_turno=None,
                subtipo_fase=None,
                origem_calculo="reconstrucao_historica",
            )
            periodos.append(periodo)
        else:
            # Agrupa eventos contíguos que têm a mesma fase
            grouped_periods = []
            current_fase_id = None

            for e in eventos:
                fid = e.fase_analitica_id
                if fid is None:
                    fid = (
                        current_fase_id
                        if current_fase_id is not None
                        else default_fase_id
                    )

                if current_fase_id is None or fid != current_fase_id:
                    grouped_periods.append({"fase_analitica_id": fid, "events": [e]})
                    current_fase_id = fid
                else:
                    grouped_periods[-1]["events"].append(e)

            # Reconstrói períodos e calcula métricas
            recurrence_counts = {}
            for i, gp in enumerate(grouped_periods):
                fid = gp["fase_analitica_id"]
                gp_events = gp["events"]

                data_inicio = datetime.fromisoformat(
                    gp_events[0].data_evento[:10]
                ).date()

                data_fim = None
                if i + 1 < len(grouped_periods):
                    next_gp_events = grouped_periods[i + 1]["events"]
                    data_fim = datetime.fromisoformat(
                        next_gp_events[0].data_evento[:10]
                    ).date()

                if data_fim and data_fim < data_inicio:
                    data_fim = data_inicio

                recurrence_counts[fid] = recurrence_counts.get(fid, 0) + 1
                recorrencia_num = recurrence_counts[fid]

                eh_fase_atual = i == len(grouped_periods) - 1

                duracao_dias = None
                if data_fim:
                    duracao_dias = (data_fim - data_inicio).days

                # Motivo de travamento
                dur_check = (
                    duracao_dias
                    if duracao_dias is not None
                    else (date.today() - data_inicio).days
                )
                motivo_travamento = None
                if dur_check > 30:
                    last_event = gp_events[-1]
                    motivo_travamento = (
                        HeuristicaTravamentoService.classificar_motivo_travamento(
                            last_event.descricao_original
                        ).value
                    )

                fase_codigo = fase_id_to_codigo.get(fid, "PROTOCOLO_INICIAL")
                subtipo_fase, numero_turno = self._classificar_subtipo_e_turno(
                    fase_codigo, gp_events
                )

                periodo = PeriodoFase(
                    proposicao_id=proposicao_id,
                    fase_analitica_id=fid,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    duracao_dias=duracao_dias,
                    recorrencia_numero=recorrencia_num,
                    eh_fase_atual=eh_fase_atual,
                    motivo_travamento=motivo_travamento,
                    tipo_proposicao=proposicao.tipo or "PL",
                    rito=proposicao.regime_tramitacao or "ORDINARIO",
                    numero_turno=numero_turno,
                    subtipo_fase=subtipo_fase,
                    origem_calculo="reconstrucao_historica",
                )
                periodos.append(periodo)

        # Atualiza o estado da Proposicao baseado no último período
        if periodos:
            ultimo_periodo = periodos[-1]
            ultima_fase_codigo = fase_id_to_codigo.get(
                ultimo_periodo.fase_analitica_id, "PROTOCOLO_INICIAL"
            )

            if ultima_fase_codigo == "ENCERRADA":
                last_event_desc = (
                    eventos[-1].descricao_original.lower() if eventos else ""
                )
                if (
                    "sancionad" in last_event_desc
                    or "norma jurídica" in last_event_desc
                ):
                    proposicao.status = "Sancionada"
                elif "vetad" in last_event_desc:
                    proposicao.status = "Vetada"
                elif any(
                    x in last_event_desc
                    for x in ["rejeitad", "arquivad", "prejudicad", "retirad"]
                ):
                    proposicao.status = "Arquivada"
                else:
                    if proposicao.status not in ("Sancionada", "Vetada", "Arquivada"):
                        proposicao.status = "Arquivada"

                proposicao.data_encerramento = ultimo_periodo.data_inicio.isoformat()
            elif ultima_fase_codigo == "TRAMITE_ENTRE_CASAS":
                proposicao.status = "Aprovada"
                proposicao.data_encerramento = None
            elif ultima_fase_codigo == "AGUARDANDO_PAUTA":
                proposicao.status = "Em Pauta"
                proposicao.data_encerramento = None
            else:
                proposicao.status = "Em Tramitação"
                proposicao.data_encerramento = None

            if eventos:
                proposicao.data_ultima_movimentacao = eventos[-1].data_evento

            proposicao.atualizar_metricas()
            self.proposicao_repo.salvar(proposicao)

        # Deleta períodos antigos e insere os novos
        self.periodo_repo.deletar_por_proposicao(proposicao_id)
        self.periodo_repo.salvar_lote(periodos)

        return periodos

    def _status_to_fase_codigo(self, status: str | None) -> str:
        if not status:
            return "PROTOCOLO_INICIAL"
        s = status.lower()
        if "sancionada" in s or "vetada" in s or "arquivada" in s:
            return "ENCERRADA"
        if "aprovada" in s:
            return "TRAMITE_ENTRE_CASAS"
        if "pauta" in s:
            return "AGUARDANDO_PAUTA"
        return "ANALISE_COMISSOES"

    def _classificar_subtipo_e_turno(
        self, fase_codigo: str, events: list[EventoTramitacao]
    ) -> tuple[str | None, int | None]:
        if not events:
            return None, None

        subtipo = None
        numero_turno = None

        all_text = " ".join([e.descricao_original.lower() for e in events])
        all_organs = {e.sigla_orgao.lower() for e in events if e.sigla_orgao}

        if fase_codigo in ("ANALISE_COMISSOES", "REVISAO_OUTRA_CASA"):
            if (
                "ccj" in all_organs
                or "ccjr" in all_organs
                or "constituição e justiça" in all_text
                or "constituicao e justica" in all_text
            ):
                subtipo = "ccj"
            elif "comissão especial" in all_text or "comissao especial" in all_text:
                subtipo = "comissao_especial"
            elif (
                "despacho" in all_text
                or "distribuição" in all_text
                or "distribuicao" in all_text
                or "distribuído" in all_text
            ):
                subtipo = "despacho"
            else:
                subtipo = "comissao_tematica"

        elif fase_codigo == "DELIBERACAO_PLENARIO":
            if (
                "1º turno" in all_text
                or "1o turno" in all_text
                or "primeiro turno" in all_text
            ):
                subtipo = "turno_1"
                numero_turno = 1
            elif (
                "2º turno" in all_text
                or "2o turno" in all_text
                or "segundo turno" in all_text
            ):
                subtipo = "turno_2"
                numero_turno = 2
            elif "redação final" in all_text or "redacao final" in all_text:
                subtipo = "redacao_final"

        elif fase_codigo == "ETAPA_EXECUTIVO":
            if "veto total" in all_text:
                subtipo = "veto_total"
            elif "veto parcial" in all_text:
                subtipo = "veto_parcial"
            else:
                subtipo = "sancao_pendente"

        return subtipo, numero_turno
