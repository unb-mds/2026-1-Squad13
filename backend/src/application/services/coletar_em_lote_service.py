import asyncio
import logging

import httpx

from application.ports.apensamento_repository import ApensamentoRepositoryPort
from application.ports.cache_provider import CacheProvider
from application.ports.camara_adapter import CamaraAdapterPort
from application.ports.evento_tramitacao_repository import (
    EventoTramitacaoRepositoryPort,
)
from application.ports.fase_analitica_repository import (
    FaseAnaliticaRepositoryPort,
)
from application.ports.log_coleta_repository import LogColetaRepositoryPort
from application.ports.orgao_legislativo_repository import (
    OrgaoLegislativoRepositoryPort,
)
from application.ports.proposicao_repository import ProposicaoRepositoryPort
from application.ports.senado_adapter import SenadoAdapterPort
from application.services.atualizar_cobertura_service import AtualizarCoberturaService
from application.services.listar_movimentacoes_service import ListarMovimentacoesService
from application.services.reconstruir_periodos_service import ReconstruirPeriodosService
from domain.entities.proposicao import Proposicao
from domain.exceptions import ApiException

logger = logging.getLogger(__name__)


class ColetarEmLoteService:
    """
    Serviço de aplicação responsável pela orquestração da coleta de proposições em lote
    da Câmara e do Senado, garantindo persistência idempotente e isolamento de falhas.
    """

    def __init__(
        self,
        repository: ProposicaoRepositoryPort,
        evento_repo: EventoTramitacaoRepositoryPort,
        fase_repo: FaseAnaliticaRepositoryPort,
        orgao_repo: OrgaoLegislativoRepositoryPort,
        apensamento_repo: ApensamentoRepositoryPort,
        log_repo: LogColetaRepositoryPort,
        camara_adapter: CamaraAdapterPort,
        senado_adapter: SenadoAdapterPort,
        reconstruir_service: ReconstruirPeriodosService | None = None,
        cobertura_service: AtualizarCoberturaService | None = None,
        cache_provider: CacheProvider | None = None,
    ):
        self.repository = repository
        self.evento_repo = evento_repo
        self.fase_repo = fase_repo
        self.orgao_repo = orgao_repo
        self.apensamento_repo = apensamento_repo
        self.log_repo = log_repo
        self.camara_adapter = camara_adapter
        self.senado_adapter = senado_adapter
        self.reconstruir_service = reconstruir_service
        self.cobertura_service = cobertura_service
        self.cache_provider = cache_provider

        self.listar_movimentacoes_service = ListarMovimentacoesService(
            evento_repo=self.evento_repo,
            proposicao_repo=self.repository,
            fase_repo=self.fase_repo,
            orgao_repo=self.orgao_repo,
            camara_adapter=self.camara_adapter,
            senado_adapter=self.senado_adapter,
            apensamento_repo=self.apensamento_repo,
            reconstruir_service=self.reconstruir_service,
            cache_provider=self.cache_provider,
        )

    async def executar_coleta_diaria(self) -> dict:
        """
        Orquestra a coleta diária inteligente baseada em gaps e cotas dinâmicas,
        evitando timeouts e sobrecarga nas APIs oficiais.
        """
        from datetime import datetime

        resumo = {
            "camara": {"status": "sucesso", "itens_coletados": 0, "erro": None},
            "senado": {"status": "sucesso", "itens_coletados": 0, "erro": None},
        }

        current_year = datetime.now().year
        anos = [current_year - 2, current_year - 1, current_year]
        tipos = ["PL", "PEC"]
        fontes = ["camara", "senado"]

        gaps = []

        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            # 1. Análise de gaps locais vs. API
            for ano in anos:
                for tipo in tipos:
                    for fonte in fontes:
                        orgao_nome = (
                            "Câmara dos Deputados"
                            if fonte == "camara"
                            else "Senado Federal"
                        )
                        adapter = (
                            self.camara_adapter
                            if fonte == "camara"
                            else self.senado_adapter
                        )

                        try:
                            local_count = self.repository.contar(
                                tipo=tipo, ano=ano, orgao_origem=orgao_nome
                            )
                            api_total = await adapter.obter_total(
                                tipo, ano, client=client
                            )

                            # Tratamento de resiliência caso API retorne 0 por instabilidade
                            if api_total == 0 and local_count > 0:
                                continue

                            if api_total > local_count:
                                gaps.append(
                                    {
                                        "fonte": fonte,
                                        "ano": ano,
                                        "tipo": tipo,
                                        "local_count": local_count,
                                        "api_total": api_total,
                                        "missing": api_total - local_count,
                                    }
                                )
                        except Exception as e:
                            logger.warning(
                                f"Falha ao analisar gaps para {fonte.upper()} {tipo} {ano}: {e}"
                            )
                            resumo[fonte]["status"] = "falha"
                            resumo[fonte]["erro"] = str(e)

            # Se não houver gaps, encerra mais cedo sem desperdiçar recursos, mas registra logs
            if not gaps:
                logger.info(
                    "🎉 Cobertura de dados em 100% nos anos recentes. Nenhuma coleta de gaps necessária."
                )
                for fonte in fontes:
                    status = resumo[fonte]["status"]
                    itens = resumo[fonte]["itens_coletados"]
                    erro = resumo[fonte]["erro"]
                    self._registrar_log(fonte, status, itens, erro)
                return resumo

            # 2. Priorização dos gaps
            # Prioriza ano mais recente (decrescente) e depois tipo/fonte
            gaps.sort(key=lambda x: x["ano"], reverse=True)

            # Cota global máxima de proposições por rodada para evitar timeouts nas APIs
            # Reduzido de 40 para 20 em 2026-06-17: mitigação de OOM kill
            # observado no Render free tier (512MB) durante execuções de
            # coleta. Ver investigação de footprint de memória do mesmo dia.
            COTA_GLOBAL_MAX = 20
            total_planejado = 0
            tarefas_execucao = []

            for gap in gaps:
                if total_planejado >= COTA_GLOBAL_MAX:
                    break

                # Limite de proposições por grupo por execução (máximo 10)
                limit_grupo = min(gap["missing"], 10)
                if total_planejado + limit_grupo > COTA_GLOBAL_MAX:
                    limit_grupo = COTA_GLOBAL_MAX - total_planejado

                if limit_grupo > 0:
                    gap["limit"] = limit_grupo
                    tarefas_execucao.append(gap)
                    total_planejado += limit_grupo

            logger.info(
                f"📋 Plano de coleta diária inteligente: {len(tarefas_execucao)} tarefas planejadas, "
                f"totalizando no máximo {total_planejado} proposições a coletar."
            )

            # 3. Execução das tarefas planejadas
            for tarefa in tarefas_execucao:
                fonte = tarefa["fonte"]
                ano = tarefa["ano"]
                tipo = tarefa["tipo"]
                limit = tarefa["limit"]
                local_offset = tarefa["local_count"]
                adapter = (
                    self.camara_adapter if fonte == "camara" else self.senado_adapter
                )

                try:
                    logger.info(
                        f"🔎 Coletando {tipo} {ano} da {fonte.upper()} (Offset: {local_offset}, Limite: {limit})..."
                    )

                    ids = []
                    if fonte == "camara":
                        page = (local_offset // limit) + 1
                        ids = await adapter.listar_recentes(
                            tipo=tipo,
                            quantidade=limit,
                            ano=ano,
                            client=client,
                            pagina=page,
                        )
                    else:
                        # Senado não tem paginação, buscamos com margem de segurança e extraímos a fatia
                        ids_raw = await adapter.listar_recentes(
                            tipo=tipo,
                            quantidade=limit + local_offset + 5,
                            ano=ano,
                            client=client,
                        )
                        ids = ids_raw[local_offset : local_offset + limit]

                    if not ids:
                        logger.warning(
                            f"Nenhum ID retornado para {fonte.upper()} {tipo} {ano}"
                        )
                        continue

                    # Deduplica IDs antes de buscar detalhes externos
                    ids_unicos = list(dict.fromkeys(ids))

                    # Semáforo para controlar concorrência das requisições externas para o grupo (máximo 5)
                    sem_grupo = asyncio.Semaphore(5)

                    async def fetch_prop(id_p, sem=sem_grupo, adapt=adapter, f=fonte):
                        async with sem:
                            return await adapt.buscar_por_id(id_p, client=client)

                    tasks_props = [fetch_prop(id_p) for id_p in ids_unicos]
                    results_props = await asyncio.gather(
                        *tasks_props, return_exceptions=True
                    )

                    proposicoes_coletadas = []
                    for idx, res in enumerate(results_props):
                        if isinstance(res, Proposicao):
                            proposicoes_coletadas.append(res)
                        elif isinstance(res, Exception):
                            logger.error(
                                f"❌ Falha na busca detalhada da proposição {ids_unicos[idx]} na {fonte.upper()}: {res}"
                            )

                    if proposicoes_coletadas:
                        # Processa e persiste no banco
                        await self._processar_proposicoes(proposicoes_coletadas, client)
                        resumo[fonte]["itens_coletados"] += len(proposicoes_coletadas)
                        logger.info(
                            f"💾 Salvas {len(proposicoes_coletadas)} proposições de {tipo} {ano} da {fonte.upper()}."
                        )

                        # Atualiza os snapshots de cobertura no banco de dados para sincronizar com o dashboard
                        if self.cobertura_service:
                            try:
                                await self.cobertura_service.atualizar_snapshot(
                                    ano, tipo, fonte
                                )
                                logger.info(
                                    f"✅ Cobertura de snapshot atualizada para {fonte.upper()} {tipo} {ano}."
                                )
                            except Exception as e:
                                logger.warning(
                                    f"Falha ao atualizar snapshot de cobertura: {e}"
                                )

                except Exception as e:
                    logger.exception(
                        f"Erro ao executar tarefa de gap para {fonte.upper()} {tipo} {ano}."
                    )
                    resumo[fonte]["status"] = "parcial"
                    resumo[fonte]["erro"] = str(e)

        # 4. Registrar logs da execução
        for fonte in fontes:
            status = resumo[fonte]["status"]
            itens = resumo[fonte]["itens_coletados"]
            erro = resumo[fonte]["erro"]
            self._registrar_log(fonte, status, itens, erro)

        return resumo

    async def _processar_proposicoes(
        self, proposicoes: list[Proposicao], client: httpx.AsyncClient
    ):
        """Salva proposições e coleta seus eventos de tramitação."""
        # 1. Normaliza status e atualiza métricas básicas para cada proposição no lote
        for prop in proposicoes:
            prop.normalizar_campo_status()
            prop.atualizar_metricas()

        # 2. Upsert das proposições (rápido)
        self.repository.upsert_em_lote_por_numero_canonico(proposicoes)

        # 2. Coleta de eventos (demorado, fazemos em pequenos batches para não estourar)
        batch_size = 10
        for i in range(0, len(proposicoes), batch_size):
            batch = proposicoes[i : i + batch_size]
            tasks = []
            for prop in batch:
                tasks.append(self._processar_uma_proposicao(prop, client))

            resultados = await asyncio.gather(*tasks, return_exceptions=True)
            for idx, res in enumerate(resultados):
                if isinstance(res, Exception):
                    if isinstance(
                        res, (ApiException, httpx.TimeoutException, httpx.RequestError)
                    ):
                        logger.warning(
                            f"⚠️ Falha de comunicação externa ao processar movimentações para a proposição {batch[idx].id}: {res}"
                        )
                    else:
                        logger.error(
                            f"❌ Falha na coleta de {batch[idx].id}: {res}",
                            exc_info=res,
                        )
            logger.info(
                f"Processados eventos para {min(i + batch_size, len(proposicoes))}/{len(proposicoes)} proposições."
            )

    async def _processar_uma_proposicao(
        self, prop: Proposicao, client: httpx.AsyncClient
    ):
        """Coleta eventos para uma única proposição com isolamento transacional e validação de ID."""
        # 1. Validação de ID (prefixo obrigatório para evitar FK violation)
        if ":" not in str(prop.id):
            logger.warning(
                f"⚠️ Proposição com ID inválido (sem prefixo): {prop.id}. Ignorando eventos para evitar FK violation."
            )
            return None

        try:
            return await self.listar_movimentacoes_service.executar(
                prop.id, client=client
            )
        except Exception as e:
            # Se houve erro de banco (ex: FK violation), a sessão fica corrompida
            # e precisa de rollback para que as outras tarefas paralelas não falhem.
            from sqlalchemy.exc import IntegrityError

            err_msg = str(e)
            is_db_error = isinstance(e, IntegrityError) or any(
                term in err_msg or term in type(e).__name__
                for term in [
                    "IntegrityError",
                    "PendingRollbackError",
                    "ForeignKeyViolation",
                    "flush",
                ]
            )

            if is_db_error:
                logger.error(
                    f"❌ Erro de banco ao processar {prop.id}: {err_msg}. Realizando rollback da sessão."
                )
                if hasattr(self.repository, "session"):
                    try:
                        self.repository.session.rollback()
                    except Exception as rb_err:
                        logger.error(f"Falha crítica ao tentar rollback: {rb_err}")

            raise e

    def _registrar_log(self, fonte: str, status: str, itens: int, erro: str = None):
        """Registra o log de execução no banco de dados."""
        self.log_repo.salvar_log(
            fonte=fonte,
            status=status,
            itens_coletados=itens,
            mensagem_erro=erro,
        )
