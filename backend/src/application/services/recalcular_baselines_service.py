import logging
from datetime import datetime

from domain.entities.baseline_tramitacao import BaselineTramitacao
from domain.services.calcular_metricas_service import CalcularMetricasService
from infrastructure.repositories.sql_baseline_tramitacao_repository import (
    SQLBaselineTramitacaoRepository,
)
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


class RecalcularBaselinesService:
    """
    Serviço de aplicação para recalcular baselines dinâmicos de tramitação com base nos dados locais.
    """

    def __init__(
        self,
        proposicao_repo: SQLProposicaoRepository,
        evento_repo: SQLEventoTramitacaoRepository,
        fase_repo: SQLFaseAnaliticaRepository,
        baseline_repo: SQLBaselineTramitacaoRepository,
    ):
        self.proposicao_repo = proposicao_repo
        self.evento_repo = evento_repo
        self.fase_repo = fase_repo
        self.baseline_repo = baseline_repo

    @staticmethod
    def calcular_mediana(valores: list[int]) -> int:
        """Calcula a mediana matemática de uma lista de inteiros."""
        if not valores:
            return 0
        valores_ordenados = sorted(valores)
        n = len(valores_ordenados)
        meio = n // 2
        if n % 2 == 1:
            return valores_ordenados[meio]
        else:
            return (valores_ordenados[meio - 1] + valores_ordenados[meio] + 1) // 2

    def executar(self) -> dict:
        """
        Executa a rotina de limpeza de baselines dinâmicos e recalcula-os.
        Retorna o total de baselines dinâmicos criados.
        """
        logger.info("Iniciando recálculo diário de baselines dinâmicos...")

        # 1. Limpa os registros dinâmicos antigos
        self.baseline_repo.remover_calculos_dinamicos()

        # 2. Busca todas as proposições e eventos
        proposicoes = self.proposicao_repo.filtrar()
        if not proposicoes:
            logger.info("Nenhuma proposição no banco para calcular baselines.")
            return {"total_iar_criados": 0, "total_iaf_criados": 0}

        pids = [str(p.id) for p in proposicoes]
        mapa_eventos = self.evento_repo.buscar_por_multiplas_proposicoes(pids)

        # Cache de fases
        todas_fases = self.fase_repo.buscar_todas()
        fase_map = {f.id: f.codigo for f in todas_fases}

        # Dicionários de agrupamento
        # {(tipo, regime): [tempos]}
        grupos_total: dict[tuple[str, str], list[int]] = {}
        # {(tipo, regime, fase_codigo): [tempos]}
        grupos_fase: dict[tuple[str, str, str], list[int]] = {}

        for prop in proposicoes:
            tipo = prop.tipo
            regime = prop.regime_tramitacao
            if not tipo or not regime:
                continue

            eventos = mapa_eventos.get(str(prop.id), [])

            # Determina encerramento e tempo decorrido
            tempo_decorrido, data_encerramento = (
                CalcularMetricasService.obter_decorrido_e_encerramento(
                    prop.data_apresentacao, eventos
                )
            )

            # --- Para IAR (Total) ---
            # Apenas proposições concluídas contam para o baseline TOTAL
            if data_encerramento is not None:
                chave_total = (tipo, regime)
                if chave_total not in grupos_total:
                    grupos_total[chave_total] = []
                grupos_total[chave_total].append(tempo_decorrido)

            # --- Para IAF (Fase) ---
            # Calcula o tempo gasto em cada fase concluída pela proposição
            fase_atual = None
            data_entrada = None

            for e in eventos:
                if e.fase_analitica_id is None:
                    continue

                if e.fase_analitica_id != fase_atual:
                    # Finalizou a fase anterior
                    if fase_atual is not None and data_entrada is not None:
                        try:
                            inicio = datetime.strptime(
                                data_entrada[:10], "%Y-%m-%d"
                            ).date()
                            fim = datetime.strptime(
                                e.data_evento[:10], "%Y-%m-%d"
                            ).date()
                            dias = (fim - inicio).days
                            if dias >= 0:
                                fase_codigo = fase_map.get(fase_atual)
                                if fase_codigo:
                                    chave_fase = (tipo, regime, fase_codigo)
                                    if chave_fase not in grupos_fase:
                                        grupos_fase[chave_fase] = []
                                    grupos_fase[chave_fase].append(dias)
                        except ValueError:
                            pass

                    fase_atual = e.fase_analitica_id
                    data_entrada = e.data_evento

            # Se a proposição foi encerrada, a última fase foi concluída na data_encerramento
            if (
                fase_atual is not None
                and data_entrada is not None
                and data_encerramento is not None
            ):
                try:
                    inicio = datetime.strptime(data_entrada[:10], "%Y-%m-%d").date()
                    fim = datetime.strptime(data_encerramento[:10], "%Y-%m-%d").date()
                    dias = (fim - inicio).days
                    if dias >= 0:
                        fase_codigo = fase_map.get(fase_atual)
                        if fase_codigo:
                            chave_fase = (tipo, regime, fase_codigo)
                            if chave_fase not in grupos_fase:
                                grupos_fase[chave_fase] = []
                            grupos_fase[chave_fase].append(dias)
                except ValueError:
                    pass

        # 3. Salva os baselines com n >= 30
        iar_criados = 0
        iaf_criados = 0

        # Salva TOTAL
        for (tipo, regime), tempos in grupos_total.items():
            if len(tempos) >= 30:
                mediana = self.calcular_mediana(tempos)
                baseline = BaselineTramitacao(
                    escopo="TOTAL",
                    tipo=tipo,
                    regime_tramitacao=regime,
                    fase_codigo=None,
                    mediana_dias=mediana,
                    origem_dados="DYNAMIC_CALCULATION",
                )
                self.baseline_repo.salvar(baseline)
                iar_criados += 1
                logger.info(
                    f"Baseline TOTAL dinâmico criado: {tipo} | {regime} = {mediana} dias (n={len(tempos)})"
                )

        # Salva FASE
        for (tipo, regime, fase_codigo), tempos in grupos_fase.items():
            if len(tempos) >= 30:
                mediana = self.calcular_mediana(tempos)
                baseline = BaselineTramitacao(
                    escopo="FASE",
                    tipo=tipo,
                    regime_tramitacao=regime,
                    fase_codigo=fase_codigo,
                    mediana_dias=mediana,
                    origem_dados="DYNAMIC_CALCULATION",
                )
                self.baseline_repo.salvar(baseline)
                iaf_criados += 1
                logger.info(
                    f"Baseline FASE dinâmico criado: {tipo} | {regime} | {fase_codigo} = {mediana} dias (n={len(tempos)})"
                )

        return {
            "total_iar_criados": iar_criados,
            "total_iaf_criados": iaf_criados,
        }
