"""
Serviço de aplicação para listar as movimentações (eventos) de uma proposição.

Substitui o antigo ListarTramitacoesService. Orquestra a busca no banco (cache),
fallback para a API externa via adapter, e normalização de tramitações.
"""

import logging
from typing import Any

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
from application.ports.orgao_legislativo_repository import (
    OrgaoLegislativoRepositoryPort,
)
from application.ports.proposicao_repository import ProposicaoRepositoryPort
from application.ports.senado_adapter import SenadoAdapterPort
from application.services.agregar_por_fase_service import AgregarPorFaseService
from application.services.normalizar_tramitacao_service import (
    NormalizarTramitacaoService,
)
from application.services.reconstruir_periodos_service import ReconstruirPeriodosService
from domain.entities.evento_tramitacao import EventoTramitacao
from domain.entities.orgao_legislativo import CasaLegislativa
from domain.exceptions import ApiException
from domain.value_objects.modo_movimentacao import ModoMovimentacao
from domain.value_objects.periodo_fase import PeriodoFase

logger = logging.getLogger(__name__)


class ListarMovimentacoesService:
    """Busca eventos normalizados, consultando adapters e cache."""

    def __init__(
        self,
        evento_repo: EventoTramitacaoRepositoryPort,
        proposicao_repo: ProposicaoRepositoryPort,
        fase_repo: FaseAnaliticaRepositoryPort,
        orgao_repo: OrgaoLegislativoRepositoryPort,
        camara_adapter: CamaraAdapterPort,
        senado_adapter: SenadoAdapterPort,
        apensamento_repo: ApensamentoRepositoryPort | None = None,
        reconstruir_service: ReconstruirPeriodosService | None = None,
        cache_provider: CacheProvider | None = None,
    ):
        self.evento_repo = evento_repo
        self.proposicao_repo = proposicao_repo
        self.fase_repo = fase_repo
        self.orgao_repo = orgao_repo
        self.camara_adapter = camara_adapter
        self.senado_adapter = senado_adapter
        self.apensamento_repo = apensamento_repo
        self.reconstruir_service = reconstruir_service
        self.cache_provider = cache_provider
        self._agregar_service = AgregarPorFaseService(fase_repo)

    def _extrair_id_numerico(self, id_val: str | int | None) -> int:
        """Extrai o ID numérico puro de uma string que pode conter prefixos (ex: 'camara:123')."""
        if id_val is None:
            return 0
        if isinstance(id_val, int):
            return id_val
        id_str = str(id_val).strip()
        if ":" in id_str:
            try:
                return int(id_str.split(":")[1])
            except ValueError:
                return 0
        try:
            return int(id_str)
        except ValueError:
            return 0

    async def executar(
        self,
        proposicao_id: str,
        modo: ModoMovimentacao = ModoMovimentacao.RESUMIDO,
        client: httpx.AsyncClient | None = None,
    ) -> list[PeriodoFase] | list[EventoTramitacao]:
        """
        Retorna a lista de eventos normalizados para a proposição solicitada.
        Se não existirem no cache, busca na API, normaliza e salva.
        """
        proposicao = None
        # 0. Resolução de slug se necessário (PL-1-2024)
        real_id = proposicao_id
        if "-" in proposicao_id:
            partes = proposicao_id.split("-")
            if len(partes) == 3:
                tipo, numero, ano_str = partes
                try:
                    ano = int(ano_str)
                    p = self.proposicao_repo.buscar_por_codigo(tipo, numero, ano)
                    if p:
                        real_id = str(p.id)
                except ValueError:
                    pass

        # 1. Tentar cache (banco de dados)
        somente_relevantes = modo == ModoMovimentacao.RELEVANTE
        eventos = self.evento_repo.buscar_por_proposicao(
            real_id, somente_relevantes=somente_relevantes
        )

        # 2. Se não está no cache, busca na API (Fail-fast de 5s para o usuário)
        # Se eventos está vazio, verificamos se é porque realmente não há nada no banco
        # ou se é apenas porque não há eventos relevantes (caso modo == RELEVANTE).
        ja_esta_no_cache = len(eventos) > 0 or (
            somente_relevantes and self.evento_repo.existe_algum_evento(real_id)
        )

        if not ja_esta_no_cache:
            proposicao = self.proposicao_repo.buscar_por_id(real_id)

            # Timeout curto para a Web (5s), mas permite maior se for via client (Seed)
            req_timeout = 5 if client is None else 30

            # Determina o adapter e a casa padrão
            dados_brutos = []

            # Se for PL ou PEC, tentamos buscar em AMBAS as casas para unificar o histórico
            tipos_unificaveis = {"PL", "PEC", "PLP", "MPV", "PLC"}

            tipo_prop = proposicao.tipo if proposicao else None
            numero_prop = proposicao.numero if proposicao else None
            ano_prop = proposicao.ano if proposicao else None

            # Tenta limpar o ID de prefixos para compatibilidade com buscas na API
            real_id_limpo = real_id.split(":")[-1]
            real_id_num = int(real_id_limpo) if real_id_limpo.isdigit() else None

            if not proposicao and real_id.isdigit():
                # IDs numéricos legados podem ter sido migrados para o formato prefixado.
                # Resolve antes de ir para a API para evitar FK violation ao salvar eventos.
                proposicao = self.proposicao_repo.buscar_por_id(
                    f"camara:{real_id}"
                ) or self.proposicao_repo.buscar_por_id(f"senado:{real_id}")
                if proposicao:
                    real_id = proposicao.id

            if not proposicao and real_id_num is not None:
                # Tenta descobrir o tipo se não tiver proposicao (fallback para IDs diretos)
                # Neste caso mantemos a lógica sequencial original
                dados_brutos = await self.camara_adapter.buscar_tramitacoes_brutas(
                    self._extrair_id_numerico(real_id), client=client
                )
                casa_padrao = CasaLegislativa.CAMARA
                if not dados_brutos:
                    dados_brutos = await self.senado_adapter.buscar_tramitacoes_brutas(
                        self._extrair_id_numerico(real_id),
                        client=client,
                        timeout=req_timeout,
                    )
                    casa_padrao = CasaLegislativa.SENADO
            elif proposicao and tipo_prop in tipos_unificaveis:
                # LÓGICA DE UNIFICAÇÃO (CROSSOVER)
                logger.info(
                    f"Iniciando busca unificada para {proposicao.nome_canonico}"
                )

                # 1. Buscar IDs em ambas as casas
                id_camara = None
                id_senado = None

                if "Câmara" in (proposicao.orgao_origem or ""):
                    id_camara = self._extrair_id_numerico(proposicao.id)
                    cache_key = f"crossover:resolvido:camara:{tipo_prop.lower()}:{numero_prop}:{ano_prop}"
                    if self.cache_provider:
                        cached_val = self.cache_provider.get(cache_key)
                        if cached_val is not None:
                            id_senado = (
                                None if cached_val == "nenhum" else int(cached_val)
                            )
                            logger.info(
                                f"⚡ ID correspondente no Senado obtido via cache: {id_senado}"
                            )

                    # Se não temos no cache, busca na API externa e salva
                    if id_senado is None and (
                        not self.cache_provider
                        or self.cache_provider.get(cache_key) is None
                    ):
                        try:
                            # Tenta achar o correspondente no Senado
                            id_senado = (
                                await self.senado_adapter.buscar_id_por_identificacao(
                                    tipo_prop, numero_prop, ano_prop, client=client
                                )
                            )
                            # Fallback para PLC se for PL da Câmara (comum em proposições antigas)
                            if not id_senado and tipo_prop == "PL":
                                id_senado = await self.senado_adapter.buscar_id_por_identificacao(
                                    "PLC", numero_prop, ano_prop, client=client
                                )

                            # Salva o ID correspondente no Redis
                            if self.cache_provider:
                                val_to_cache = str(id_senado) if id_senado else "nenhum"
                                self.cache_provider.set(
                                    cache_key, val_to_cache, ttl_seconds=604800
                                )
                        except (
                            ApiException,
                            httpx.TimeoutException,
                            httpx.RequestError,
                        ) as e:
                            logger.warning(
                                f"⚠️ Crossover com o Senado para a proposição {proposicao.id} ignorado por instabilidade de rede: {e}"
                            )
                            id_senado = None

                    # Verificação de integridade: garante que o Senado refere-se à mesma proposição
                    if id_senado:
                        try:
                            p_sen = await self.senado_adapter.buscar_por_id(
                                id_senado, client=client
                            )
                            if p_sen:
                                # Se o Senado diz que veio da Câmara com o mesmo nome canônico, ou se o nome é idêntico
                                match = (proposicao.nome_canonico in p_sen.tags) or (
                                    p_sen.nome_canonico == proposicao.nome_canonico
                                )
                                if not match:
                                    logger.warning(
                                        f"Crossover ignorado: {p_sen.nome_canonico} no Senado não é {proposicao.nome_canonico}"
                                    )
                                    id_senado = None
                        except (
                            ApiException,
                            httpx.TimeoutException,
                            httpx.RequestError,
                        ) as e:
                            logger.warning(
                                f"⚠️ Crossover ignorado: erro ao buscar detalhes no Senado para ID {id_senado}: {e}"
                            )
                            id_senado = None
                else:
                    id_senado = self._extrair_id_numerico(proposicao.id)
                    # Tenta achar o correspondente na Câmara
                    id_camara = None
                    cache_key = f"crossover:resolvido:senado:{tipo_prop.lower()}:{numero_prop}:{ano_prop}"
                    if self.cache_provider:
                        cached_val = self.cache_provider.get(cache_key)
                        if cached_val is not None:
                            id_camara = (
                                None if cached_val == "nenhum" else int(cached_val)
                            )
                            logger.info(
                                f"⚡ ID correspondente na Câmara obtido via cache: {id_camara}"
                            )

                    # Se não temos no cache, busca na API externa e salva
                    if id_camara is None and (
                        not self.cache_provider
                        or self.cache_provider.get(cache_key) is None
                    ):
                        try:
                            # Primeiro tenta via tags de origem (ex: "PL 2681/1996")
                            for tag in proposicao.tags or []:
                                if " " in tag and "/" in tag:
                                    try:
                                        t_orig, rest = tag.split(" ", 1)
                                        n_orig, a_orig = rest.split("/", 1)
                                        id_camara = await self.camara_adapter.buscar_id_por_identificacao(
                                            t_orig, n_orig, int(a_orig), client=client
                                        )
                                        if id_camara:
                                            logger.info(
                                                f"Origem na Câmara encontrada via tags: {tag} (ID {id_camara})"
                                            )
                                            break
                                    except Exception:
                                        continue

                            # Fallback: busca direta pelo mesmo nome
                            if not id_camara:
                                id_camara = await self.camara_adapter.buscar_id_por_identificacao(
                                    tipo_prop, numero_prop, ano_prop, client=client
                                )

                            # Salva o ID correspondente no Redis
                            if self.cache_provider:
                                val_to_cache = str(id_camara) if id_camara else "nenhum"
                                self.cache_provider.set(
                                    cache_key, val_to_cache, ttl_seconds=604800
                                )
                        except (
                            ApiException,
                            httpx.TimeoutException,
                            httpx.RequestError,
                        ) as e:
                            logger.warning(
                                f"⚠️ Crossover com a Câmara para a proposição {proposicao.id} ignorado por instabilidade de rede: {e}"
                            )
                            id_camara = None

                # 2. Coletar tramitações de onde encontramos ID
                tramitacoes_camara = []
                tramitacoes_senado = []

                if id_camara:
                    try:
                        tramitacoes_camara = (
                            await self.camara_adapter.buscar_tramitacoes_brutas(
                                id_camara, client=client
                            )
                        )
                    except (
                        ApiException,
                        httpx.TimeoutException,
                        httpx.RequestError,
                    ) as e:
                        logger.warning(
                            f"⚠️ Falha de rede ao buscar tramitações da Câmara para crossover de {proposicao.id}: {e}"
                        )
                        tramitacoes_camara = []
                if id_senado:
                    try:
                        tramitacoes_senado = (
                            await self.senado_adapter.buscar_tramitacoes_brutas(
                                id_senado, client=client, timeout=req_timeout
                            )
                        )
                    except (
                        ApiException,
                        httpx.TimeoutException,
                        httpx.RequestError,
                    ) as e:
                        logger.warning(
                            f"⚠️ Falha de rede ao buscar tramitações do Senado para crossover de {proposicao.id}: {e}"
                        )
                        tramitacoes_senado = []

                # 3. Normalizar separadamente (pois cada uma tem sua casa_padrao)
                eventos_unificados = []

                if tramitacoes_camara:
                    norm_c = NormalizarTramitacaoService(
                        self.fase_repo,
                        self.orgao_repo,
                        self.apensamento_repo,
                        CasaLegislativa.CAMARA,
                    )
                    eventos_unificados.extend(
                        norm_c.normalizar(real_id, tramitacoes_camara)
                    )

                if tramitacoes_senado:
                    norm_s = NormalizarTramitacaoService(
                        self.fase_repo,
                        self.orgao_repo,
                        self.apensamento_repo,
                        CasaLegislativa.SENADO,
                    )
                    eventos_unificados.extend(
                        norm_s.normalizar(real_id, tramitacoes_senado)
                    )

                # 4. Ordenar e deduplicar
                # Ordena por data e depois por sequencia
                eventos_unificados.sort(key=lambda e: (e.data_evento, e.sequencia))

                # Deduplicação por data e descrição (caso as casas repitam o mesmo evento de trânsito)
                vistos = set()
                eventos_finais = []
                for e in eventos_unificados:
                    chave = (e.data_evento[:16], e.descricao_original[:50].lower())
                    if chave not in vistos:
                        vistos.add(chave)
                        eventos_finais.append(e)

                eventos = eventos_finais
                # Forçamos a sequencia correta após unificar
                for i, e in enumerate(eventos):
                    e.sequencia = i + 1

                # Sincroniza a proposição
                if eventos:
                    self.evento_repo.salvar_lote(eventos)
                    self._sincronizar_proposicao(proposicao, eventos)
                    self.proposicao_repo.salvar(proposicao)

                    # Reconstrói os períodos para persistência e uso no dashboard (estoque)
                    if self.reconstruir_service:
                        try:
                            self.reconstruir_service.reconstruir_para_proposicao(
                                real_id
                            )
                        except Exception as e:
                            logger.error(
                                f"Erro ao reconstruir períodos no crossover para {real_id}: {e}"
                            )
            else:
                # Fallback para tipos não unificáveis (ou sem proposição)
                id_parts = str(real_id).split(":")
                id_num = self._extrair_id_numerico(real_id)

                if len(id_parts) > 1:
                    prefixo = id_parts[0].lower()
                    if prefixo == "camara" and id_num > 0:
                        dados_brutos = (
                            await self.camara_adapter.buscar_tramitacoes_brutas(
                                id_num, client=client
                            )
                        )
                        casa_padrao = CasaLegislativa.CAMARA
                    elif prefixo == "senado" and id_num > 0:
                        dados_brutos = (
                            await self.senado_adapter.buscar_tramitacoes_brutas(
                                id_num, client=client, timeout=req_timeout
                            )
                        )
                        casa_padrao = CasaLegislativa.SENADO
                    else:
                        dados_brutos = []
                        casa_padrao = CasaLegislativa.CAMARA
                else:
                    # Se não tem prefixo, tenta descobrir onde está
                    dados_brutos = await self.camara_adapter.buscar_tramitacoes_brutas(
                        id_num, client=client
                    )
                    casa_padrao = CasaLegislativa.CAMARA
                    if not dados_brutos:
                        dados_brutos = (
                            await self.senado_adapter.buscar_tramitacoes_brutas(
                                id_num, client=client, timeout=req_timeout
                            )
                        )
                        casa_padrao = CasaLegislativa.SENADO

            if not eventos and dados_brutos:
                # Normalizar e salvar (lógica original)
                normalizer = NormalizarTramitacaoService(
                    fase_repo=self.fase_repo,
                    orgao_repo=self.orgao_repo,
                    apensamento_repo=self.apensamento_repo,
                    casa_padrao=casa_padrao,
                )
                eventos = normalizer.normalizar(real_id, dados_brutos)
                if eventos:
                    self.evento_repo.salvar_lote(eventos)
                    if proposicao:
                        self._sincronizar_proposicao(proposicao, eventos)
                        self.proposicao_repo.salvar(proposicao)

        # 5. Aplica a lógica do modo
        if modo == ModoMovimentacao.RESUMIDO:
            # Se já temos a proposição carregada, usamos ela; caso contrário buscamos
            prop_resumo = proposicao or self.proposicao_repo.buscar_por_id(real_id)

            data_encerramento_obj = None
            if prop_resumo and prop_resumo.data_encerramento:
                try:
                    from datetime import datetime

                    data_encerramento_obj = datetime.fromisoformat(
                        prop_resumo.data_encerramento[:10]
                    ).date()
                except (ValueError, TypeError):
                    pass

            return self._agregar_service.executar(
                eventos,
                proposicao_encerrada=data_encerramento_obj is not None,
                data_encerramento=data_encerramento_obj,
            )

        if modo == ModoMovimentacao.RELEVANTE:
            return [e for e in eventos if e.relevante]

        return eventos

    def _sincronizar_proposicao(self, proposicao: Any, eventos: list[EventoTramitacao]):
        """Atualiza campos da proposição baseando-se no histórico de eventos."""
        if not eventos:
            return

        # 1. Determinar Encerramento
        ultimo_evento_terminal = None
        for e in reversed(eventos):
            if e.eh_evento_terminal:
                ultimo_evento_terminal = e
                break

        if ultimo_evento_terminal:
            proposicao.data_encerramento = ultimo_evento_terminal.data_evento[:10]
            # Se terminou, o status deve refletir isso
            proposicao.status = ultimo_evento_terminal.descricao_original
            proposicao.status_original = ultimo_evento_terminal.descricao_original
        else:
            proposicao.data_encerramento = None
            # Se não terminou, pega o último status relevante ou o último de todos
            for e in reversed(eventos):
                if e.relevante or e.deliberativo:
                    proposicao.status = e.descricao_original
                    proposicao.status_original = e.descricao_original
                    break

        # 2. Atualizar órgão atual
        if eventos[-1].sigla_orgao:
            proposicao.orgao_atual = eventos[-1].sigla_orgao

        # 3. Normalizar e recalcular

        # Garante que temos os métodos de domínio se for um model
        if hasattr(proposicao, "normalizar_campo_status"):
            proposicao.normalizar_campo_status()
            proposicao.atualizar_metricas()
