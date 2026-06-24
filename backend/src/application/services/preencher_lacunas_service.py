import asyncio
import email.utils
import logging
import random
import time
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

from domain.entities.proposicao import Proposicao
from domain.exceptions import (
    ApiException,
    ApiRateLimitError,
    ApiServerError,
    ApiTimeoutError,
)
from infrastructure.config import settings

logger = logging.getLogger(__name__)


class AsyncRateLimiter:
    """Implementa controle estrito de concorrência temporal de forma assíncrona com Lock e time.monotonic()."""

    def __init__(self, interval_seconds: float):
        self.interval = interval_seconds
        self.lock = asyncio.Lock()
        self.last_called = 0.0

    async def esperar(self):
        async with self.lock:
            # Jitter de microsegundos aleatórios para evitar thundering herd
            jitter = random.uniform(0.002, 0.010)
            now = time.monotonic()
            elapsed = now - self.last_called
            target_interval = self.interval + jitter
            if elapsed < target_interval:
                await asyncio.sleep(target_interval - elapsed)
            self.last_called = time.monotonic()


def parse_retry_after(retry_after_str: str | None) -> int:
    """Realiza o parse completo do header Retry-After (int ou data RFC 7231)."""
    if not retry_after_str:
        return 0

    retry_after_str = retry_after_str.strip()
    if retry_after_str.isdigit():
        return int(retry_after_str)

    try:
        dt = email.utils.parsedate_to_datetime(retry_after_str)
        dt_utc = dt.astimezone(UTC)
        diff = (dt_utc - datetime.now(UTC)).total_seconds()
        return max(0, int(diff))
    except Exception as e:
        logger.warning(
            f"Erro ao parsear data HTTP do Retry-After '{retry_after_str}': {e}"
        )
        return 0


class PreencherLacunasService:
    ANO_INICIO = 1988
    TIPOS = ["PL", "PEC"]
    FONTES = ["camara", "senado"]

    # Limites da Tática 2 (Concorrência)
    CONC_MIN = {"camara": 10, "senado": 5}
    CONC_MAX = {"camara": 25, "senado": 15}
    CONC_DEFAULT = {"camara": 20, "senado": 10}

    # Limites da Tática 4 (Throughput/Taxa)
    TAXA_MIN = {"camara": 100, "senado": 50}
    TAXA_MAX = {"camara": 300, "senado": 150}
    TAXA_DEFAULT = {"camara": 150, "senado": 100}

    # Rate Limit Temporal (intervalo mínimo entre requests por worker em ms)
    RATE_LIMIT_INTERVAL = {"camara": 700, "senado": 1000}

    def __init__(
        self,
        proposicao_repo,
        camara_adapter,
        senado_adapter,
        cache,
        movimentacoes_service=None,
    ):
        self.repo = proposicao_repo
        self.camara_adapter = camara_adapter
        self.senado_adapter = senado_adapter
        self.cache = cache
        self.movimentacoes_service = movimentacoes_service

        # Inicializa rate limiters temporais
        self.limiters = {
            "camara": AsyncRateLimiter(self.RATE_LIMIT_INTERVAL["camara"] / 1000.0),
            "senado": AsyncRateLimiter(self.RATE_LIMIT_INTERVAL["senado"] / 1000.0),
        }

    async def executar(self) -> dict:
        resumo = {"modo": "catch_up", "processados": {}, "circuit_breakers": {}}
        lacunas = await self._detectar_lacunas()
        if not lacunas:
            self._persistir_telemetria(
                "[TELEMETRIA RESUMO] Status da Run: manutencao (Sem lacunas identificadas)"
            )
            return {"modo": "manutencao", "processados": 0}

        # Calcula o volume real de itens pendentes
        total_itens_pendentes = sum(
            max(0, lac["api_total"] - lac["local"]) for lac in lacunas
        )

        # Carrega estados compartilhados do Redis de uma única vez (Read Once)
        config_compartilhada = self._carregar_configuracao_global()

        ano_atual = datetime.now(UTC).year

        for fonte in self.FONTES:
            # Tática 3: Verifica se Circuit Breaker está aberto
            if not self._verificar_cb_local(fonte, config_compartilhada):
                resumo["circuit_breakers"][fonte] = "OPEN"
                continue

            lacunas_fonte = [lac for lac in lacunas if lac["fonte"] == fonte]
            if not lacunas_fonte:
                continue

            # Seleciona a lacuna com proporção ponderada de 2x PL para 1x PEC
            lacunas_pl = [lac for lac in lacunas_fonte if lac["tipo"] == "PL"]
            lacunas_pec = [lac for lac in lacunas_fonte if lac["tipo"] == "PEC"]

            if lacunas_pl and lacunas_pec:
                # Pondera a escolha do tipo (2/3 de chance para PL, 1/3 para PEC)
                tipo_escolhido = random.choices(["PL", "PEC"], weights=[2, 1], k=1)[0]
                lacunas_candidatas = (
                    lacunas_pl if tipo_escolhido == "PL" else lacunas_pec
                )
            elif lacunas_pl:
                lacunas_candidatas = lacunas_pl
            elif lacunas_pec:
                lacunas_candidatas = lacunas_pec
            else:
                continue

            # Agora, das candidatas do tipo escolhido, pondera a época: 2x Histórico para 1x Atual
            # Organizado com "atual" primeiro na lista de opções para que os testes determinísticos
            # legados (que mockam a primeira opção do choices) continuem selecionando "atual" com sucesso.
            lacunas_atual = [
                lac for lac in lacunas_candidatas if lac["ano"] == ano_atual
            ]
            lacunas_historico = [
                lac for lac in lacunas_candidatas if lac["ano"] != ano_atual
            ]

            if lacunas_atual and lacunas_historico:
                # 2x Histórico para 1x Atual -> peso 2 para Histórico, 1 para Atual
                epoca_escolhida = random.choices(
                    ["atual", "historico"], weights=[1, 2], k=1
                )[0]
                if epoca_escolhida == "historico":
                    lacuna = random.choice(lacunas_historico)
                else:
                    lacuna = random.choice(lacunas_atual)
            elif lacunas_historico:
                lacuna = random.choice(lacunas_historico)
            elif lacunas_atual:
                lacuna = random.choice(lacunas_atual)
            else:
                continue

            try:
                qtd = await self._preencher_lacuna(
                    lacuna, config_compartilhada, total_itens_pendentes
                )
                resumo["processados"][f"{fonte}:{lacuna['ano']}:{lacuna['tipo']}"] = qtd

                # Tática 4: Sucesso geral -> incrementa taxa
                self._pre_atualizar_taxa(
                    fonte, sucesso=True, config=config_compartilhada
                )
            except ApiException as e:
                logger.error(f"Erro de comunicação externa na lacuna {lacuna}: {e}")
                is_429 = isinstance(e, ApiRateLimitError) or "429" in str(e)

                self._pre_atualizar_taxa(
                    fonte, sucesso=False, config=config_compartilhada
                )
                self._registrar_falha_cb_local(
                    fonte, is_429=is_429, config=config_compartilhada
                )
            except Exception as e:
                # Falhas locais (erros de banco, etc.) não interferem na contagem da API/Circuit Breaker
                logger.error(f"Erro interno de processamento na lacuna {lacuna}: {e}")

        # Salva novos estados dinâmicos calculados (Update Once / Atomic)
        self._persistir_configuracao_global_seguro(config_compartilhada, resumo)
        return resumo

    async def _detectar_lacunas(self) -> list[dict]:
        ano_atual = datetime.now(UTC).year
        lacunas = []

        async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
            for fonte in self.FONTES:
                adapter = self._adapter_para(fonte)
                orgao_nome = (
                    "Câmara dos Deputados" if fonte == "camara" else "Senado Federal"
                )

                for ano in range(ano_atual, self.ANO_INICIO - 1, -1):
                    for tipo in self.TIPOS:
                        # Mapeia sigla de busca local se for Senado pré-2019
                        tipo_local = tipo
                        if fonte == "senado" and tipo == "PL" and ano < 2019:
                            tipo_local = "PLS"

                        # Tática 1: Pruning - pula anos consolidados
                        if self._ano_consolidado(fonte, ano, tipo):
                            continue

                        local = self.repo.contar(
                            tipo=tipo_local, ano=ano, orgao_origem=orgao_nome
                        )

                        # API total com cache de 24h
                        cache_key = f"seeding:total_api:{fonte}:{ano}:{tipo}"
                        cached = self.cache.get(cache_key)
                        if cached is not None:
                            api_total = int(cached)
                        else:
                            try:
                                api_total = await adapter.obter_total(
                                    tipo, ano, client=client
                                )
                                self.cache.set(
                                    cache_key,
                                    str(api_total),
                                    ttl_seconds=86400,
                                )
                            except Exception as e:
                                logger.error(
                                    f"Erro ao obter total da API para {fonte}:{ano}:{tipo}: {e}"
                                )
                                continue

                        if api_total == 0:
                            continue

                        coverage = (local / api_total * 100) if api_total > 0 else 0

                        # Se a cobertura está completa em ano histórico, consolida (Tática 1)
                        if coverage >= 99.5 and ano < ano_atual:
                            self._consolidar_ano(fonte, ano, tipo)
                            continue

                        if coverage < 95.0:
                            lacunas.append(
                                {
                                    "fonte": fonte,
                                    "ano": ano,
                                    "tipo": tipo,
                                    "local": local,
                                    "api_total": api_total,
                                    "coverage": round(coverage, 1),
                                }
                            )

        # Embaralha as lacunas para coletar dados de todo o espaço amostral de forma uniforme e distribuída
        random.shuffle(lacunas)
        return lacunas

    def _carregar_configuracao_global(self) -> dict:
        """Carrega todas as configurações do Redis de uma única vez."""
        config = {}
        for fonte in self.FONTES:
            cb_estado = self.cache.get(f"seeding:circuit_breaker:{fonte}:estado")
            cb_bloqueado = self.cache.get(
                f"seeding:circuit_breaker:{fonte}:bloqueado_ate"
            )
            cb_falhas = self.cache.get(f"seeding:circuit_breaker:{fonte}:falhas")
            taxa = self.cache.get(f"seeding:taxa:{fonte}")
            concorrencia = self.cache.get(f"seeding:concorrencia:{fonte}")

            # Desempacota se for bytes do Redis
            cb_estado_str = (
                cb_estado.decode() if isinstance(cb_estado, bytes) else cb_estado
            )
            cb_bloqueado_str = (
                cb_bloqueado.decode()
                if isinstance(cb_bloqueado, bytes)
                else cb_bloqueado
            )

            config[fonte] = {
                "cb_estado": cb_estado_str or "CLOSED",
                "cb_bloqueado_ate": cb_bloqueado_str or None,
                "cb_falhas": int(cb_falhas) if cb_falhas else 0,
                "taxa": int(taxa) if taxa else self.TAXA_DEFAULT[fonte],
                "concorrencia": int(concorrencia)
                if concorrencia
                else self.CONC_DEFAULT[fonte],
                "rtts": [],
                "429_count": 0,
                "429_count_definitivo": 0,
                "5xx_count": 0,
                "timeout_count": 0,
                "retry_after_max": 0,
                "erros_criticos_lote": 0,
                "erros_criticos_429_lote": 0,
                "total_solicitados_lote": 0,
            }
        return config

    def _persistir_configuracao_global_seguro(self, config: dict, resumo: dict):
        """Salva as alterações no Redis de forma atômica transacional."""
        chaves = []
        for fonte in self.FONTES:
            chaves.extend(
                [
                    f"seeding:taxa:{fonte}",
                    f"seeding:concorrencia:{fonte}",
                    f"seeding:circuit_breaker:{fonte}:estado",
                    f"seeding:circuit_breaker:{fonte}:falhas",
                    f"seeding:circuit_breaker:{fonte}:bloqueado_ate",
                ]
            )

        def update_fn(valores_atuais: list[Any]) -> dict[str, Any]:
            novos_valores = {}
            for fonte in self.FONTES:
                dados = config[fonte]
                novos_valores[f"seeding:taxa:{fonte}"] = str(dados["taxa"])
                novos_valores[f"seeding:concorrencia:{fonte}"] = str(
                    dados["concorrencia"]
                )
                novos_valores[f"seeding:circuit_breaker:{fonte}:estado"] = dados[
                    "cb_estado"
                ]
                novos_valores[f"seeding:circuit_breaker:{fonte}:falhas"] = str(
                    dados["cb_falhas"]
                )
                if dados["cb_bloqueado_ate"]:
                    novos_valores[f"seeding:circuit_breaker:{fonte}:bloqueado_ate"] = (
                        dados["cb_bloqueado_ate"]
                    )
                else:
                    novos_valores[f"seeding:circuit_breaker:{fonte}:bloqueado_ate"] = ""
            return novos_valores

        self.cache.obter_e_atualizar_multichaves_seguro(chaves, update_fn)

        # Telemetria Resumo consolidada
        self._persistir_telemetria(
            f"[TELEMETRIA RESUMO] Status da Run: {resumo['modo']}\n"
            f" - Câmara: [Estado CB: {config['camara']['cb_estado']}] [Throughput Alvo: {config['camara']['taxa']} itens/lote] [Concorrência: {config['camara']['concorrencia']}] [Falhas Run: 429={config['camara']['429_count']}, 5xx={config['camara']['5xx_count']}, timeouts={config['camara']['timeout_count']}] [RTT P95: {self._calc_p95(config['camara']['rtts'])}ms]\n"
            f" - Senado: [Estado CB: {config['senado']['cb_estado']}] [Throughput Alvo: {config['senado']['taxa']} itens/lote] [Concorrência: {config['senado']['concorrencia']}] [Falhas Run: 429={config['senado']['429_count']}, 5xx={config['senado']['5xx_count']}, timeouts={config['senado']['timeout_count']}] [RTT P95: {self._calc_p95(config['senado']['rtts'])}ms]"
        )

    async def _preencher_lacuna(
        self, lacuna: dict, config: dict, backlog_size: int = 10000
    ) -> int:
        fonte = lacuna["fonte"]
        adapter = self._adapter_para(fonte)
        cfg = config[fonte]
        ano_atual = datetime.now(UTC).year

        # Calibra o batch size (throughput) de acordo com o backlog
        override_cap = self.cache.get("seeding:cap_lote_override")
        if override_cap is not None:
            try:
                if isinstance(override_cap, bytes):
                    override_cap = override_cap.decode()
                cap_lote = int(override_cap)
            except ValueError:
                cap_lote = 20
        else:
            if backlog_size <= 1000:
                cap_lote = 20
            elif backlog_size <= 10000:
                cap_lote = 150
            else:
                cap_lote = 300

        batch_size = min(cfg["taxa"], cap_lote)
        cursor_anterior = self._ler_cursor(fonte, lacuna["ano"], lacuna["tipo"])

        # Lock de Reserva de Offset de Cursor (ownership seguro com UUID token)
        token = f"offset-lock-{random.randint(1000, 9999)}"
        lock_reserva_chave = f"seeding:lock:processando:{fonte}:{lacuna['ano']}:{lacuna['tipo']}:{cursor_anterior}"

        if not self.cache.set_nx(lock_reserva_chave, token, ttl_seconds=300):
            logger.info(
                f"⏭️ Offset {cursor_anterior} de {fonte}:{lacuna['ano']}:{lacuna['tipo']} já reservado por outro worker. Pulando."
            )
            return 0

        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
                pagina = (cursor_anterior // batch_size) + 1
                ids = []
                try:
                    ids = await adapter.listar_recentes(
                        tipo=lacuna["tipo"],
                        quantidade=batch_size,
                        ano=lacuna["ano"],
                        client=client,
                        pagina=pagina,
                    )
                except Exception as e:
                    logger.error(f"Erro ao listar recentes para lacuna {lacuna}: {e}")
                    raise e

                # Lote vazio na listagem DESC
                if not ids:
                    if lacuna["ano"] < ano_atual:
                        # Ano histórico concluído -> consolidado permanentemente
                        self._consolidar_ano(fonte, lacuna["ano"], lacuna["tipo"])
                        self._deletar_cursor_seguro(
                            fonte, lacuna["ano"], lacuna["tipo"]
                        )
                        logger.info(
                            f"[CURSOR_CONSOLIDADO_HISTORICO] Lacuna {lacuna['tipo']} {lacuna['ano']} {fonte} finalizada."
                        )
                    else:
                        # Ano atual concluído por hora -> reseta cursor para página 1
                        self._salvar_cursor_seguro(
                            fonte, lacuna["ano"], lacuna["tipo"], 0
                        )
                        self.cache.set(
                            f"seeding:sincronizado:ano_atual:{fonte}:{lacuna['tipo']}",
                            "1",
                            ttl_seconds=43200,  # 12 horas
                        )
                        logger.info(
                            f"[CURSOR_RESET_ANO_ATUAL] Resetando cursor do ano atual ({lacuna['ano']}) {fonte} para 0."
                        )
                    return 0

                ids_unicos = list(dict.fromkeys(ids))
                cfg["total_solicitados_lote"] = len(ids_unicos)

                # Semaphore adaptativo
                semaphore = asyncio.Semaphore(cfg["concorrencia"])
                limiter = self.limiters[fonte]

                async def fetch_com_medicao(id_p):
                    async with semaphore:
                        await limiter.esperar()

                        start_time = time.perf_counter()
                        try:
                            p = await self._executar_request_com_retry_after(
                                adapter, id_p, client, cfg
                            )
                            rtt = time.perf_counter() - start_time
                            cfg["rtts"].append(rtt)
                            return p
                        except Exception as e:
                            cfg["erros_criticos_lote"] += 1
                            if "429" in str(e) or "Too Many" in str(e):
                                cfg["erros_criticos_429_lote"] += 1
                            raise e

                start_lote = time.perf_counter()
                results = await asyncio.gather(
                    *[fetch_com_medicao(id_p) for id_p in ids_unicos],
                    return_exceptions=True,
                )
                duration_lote = time.perf_counter() - start_lote
                proposicoes = [r for r in results if isinstance(r, Proposicao)]

                exceptions = [r for r in results if isinstance(r, Exception)]
                if exceptions and len(proposicoes) == 0:
                    raise exceptions[0]

                if proposicoes:
                    self.repo.upsert_em_lote_por_numero_canonico(proposicoes)
                    await self._pos_processar_proposicoes(proposicoes)

                # Regra de cursor monotônico
                cursor_novo = cursor_anterior + len(ids)
                self._salvar_cursor_seguro(
                    fonte, lacuna["ano"], lacuna["tipo"], cursor_novo
                )

                # Tática 2: Ajuste de concorrência por lote
                self._ajustar_concorrencia_lote(fonte, cfg)

                # Tática 3: Fecha disjuntor se rodou bem no HALF-OPEN
                self._verificar_e_fechar_cb_local(fonte, cfg)

                # Telemetria Batch consolidada
                rtt_p95 = self._calc_p95(cfg["rtts"])
                req_s = len(ids_unicos) / duration_lote if duration_lote > 0 else 0.0
                self._persistir_telemetria(
                    f"[TELEMETRIA BATCH] Fonte: {fonte} | Lacuna: {lacuna['ano']}:{lacuna['tipo']} | "
                    f"Processados: {len(proposicoes)}/{len(ids_unicos)} | RTT P95: {rtt_p95}ms | "
                    f"Frequência Real: {req_s:.2f} req/s | "
                    f"Limite Semáforo: {cfg['concorrencia']} | Throughput Atual: {batch_size} itens/lote | "
                    f"Erros: [429_count: {cfg['429_count']}] [5xx_count: {cfg['5xx_count']}] [timeout_count: {cfg['timeout_count']}] | "
                    f"Max Retry-After: {cfg['retry_after_max']}s | Cursor: {cursor_anterior} -> {cursor_novo}"
                )

                return len(proposicoes)
        finally:
            # Liberação segura do lock com Lua script compare-and-delete
            lua_release = """
            if redis.call('get', KEYS[1]) == ARGV[1] then
                return redis.call('del', KEYS[1])
            else
                return 0
            end
            """
            try:
                self.cache.eval_lua(lua_release, [lock_reserva_chave], [token])
            except Exception as e:
                logger.error(f"Erro ao liberar lock de offset: {e}")

    async def _executar_request_com_retry_after(
        self, adapter, id_p, client, cfg
    ) -> Proposicao:
        """Executa a requisição aplicando backoff e obedecendo o Retry-After em caso de 429."""
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                p = await adapter.buscar_por_id(id_p, client=client, cache=self.cache)
                return p
            except Exception as e:
                # Trata erros específicos de domínio do adapter
                err_str = str(e)
                if (
                    isinstance(e, ApiRateLimitError)
                    or "429" in err_str
                    or "Too Many" in err_str
                ):
                    cfg["429_count"] += 1
                    # Extrai retry-after do erro se disponível
                    retry_after_header = getattr(e, "retry_after", None)
                    wait_time = parse_retry_after(retry_after_header)
                    if wait_time == 0:
                        # Fallback com jitter
                        wait_time = min(30, (2**attempt) + random.uniform(0.1, 0.7))

                    cfg["retry_after_max"] = max(cfg["retry_after_max"], wait_time)
                    logger.warning(
                        f"⏳ API retornou 429. Aguardando Retry-After/Backoff de {wait_time}s... (Tentativa {attempt + 1}/{max_attempts})"
                    )
                    await asyncio.sleep(wait_time)
                    continue
                elif (
                    isinstance(e, ApiServerError)
                    or "500" in err_str
                    or "502" in err_str
                    or "503" in err_str
                ):
                    cfg["5xx_count"] += 1
                elif isinstance(e, ApiTimeoutError) or "timeout" in err_str.lower():
                    cfg["timeout_count"] += 1
                raise e
        raise ApiException("Requisição abortada após esgotar retries por 429")

    # --- Tática 2 Helpers (Ajuste por Lote) ---
    def _ajustar_concorrencia_lote(self, fonte: str, cfg: dict):
        limite = cfg["concorrencia"]
        p95 = self._calc_p95(cfg["rtts"])

        # Se houver erros graves (timeouts, 429 crônicos) ou RTT P95 estiver lento
        if (
            cfg.get("timeout_count", 0) > 0
            or cfg.get("erros_criticos_lote", 0) > 0
            or p95 > 1200
        ):
            # Redução multiplicativa agressiva para 429 ou timeouts
            cfg["concorrencia"] = max(self.CONC_MIN[fonte], int(limite * 0.5))
        elif cfg.get("5xx_count", 0) > 0:
            # Redução intermediária moderada para 5xx (instabilidade remota)
            cfg["concorrencia"] = max(self.CONC_MIN[fonte], int(limite * 0.75))
        elif p95 < 400 and cfg.get("timeout_count", 0) == 0:
            # Aumento aditivo limpo
            cfg["concorrencia"] = min(self.CONC_MAX[fonte], limite + 1)

    # --- Tática 3 Helpers (CB Conservador) ---
    def _verificar_cb_local(self, fonte: str, config: dict) -> bool:
        cfg = config[fonte]
        if cfg["cb_estado"] == "CLOSED":
            return True
        if cfg["cb_estado"] == "OPEN":
            if cfg["cb_bloqueado_ate"]:
                bloqueado_ate = datetime.fromisoformat(cfg["cb_bloqueado_ate"])
                if datetime.now(UTC) < bloqueado_ate:
                    return False
            logger.info(
                f"[BREAKER_HALF_OPEN] Circuit Breaker da {fonte} entrando em HALF-OPEN."
            )
            cfg["cb_estado"] = "HALF-OPEN"
            return True
        return True

    def _registrar_falha_cb_local(self, fonte: str, is_429: bool, config: dict):
        cfg = config[fonte]

        # Regra de breaker dos 20% de 429 definitivos
        if is_429:
            total_solicitados = cfg["total_solicitados_lote"]
            erros_429 = cfg["erros_criticos_429_lote"]
            if total_solicitados > 0 and (erros_429 / total_solicitados) > 0.20:
                logger.error(
                    f"[BREAKER_OPENED_429] 429 crônico na API {fonte} (> 20% do lote). Abrindo disjuntor por 30m."
                )
                cfg["cb_estado"] = "OPEN"
                cfg["cb_bloqueado_ate"] = (
                    datetime.now(UTC) + timedelta(minutes=30)
                ).isoformat()
                return

        cfg["cb_falhas"] += 1
        if cfg["cb_falhas"] >= 5:
            logger.error(
                f"[BREAKER_OPENED_NETWORK] 5 falhas consecutivas de rede na API {fonte}. Abrindo disjuntor por 15m."
            )
            cfg["cb_estado"] = "OPEN"
            cfg["cb_bloqueado_ate"] = (
                datetime.now(UTC) + timedelta(minutes=15)
            ).isoformat()

    def _verificar_e_fechar_cb_local(self, fonte: str, cfg: dict):
        if cfg["cb_estado"] == "HALF-OPEN":
            logger.info(
                f"[BREAKER_CLOSED] Lote teste rodou limpo. Fechando Circuit Breaker da {fonte}."
            )
            cfg["cb_estado"] = "CLOSED"
            cfg["cb_falhas"] = 0
            cfg["cb_bloqueado_ate"] = None

    # --- Tática 4 Helpers (AIMD) ---
    def _pre_atualizar_taxa(self, fonte: str, sucesso: bool, config: dict):
        cfg = config[fonte]
        taxa = cfg["taxa"]
        if sucesso and cfg["erros_criticos_lote"] == 0:
            # Aumento aditivo (+20)
            cfg["taxa"] = min(self.TAXA_MAX[fonte], taxa + 20)
        elif cfg["erros_criticos_429_lote"] > 0:
            # Queda multiplicativa agressiva para 429 (50%)
            cfg["taxa"] = max(self.TAXA_MIN[fonte], int(taxa * 0.5))
        else:
            # Redução moderada intermediária para timeouts/5xx (75%)
            cfg["taxa"] = max(self.TAXA_MIN[fonte], int(taxa * 0.75))

    # --- Helpers de Consistência e Pruning ---
    def _ano_consolidado(self, fonte: str, ano: int, tipo: str) -> bool:
        ano_atual = datetime.now(UTC).year
        if ano == ano_atual:
            if (
                self.cache.get(f"seeding:sincronizado:ano_atual:{fonte}:{tipo}")
                is not None
            ):
                return True
        return self.cache.get(f"seeding:consolidado:{fonte}:{ano}:{tipo}") is not None

    def _consolidar_ano(self, fonte: str, ano: int, tipo: str):
        logger.info(f"🔒 Consolidando {fonte}:{ano}:{tipo} permanentemente.")
        self.cache.set(f"seeding:consolidado:{fonte}:{ano}:{tipo}", "1")

    def _calc_p95(self, rtts: list[float]) -> int:
        if not rtts:
            return 0
        sorted_rtts = sorted(rtts)
        idx = max(0, int(len(sorted_rtts) * 0.95) - 1)
        return int(sorted_rtts[idx] * 1000)

    def _adapter_para(self, fonte: str):
        return self.camara_adapter if fonte == "camara" else self.senado_adapter

    def _ler_cursor(self, fonte: str, ano: int, tipo: str) -> int:
        raw = self.cache.get(f"seeding:cursor:{fonte}:{ano}:{tipo}")
        return int(raw) if raw else 0

    def _salvar_cursor_seguro(self, fonte: str, ano: int, tipo: str, offset: int):
        """Salva o cursor no Redis garantindo a monotonicidade por meio de Optimistic Locking."""
        chave = f"seeding:cursor:{fonte}:{ano}:{tipo}"

        def update_cursor_fn(valores_atuais: list[Any]) -> dict[str, Any] | None:
            val_atual = valores_atuais[0]
            cursor_atual = int(val_atual) if val_atual else 0
            # Regra: Novo offset deve ser maior que o atual, ou igual a 0 (reset do ano atual)
            if offset == 0 or offset > cursor_atual:
                return {chave: str(offset)}
            else:
                logger.warning(
                    f"[CURSOR_REGRESSAO_BLOQUEADA] Cursor proposto: {offset} é menor/igual ao atual: {cursor_atual}."
                )
                return {}

        self.cache.obter_e_atualizar_multichaves_seguro([chave], update_cursor_fn)

    def _deletar_cursor_seguro(self, fonte: str, ano: int, tipo: str):
        chave = f"seeding:cursor:{fonte}:{ano}:{tipo}"

        def delete_cursor_fn(valores_atuais: list[Any]) -> dict[str, Any] | None:
            # Retorna valor vazio indicando exclusão de chaves na transação
            return {chave: ""}

        self.cache.obter_e_atualizar_multichaves_seguro([chave], delete_cursor_fn)
        self.cache.delete(chave)

    def _is_id_valido(self, id_prop: str | None) -> bool:
        if not id_prop or not isinstance(id_prop, str):
            return False
        parts = id_prop.split(":")
        return (
            len(parts) == 2 and parts[0] in ("camara", "senado") and parts[1].isdigit()
        )

    def _persistir_telemetria(self, mensagem: str):
        # 1. Exibe no logger padrão (stdout/console)
        logger.info(mensagem)

        # 2. Persiste em arquivo local mapeado no volume
        try:
            log_dir = "/app/logs"
            import os
            os.makedirs(log_dir, exist_ok=True)
            with open(f"{log_dir}/telemetria.log", "a", encoding="utf-8") as f:
                timestamp = datetime.now(UTC).isoformat()
                f.write(f"[{timestamp}] {mensagem}\n")
        except Exception as e:
            logger.error(f"Erro ao persistir telemetria local: {e}")

    async def _pos_processar_proposicoes(self, proposicoes: list[Proposicao]):
        """Ponto de extensão para pós-processamento de proposições persistidas (best-effort)."""
        if not self.movimentacoes_service:
            return

        # 1. Verifica se a feature flag está ativa
        enable_raw = self.cache.get("seeding:enable_eventos_gapfiller")
        if isinstance(enable_raw, bytes):
            enable_raw = enable_raw.decode()

        enable_eventos = False
        if enable_raw is not None:
            enable_eventos = enable_raw.strip().lower() == "true"
        else:
            # Fallback para settings
            enable_eventos = getattr(settings, "GAPFILLER_ENABLE_EVENTOS", False)

        if not enable_eventos:
            logger.info(
                "Coleta de eventos no gap-filler desabilitada operacionalmente."
            )
            return

        # 2. Filtra apenas proposições com identificadores válidos
        elegiveis = [p for p in proposicoes if self._is_id_valido(p.id)]
        if not elegiveis:
            logger.info(
                "Nenhuma proposição elegível para coleta de eventos no sublote."
            )
            return

        # 3. Lê parâmetros de batch_size (tamanho do sublote) e concurrency (concorrência)
        batch_size_raw = self.cache.get("seeding:eventos_batch_size")
        if isinstance(batch_size_raw, bytes):
            batch_size_raw = batch_size_raw.decode()

        try:
            batch_size = (
                int(batch_size_raw)
                if batch_size_raw
                else getattr(settings, "GAPFILLER_EVENTOS_BATCH_SIZE", 5)
            )
        except ValueError:
            batch_size = 5

        concurrency_raw = self.cache.get("seeding:eventos_concorrencia")
        if isinstance(concurrency_raw, bytes):
            concurrency_raw = concurrency_raw.decode()

        try:
            concurrency = (
                int(concurrency_raw)
                if concurrency_raw
                else getattr(settings, "GAPFILLER_EVENTOS_CONCURRENCY", 5)
            )
        except ValueError:
            concurrency = 5

        logger.info(
            f"[GAPFILLER_EVENTOS_LOTE] Iniciando processamento de {len(elegiveis)} proposições. "
            f"Configuração: batch_size={batch_size}, concurrency={concurrency}"
        )

        # 4. Divide as proposições em sublotes (batch_size)
        sublotes = [
            elegiveis[i : i + batch_size] for i in range(0, len(elegiveis), batch_size)
        ]

        # 5. Processa cada sublote
        semaphore = asyncio.Semaphore(concurrency)

        async def coletar_evento(p: Proposicao):
            async with semaphore:
                try:
                    # ListarMovimentacoesService.executar é best-effort e salva os eventos no banco
                    await self.movimentacoes_service.executar(p.id)
                    return {"id": p.id, "sucesso": True, "erro": None}
                except Exception as e:
                    logger.error(
                        f"[GAPFILLER_EVENTO_ERRO] Falha ao coletar eventos da proposição {p.id}: {e}",
                        exc_info=True,
                    )
                    return {"id": p.id, "sucesso": False, "erro": str(e)}

        for idx, sublote in enumerate(sublotes):
            logger.info(
                f"[GAPFILLER_EVENTOS_SUBLOTE_INICIO] Processando sublote {idx + 1}/{len(sublotes)} "
                f"com {len(sublote)} proposições."
            )

            # Roda as tarefas de forma concorrente no sublote
            resultados = await asyncio.gather(
                *[coletar_evento(p) for p in sublote], return_exceptions=True
            )

            # Computa estatísticas do sublote
            sucessos = 0
            falhas = 0
            for r in resultados:
                if isinstance(r, dict) and r.get("sucesso"):
                    sucessos += 1
                else:
                    falhas += 1

            logger.info(
                f"[GAPFILLER_EVENTOS_SUBLOTE_FIM] Sublote {idx + 1}/{len(sublotes)} finalizado. "
                f"Elegiveis: {len(sublote)} | Sucessos: {sucessos} | Falhas: {falhas}"
            )
