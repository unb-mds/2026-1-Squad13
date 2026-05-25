import logging
from datetime import datetime

from application.ports.baseline_tramitacao_repository import (
    BaselineTramitacaoRepositoryPort,
)
from domain.constants import LIMITE_DIAS_ATRASO
from domain.services.calcular_metricas_service import CalcularMetricasService
from infrastructure.repositories.sql_evento_tramitacao_repository import (
    SQLEventoTramitacaoRepository,
)
from infrastructure.repositories.sql_fase_analitica_repository import (
    SQLFaseAnaliticaRepository,
)
from infrastructure.repositories.sql_proposicao_repository import (
    SQLProposicaoRepository,
)

logger = logging.getLogger(__name__)


class ProcessarMetricasService:
    """
    Serviço de aplicação para orquestrar o cálculo e atualização de métricas legislativas.
    """

    def __init__(
        self,
        proposicao_repo: SQLProposicaoRepository,
        evento_repo: SQLEventoTramitacaoRepository,
        fase_repo: SQLFaseAnaliticaRepository,
        baseline_repo: BaselineTramitacaoRepositoryPort,
    ):
        self.proposicao_repo = proposicao_repo
        self.evento_repo = evento_repo
        self.fase_repo = fase_repo
        self.baseline_repo = baseline_repo

    def executar(self, proposicao_ids: list[str] | None = None) -> dict:
        """
        Orquestra a atualização das métricas para uma lista de IDs ou todas as proposições do banco.
        Retorna um resumo estatístico da execução.
        """
        if proposicao_ids is not None:
            proposicoes = []
            for pid in proposicao_ids:
                p = self.proposicao_repo.buscar_por_id(pid)
                if p:
                    proposicoes.append(p)
        else:
            proposicoes = self.proposicao_repo.filtrar()

        if not proposicoes:
            logger.info("Nenhuma proposição encontrada para cálculo de métricas.")
            return {"processados": 0, "sucessos": 0, "falhas": 0}

        # Carrega todas as fases para cache local de lookup O(1)
        todas_fases = self.fase_repo.buscar_todas()
        fase_map = {f.id: f.codigo for f in todas_fases}

        sucessos = 0
        falhas = 0

        # Carrega eventos para as proposições em lote
        pids = [str(p.id) for p in proposicoes]
        mapa_eventos = self.evento_repo.buscar_por_multiplas_proposicoes(pids)

        for prop in proposicoes:
            try:
                eventos = mapa_eventos.get(str(prop.id), [])

                # 1. Determina decorrido e encerramento
                tempo_decorrido, data_encerramento = (
                    CalcularMetricasService.obter_decorrido_e_encerramento(
                        prop.data_apresentacao, eventos
                    )
                )

                # 2. Busca baseline do escopo TOTAL
                baseline_total = self.baseline_repo.buscar_baseline(
                    escopo="TOTAL",
                    tipo=prop.tipo,
                    regime_tramitacao=prop.regime_tramitacao,
                )

                dias_esperados_total = None
                baseline_grupo_id = None
                iar = None

                if baseline_total:
                    dias_esperados_total = baseline_total.mediana_dias
                    baseline_grupo_id = str(baseline_total.baseline_id)
                    iar = CalcularMetricasService.calcular_iar(
                        tempo_decorrido, baseline_total.mediana_dias
                    )

                # 3. Classifica status de atraso
                status_atraso = CalcularMetricasService.classificar_status_atraso(iar)

                # 4. Calcula IEI (Espera Improdutiva)
                iei = CalcularMetricasService.calcular_iei(eventos, tempo_decorrido)

                # 5. Determina IAF (Fase Atual)
                fase_atual_id, data_entrada_fase = (
                    CalcularMetricasService.obter_data_entrada_fase_atual(
                        prop.data_apresentacao, eventos
                    )
                )

                fase_codigo = fase_map.get(fase_atual_id) if fase_atual_id else None
                iaf = None

                if fase_codigo:
                    baseline_fase = self.baseline_repo.buscar_baseline(
                        escopo="FASE",
                        tipo=prop.tipo,
                        regime_tramitacao=prop.regime_tramitacao,
                        fase_codigo=fase_codigo,
                    )
                    if baseline_fase:
                        iaf = CalcularMetricasService.calcular_iaf(
                            data_entrada_fase,
                            baseline_fase.mediana_dias,
                            data_encerramento,
                        )

                # 6. Atualiza entidade
                prop.indice_atraso_relativo = iar
                prop.indice_atraso_fase_atual = iaf
                prop.indice_espera_improdutiva = iei
                prop.status_atraso = status_atraso
                prop.dias_decorridos_total = tempo_decorrido
                prop.dias_esperados_total = dias_esperados_total
                prop.baseline_grupo_id = baseline_grupo_id
                prop.data_calculo_metricas = datetime.now()
                prop.data_encerramento = data_encerramento
                prop.tempo_total_dias = tempo_decorrido
                prop.tem_atraso = (tempo_decorrido > LIMITE_DIAS_ATRASO) and (
                    data_encerramento is None
                )

                # 7. Salva no banco de dados
                self.proposicao_repo.salvar(prop)
                sucessos += 1

            except Exception as e:
                logger.error(
                    f"Erro ao processar métricas para proposição {prop.id}: {e}",
                    exc_info=True,
                )
                falhas += 1

        return {
            "processados": len(proposicoes),
            "sucessos": sucessos,
            "falhas": falhas,
        }
