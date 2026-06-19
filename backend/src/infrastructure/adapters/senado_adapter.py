import asyncio
import logging
import re

import httpx

from domain.classificacao_preditiva import (
    classificar_tema_economico,
    identificar_autor_executivo,
)
from domain.entities.proposicao import Proposicao
from domain.exceptions import (
    ApiConnectionError,
    ApiException,
    ApiRateLimitError,
    ApiServerError,
    ApiTimeoutError,
)

logger = logging.getLogger(__name__)


class SenadoAdapter:
    """
    Adaptador para a API de Dados Abertos do Senado Federal.
    Realiza a coleta e normalização de matérias e tramitações.
    """

    def __init__(self, base_url: str = "https://legis.senado.leg.br/dadosabertos"):
        self.base_url = base_url
        # Timeout granular: 3s para conectar (Fail Fast), 8s para ler os dados
        self.default_timeout = httpx.Timeout(8.0, connect=3.0)

    async def _get_with_retry(
        self,
        client: httpx.AsyncClient,
        url: str,
        params=None,
        headers=None,
        timeout=None,
        max_retries=3,
        backoff_type="exponential",
    ) -> httpx.Response:
        """Helper para realizar requisições com retry rápido em caso de erro."""
        for attempt in range(max_retries):
            # Escala connect de 3.0s até 6.0s se timeout não for passado
            if timeout is None:
                connect_timeout = min(3.0 + (attempt * 1.5), 6.0)
                timeout_config = httpx.Timeout(8.0, connect=connect_timeout)
            else:
                timeout_config = timeout
                connect_timeout = getattr(timeout_config, "connect", 3.0)

            try:
                resp = await client.get(
                    url, params=params, headers=headers, timeout=timeout_config
                )

                if resp.status_code == 429:
                    retry_after = resp.headers.get("Retry-After")
                    if attempt < max_retries - 1:
                        wait_time = 1 if backoff_type == "flat" else (3 * (attempt + 1))
                        logger.warning(
                            f"⏳ Senado aplicando Rate Limit. Aguardando {wait_time}s..."
                        )
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        raise ApiRateLimitError(
                            "Senado com limite de requisições excedido",
                            retry_after=retry_after,
                        )

                if resp.status_code >= 500:
                    if attempt < max_retries - 1:
                        delay = 1 if backoff_type == "flat" else (2**attempt)
                        logger.warning(
                            f"🔄 Senado instável (Erro {resp.status_code}). Aguardando {delay}s antes da tentativa {attempt + 1}/{max_retries}..."
                        )
                        await asyncio.sleep(delay)
                        continue
                    else:
                        raise ApiServerError(
                            f"Erro no servidor do Senado: {resp.status_code}",
                            resp.status_code,
                        )

                if resp.status_code != 404:
                    resp.raise_for_status()
                return resp
            except (httpx.ConnectTimeout, httpx.ConnectError) as e:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"🔌 Erro de conexão com Senado ({type(e).__name__}). Possível Cold Start ou DNS lento. "
                        f"Tentando reconectar ({attempt + 1}/{max_retries}) com connect={connect_timeout}s..."
                    )
                    delay = 1 if backoff_type == "flat" else 2
                    await asyncio.sleep(delay)
                else:
                    raise ApiConnectionError(
                        f"Falha de conexão com o Senado: {type(e).__name__}"
                    ) from e
            except httpx.TimeoutException as e:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"🕒 Timeout no Senado (connect={connect_timeout}s). Tentando novamente ({attempt + 1}/{max_retries})..."
                    )
                    delay = 1 if backoff_type == "flat" else 1
                    await asyncio.sleep(delay)
                else:
                    raise ApiTimeoutError("Timeout na API do Senado") from e
            except Exception as e:
                if isinstance(e, ApiException):
                    raise e
                if attempt < max_retries - 1:
                    logger.warning(
                        f"🔄 Falha inesperada no Senado: {type(e).__name__}. Retentando..."
                    )
                    delay = 1 if backoff_type == "flat" else 1
                    await asyncio.sleep(delay)
                else:
                    raise ApiConnectionError(
                        f"Falha inesperada no Senado: {type(e).__name__}"
                    ) from e
        raise ApiConnectionError("Senado indisponível após múltiplas tentativas")

    async def buscar_por_id(
        self, id_materia: int, client: httpx.AsyncClient | None = None, cache=None
    ) -> Proposicao | None:
        """
        Busca detalhes de uma matéria legislativa no Senado.
        Tenta primeiro o endpoint de matéria (legado mas compatível com idMateria)
        e depois o de processo se necessário.
        """
        url = f"{self.base_url}/materia/{id_materia}"
        url_emendas = f"{self.base_url}/materia/emendas/{id_materia}"
        headers = {"Accept": "application/json"}

        _client = client or httpx.AsyncClient(follow_redirects=True)
        try:
            try:
                # Verifica a degradação seletiva de emendas
                emendas_degradadas = False
                if cache is not None:
                    try:
                        if cache.get("seeding:degradacao:senado:emendas") is not None:
                            emendas_degradadas = True
                    except Exception as e:
                        logger.error(f"Erro ao verificar chave de degradação: {e}")

                # Dispara requisições da matéria principal e emendas em paralelo
                task_materia = self._get_with_retry(
                    _client,
                    url,
                    headers=headers,
                    timeout=httpx.Timeout(12.0, connect=3.0),
                    max_retries=3,
                    backoff_type="exponential",
                )

                if emendas_degradadas:
                    logger.warning(
                        f"⚠️ [DEGRADACAO_ATIVA] Senado com API de emendas degradada. Ignorando endpoint para ID {id_materia}."
                    )

                    async def mock_emendas():
                        return httpx.Response(
                            404, request=httpx.Request("GET", url_emendas)
                        )

                    task_emendas = mock_emendas()
                else:
                    task_emendas = self._get_with_retry(
                        _client,
                        url_emendas,
                        headers=headers,
                        timeout=httpx.Timeout(6.0, connect=3.0),
                        max_retries=2,
                        backoff_type="flat",
                    )

                res_materia, res_emendas = await asyncio.gather(
                    task_materia, task_emendas, return_exceptions=True
                )

                # Processa a requisição principal da matéria com fallback para o endpoint de processo se der 404
                if isinstance(res_materia, Exception):
                    if (
                        isinstance(res_materia, httpx.HTTPStatusError)
                        and res_materia.response.status_code == 404
                    ):
                        url_proc = f"{self.base_url}/processo/{id_materia}?v=1"
                        resp = await self._get_with_retry(
                            _client,
                            url_proc,
                            headers=headers,
                            timeout=httpx.Timeout(15.0, connect=3.0),
                            max_retries=2,
                            backoff_type="linear",
                        )
                    else:
                        raise res_materia
                else:
                    resp = res_materia
                    if resp.status_code == 404:
                        url_proc = f"{self.base_url}/processo/{id_materia}?v=1"
                        resp = await self._get_with_retry(
                            _client,
                            url_proc,
                            headers=headers,
                            timeout=httpx.Timeout(15.0, connect=3.0),
                            max_retries=2,
                            backoff_type="linear",
                        )

                resp.raise_for_status()
                dados_brutos = resp.json()

                # Processa a requisição de emendas de forma resiliente a falhas
                numero_emendas = None
                if isinstance(res_emendas, Exception):
                    if (
                        isinstance(res_emendas, httpx.HTTPStatusError)
                        and res_emendas.response.status_code == 404
                    ):
                        numero_emendas = 0
                    else:
                        logger.warning(
                            f"Não foi possível buscar emendas para proposição {id_materia} no Senado: {res_emendas}"
                        )
                        # Ativa degradação seletiva por 15 minutos se falhou por timeout ou 429
                        if cache is not None:
                            try:
                                err_str = str(res_emendas)
                                is_transient = (
                                    isinstance(
                                        res_emendas,
                                        (ApiTimeoutError, ApiRateLimitError),
                                    )
                                    or "timeout" in err_str.lower()
                                    or "429" in err_str
                                )
                                if is_transient:
                                    logger.warning(
                                        f"⚠️ [DEGRADACAO_INICIADA] Falha transitória em emendas ({type(res_emendas).__name__}). Ativando degradação por 15m."
                                    )
                                    cache.set(
                                        "seeding:degradacao:senado:emendas",
                                        "1",
                                        ttl_seconds=900,
                                    )
                            except Exception as ce:
                                logger.error(f"Erro ao setar chave de degradação: {ce}")
                        numero_emendas = 0
                else:
                    if res_emendas.status_code == 200:
                        data_emendas = res_emendas.json()
                        emendas_obj = (
                            data_emendas.get("EmendaMateria", {})
                            .get("Materia", {})
                            .get("Emendas", {})
                            .get("Emenda", [])
                        )
                        if isinstance(emendas_obj, list):
                            numero_emendas = len(emendas_obj)
                        elif isinstance(emendas_obj, dict):
                            numero_emendas = 1
                        else:
                            numero_emendas = 0
                    elif res_emendas.status_code == 404:
                        numero_emendas = 0

                if (
                    "DetalheMateria" in dados_brutos
                    and "Materia" in dados_brutos["DetalheMateria"]
                ):
                    dados = dados_brutos["DetalheMateria"]["Materia"]
                    identificacao_obj = dados.get("IdentificacaoMateria", {})
                    identificacao = identificacao_obj.get(
                        "DescricaoIdentificacaoMateria", ""
                    )

                    # Tenta extrair outros números (origem na Câmara)
                    outros_numeros = dados.get("OutrosNumerosDaMateria", {}).get(
                        "OutroNumeroDaMateria", []
                    )
                    if isinstance(outros_numeros, dict):
                        outros_numeros = [outros_numeros]

                    tags = []
                    for on in outros_numeros:
                        ident = on.get("IdentificacaoMateria", {})
                        sigla = ident.get("SiglaSubtipoMateria")
                        num = ident.get("NumeroMateria")
                        ano_on = ident.get("AnoMateria")
                        if sigla and num and ano_on:
                            try:
                                num_str = str(int(num))
                            except ValueError:
                                num_str = str(num)
                            tags.append(f"{sigla} {num_str}/{ano_on}")

                    id_processo = identificacao_obj.get("IdentificacaoProcesso")
                    if id_processo:
                        try:
                            resp_proc = await _client.get(
                                f"{self.base_url}/processo/{id_processo}?v=1",
                                headers=headers,
                                timeout=self.default_timeout,
                            )
                            if resp_proc.status_code == 200:
                                dados_proc = resp_proc.json()
                                prop = self._processar_dados_processo(
                                    dados_proc,
                                    str(id_materia),
                                    numero_emendas=numero_emendas,
                                )
                                if prop:
                                    prop.tags = tags
                                    return prop
                        except Exception:
                            pass

                    # Fallback para processamento manual se não tiver processo ou falhar
                    ementa = dados.get("DadosBasicosMateria", {}).get(
                        "EmentaMateria", "Sem ementa"
                    )
                    data_apresentacao = dados.get("DadosBasicosMateria", {}).get(
                        "DataApresentacao", ""
                    )
                    autor_nome = dados.get("DadosBasicosMateria", {}).get(
                        "Autor", "Não informado"
                    )
                    situacao_atual_obj = (
                        dados.get("SituacaoAtual", {})
                        .get("Autuacoes", {})
                        .get("Autuacao", {})
                    )
                    if isinstance(situacao_atual_obj, list):
                        situacao_atual_obj = (
                            situacao_atual_obj[0] if situacao_atual_obj else {}
                        )
                    situacao = situacao_atual_obj.get("Situacao", {})
                    status_atual = situacao.get("DescricaoSituacao", "Sem status")
                    data_ultima_movimentacao = situacao.get("DataSituacao", "")

                    tipo = ""
                    numero = 0
                    ano = 0
                    if identificacao and " " in identificacao:
                        parts = identificacao.split(" ")
                        tipo = parts[0]
                        if len(parts) > 1 and "/" in parts[1]:
                            num_str, ano_str = parts[1].split("/", 1)
                            numero = int(num_str) if num_str.isdigit() else 0
                            ano = int(ano_str) if ano_str.isdigit() else 0

                    if not data_ultima_movimentacao:
                        data_ultima_movimentacao = data_apresentacao

                    regime_obj = dados.get("DadosBasicosMateria", {}).get(
                        "RegimeTramitacao", {}
                    )
                    regime_raw = (
                        (regime_obj.get("DescricaoRegime") or "").upper()
                        if isinstance(regime_obj, dict)
                        else ""
                    )
                    regime_tramitacao = (
                        "URGENCIA" if "URG" in regime_raw else "ORDINARIO"
                    )

                    # ML variables for fallback
                    # numero_assinaturas:
                    autores_lista = dados.get("Autoria", {}).get("Autor", [])
                    if isinstance(autores_lista, dict):
                        autores_lista = [autores_lista]
                    elif not isinstance(autores_lista, list):
                        autores_lista = []
                    numero_assinaturas = (
                        len(autores_lista)
                        if autores_lista
                        else (1 if autor_nome and autor_nome != "Não informado" else 0)
                    )
                    bloco_legislativo = (
                        autores_lista[0]
                        .get("IdentificacaoParlamentar", {})
                        .get("SiglaPartidoParlamentar", "N/A")
                        if autores_lista and isinstance(autores_lista[0], dict)
                        else "N/A"
                    )

                    # Determine parecer_ccj_favoravel for fallback (simplified, most recent first)
                    parecer_ccj_favoravel = None
                    historico = dados.get("HistoricoTramitacao", {}).get(
                        "Tramitacao", []
                    )
                    if isinstance(historico, dict):
                        historico = [historico]
                    for h in reversed(historico):
                        unidade = (
                            h.get("UnidadeOndeTramitou", {}).get("SiglaUnidade") or ""
                        ).upper()
                        if unidade == "CCJ":
                            texto = (h.get("TextoTramitacao") or "").upper()
                            if "PARECER" in texto and (
                                "DESFAVORÁVEL" in texto
                                or "CONTRÁR" in texto
                                or "CONTRA" in texto
                            ):
                                parecer_ccj_favoravel = False
                                break
                            elif "PARECER" in texto and "FAVORÁVEL" in texto:
                                parecer_ccj_favoravel = True
                                break

                    # Classify power exec and theme via Domain functions
                    autor_e_poder_executivo = identificar_autor_executivo(autor_nome)
                    tema_economico = classificar_tema_economico(ementa)

                    return Proposicao(
                        id=f"senado:{id_materia}",
                        tipo=tipo,
                        numero=str(numero),
                        ano=ano,
                        autor=autor_nome,
                        uf_autor="N/A",
                        orgao_origem="Senado Federal",
                        status=status_atual,
                        ementa=ementa,
                        data_apresentacao=data_apresentacao,
                        data_ultima_movimentacao=data_ultima_movimentacao,
                        orgao_atual="Senado Federal",
                        link_oficial=f"https://wwws.senado.leg.br/ecidadania/visualizacaomateria?id={id_materia}",
                        regime_tramitacao=regime_tramitacao,
                        tags=tags,
                        numero_assinaturas=numero_assinaturas,
                        numero_emendas=numero_emendas,
                        autor_e_poder_executivo=autor_e_poder_executivo,
                        tema_economico=tema_economico,
                        bloco_legislativo=bloco_legislativo,
                        parecer_ccj_favoravel=parecer_ccj_favoravel,
                    )
                elif (
                    "DetalheMateria" in dados_brutos
                    and "Materia" not in dados_brutos["DetalheMateria"]
                ):
                    url_proc = f"{self.base_url}/processo/{id_materia}?v=1"
                    resp_proc = await _client.get(
                        url_proc, headers=headers, timeout=self.default_timeout
                    )
                    if resp_proc.status_code == 200:
                        return self._processar_dados_processo(
                            resp_proc.json(),
                            str(id_materia),
                            numero_emendas=numero_emendas,
                        )
                    return None
                else:
                    return self._processar_dados_processo(
                        dados_brutos, str(id_materia), numero_emendas=numero_emendas
                    )

            except httpx.ConnectError:
                logger.error(
                    f"❌ Erro de CONEXÃO com o Senado para ID {id_materia}. Verifique se o container tem acesso à internet (DNS/Firewall)."
                )
                return None
            except httpx.TimeoutException:
                logger.error(
                    f"⏳ TIMEOUT ao acessar Senado para ID {id_materia} após {self.default_timeout}s."
                )
                return None
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                logger.error(
                    f"Erro de rede ao buscar proposição {id_materia} no Senado: {e}"
                )
                return None
            except Exception as e:
                if isinstance(e, ApiException):
                    raise e
                logger.error(
                    f"Erro inesperado ao processar dados do Senado para ID {id_materia}: {e}"
                )
                return None
        finally:
            if client is None:
                await _client.aclose()

    async def obter_total(
        self, tipo: str, ano: int, client: httpx.AsyncClient | None = None
    ) -> int:
        """Obtém o total de matérias para um tipo e ano na API do Senado."""
        url = f"{self.base_url}/processo"
        params = {"sigla": tipo, "ano": ano}
        headers = {"Accept": "application/json"}
        _client = client or httpx.AsyncClient(follow_redirects=True)
        try:
            resp = await self._get_with_retry(
                _client, url, params=params, headers=headers
            )
            if resp.status_code == 404:
                return 0
            dados = resp.json()
            if not dados:
                return 0
            # A API de processo do Senado retorna uma lista direta ou objeto único
            if isinstance(dados, list):
                return len(dados)
            return 1
        except Exception as e:
            logger.error(
                f"❌ Erro ao obter total do Senado ({tipo}, {ano}): {str(e) or type(e).__name__}"
            )
            raise e
        finally:
            if client is None:
                await _client.aclose()

    async def listar_recentes(
        self,
        tipo: str,
        quantidade: int = 10,
        ano: int | None = None,
        client: httpx.AsyncClient | None = None,
        numero: str | None = None,
        pagina: int = 1,
    ) -> list[int]:
        """Busca uma lista de IDs das matérias de um determinado tipo no Senado, opcionalmente por ano e número."""
        url = f"{self.base_url}/processo"

        if not ano:
            from datetime import date

            ano = date.today().year

        params = {
            "sigla": tipo,
            "ano": ano,
        }
        if numero:
            params["numero"] = numero

        headers = {"Accept": "application/json"}
        _client = client or httpx.AsyncClient(follow_redirects=True)
        try:
            resp = await self._get_with_retry(
                _client, url, params=params, headers=headers
            )
            resp.raise_for_status()
            dados = resp.json()

            if not isinstance(dados, list):
                dados = [dados] if dados else []

            ids = []
            for m in dados:
                try:
                    raw_id = m.get("codigoMateria") or m.get("id")
                    if raw_id is not None:
                        val = str(raw_id)
                        if val.isdigit():
                            ids.append(int(val))
                        else:
                            # Tenta extrair apenas o prefixo numérico (ex: "0113A" -> 113)
                            match = re.match(r"^(\d+)", val)
                            if match:
                                ids.append(int(match.group(1)))
                            else:
                                logger.warning(f"ID não-numérico ignorado: {val}")
                except (ValueError, TypeError, AttributeError) as e:
                    logger.warning(
                        f"Erro ao processar ID {m.get('codigoMateria') or m.get('id')}: {e}"
                    )
                    continue

            # Aplica paginação simulada na lista completa
            start_offset = (pagina - 1) * quantidade
            end_offset = start_offset + quantidade
            return ids[start_offset:end_offset]
        except Exception as e:
            logger.error(f"Erro ao listar recentes do Senado: {e}")
            raise e
        finally:
            if client is None:
                await _client.aclose()

    async def buscar_id_por_identificacao(
        self,
        tipo: str,
        numero: str,
        ano: int,
        client: httpx.AsyncClient | None = None,
    ) -> int | None:
        """Localiza o ID interno do Senado para uma matéria conhecida."""
        ids = await self.listar_recentes(tipo, 1, ano, client=client, numero=numero)
        return ids[0] if ids else None

    async def buscar_tramitacoes_brutas(
        self,
        id_materia: int,
        client: httpx.AsyncClient | None = None,
        timeout: int | None = None,
    ) -> list[dict]:
        """
        Retorna payload bruto de cada tramitação do Senado.
        """
        headers = {"Accept": "application/json"}
        id_processo = id_materia
        _client = client or httpx.AsyncClient(follow_redirects=True)

        try:
            try:
                url_mat = f"{self.base_url}/materia/{id_materia}"
                resp_mat = await _client.get(
                    url_mat, headers=headers, timeout=timeout or self.default_timeout
                )
                if resp_mat.status_code == 200:
                    dados_mat = resp_mat.json()
                    if (
                        "DetalheMateria" in dados_mat
                        and "Materia" in dados_mat["DetalheMateria"]
                    ):
                        id_proc = (
                            dados_mat["DetalheMateria"]["Materia"]
                            .get("IdentificacaoMateria", {})
                            .get("IdentificacaoProcesso")
                        )
                        if id_proc:
                            id_processo = id_proc
            except Exception:
                pass

            url = f"{self.base_url}/processo/{id_processo}?v=1"
            try:
                resp = await self._get_with_retry(
                    _client, url, headers=headers, timeout=timeout
                )
                resp.raise_for_status()
                dados = resp.json()

                brutas = []
                autuacoes = dados.get("autuacoes", [])
                if not autuacoes:
                    return []

                # O Senado agrupa tramitações por 'autuacao' (geralmente uma só)
                brutas = []
                for aut in autuacoes:
                    situacoes = aut.get("situacoes", [])
                    if not situacoes:
                        continue

                    # Garante que as situações da autuação estejam em ordem cronológica (antiga -> nova)
                    # A API costuma retornar invertido ou inconsistente em versões diferentes.
                    # 'inicio' ou 'DataSituacao' é a chave de data.
                    def get_data(s):
                        return s.get("inicio") or s.get("DataSituacao") or ""

                    situacoes_ordenadas = sorted(situacoes, key=get_data)

                    for s in situacoes_ordenadas:
                        data = get_data(s)
                        desc = s.get("descricao") or s.get("DescricaoSituacao")

                        # Extração robusta do órgão
                        orgao = None
                        if s.get("enteAdministrativo"):
                            orgao = s["enteAdministrativo"].get("sigla")
                        if not orgao and s.get("Orgao"):
                            orgao = s["Orgao"].get("SiglaOrgao")
                        if not orgao and s.get("colegiado"):
                            orgao = s["colegiado"].get("sigla")

                        if not data or not desc:
                            continue

                        brutas.append(
                            {
                                "data_hora": data,
                                "sequencia": len(brutas) + 1,
                                "sigla_orgao": orgao,
                                "descricao": desc,
                                "payload_bruto": s,
                            }
                        )

                return brutas

            except Exception as e:
                logger.error(
                    f"Erro ao buscar tramitações brutas do Senado para ID {id_materia} (Processo {id_processo}): {e}"
                )
                return []
        finally:
            if client is None:
                await _client.aclose()

    async def coletar_em_lote(self, params: dict | None = None) -> list[Proposicao]:
        """
        Busca proposições em lote no Senado.
        A API do Senado não possui paginação nativa idêntica à da Câmara no endpoint principal,
        então buscamos por ano/quantidade e limitamos o batch.
        """
        if params is None:
            params = {}

        url = f"{self.base_url}/processo"
        headers = {"Accept": "application/json"}

        # Parâmetros default caso não informados
        if "ano" not in params:
            from datetime import date

            params["ano"] = date.today().year

        # O Senado não tem "itens" na API de processo, mas limitamos no código
        limite = params.get("limite_total", 200)
        ids_coletados = []

        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                # Removemos itens da query string pois a API do senado pode rejeitar parâmetros desconhecidos
                api_params = {k: v for k, v in params.items() if k in ["sigla", "ano"]}

                resp = await self._get_with_retry(
                    client, url, params=api_params, headers=headers
                )
                resp.raise_for_status()
                dados = resp.json()

                if not isinstance(dados, list):
                    dados = [dados] if dados else []

                for m in dados:
                    try:
                        raw_id = m.get("codigoMateria") or m.get("id")
                        if raw_id is not None:
                            val = str(raw_id)
                            if val.isdigit():
                                ids_coletados.append(int(val))
                            else:
                                # Tenta extrair apenas o prefixo numérico (ex: "0113A" -> 42)
                                match = re.match(r"^(\d+)", val)
                                if match:
                                    ids_coletados.append(int(match.group(1)))
                                else:
                                    logger.warning(f"ID não-numérico ignorado: {val}")
                    except (ValueError, TypeError, AttributeError) as e:
                        logger.warning(
                            f"Erro ao processar ID {m.get('codigoMateria') or m.get('id')}: {e}"
                        )
                        continue

                    if len(ids_coletados) >= limite:
                        break

            except Exception as e:
                logger.error(f"Erro na listagem em lote do Senado: {e}")

        # Deduplica os IDs coletados antes de buscar os detalhes externos
        ids_unicos = list(dict.fromkeys(ids_coletados))

        proposicoes_completas = []
        # Limite menor para o Senado pois a API costuma ser mais lenta/instável
        semaphore = asyncio.Semaphore(5)

        async def fetch_full(id_prop: int):
            async with semaphore:
                return await self.buscar_por_id(id_prop)

        tasks = [fetch_full(id_prop) for id_prop in ids_unicos]
        resultados = await asyncio.gather(*tasks, return_exceptions=True)

        for res in resultados:
            if isinstance(res, Proposicao):
                proposicoes_completas.append(res)
            elif isinstance(res, Exception):
                logger.error(f"Erro na coleta em lote de proposição do Senado: {res}")

        return proposicoes_completas

    def _processar_dados_processo(
        self, dados: dict, id_materia: str, numero_emendas: int = 0
    ) -> Proposicao:
        """Processa a estrutura flat retornada pelo endpoint /processo."""
        identificacao = dados.get("identificacao", "")
        ementa = dados.get("conteudo", {}).get("ementa") or dados.get(
            "documento", {}
        ).get("ementa", "Sem ementa")
        data_apresentacao = dados.get("documento", {}).get("dataApresentacao", "")
        autoria = dados.get("autoriaIniciativa", [])
        autor_nome = (
            autoria[0].get("autor", "Não informado") if autoria else "Não informado"
        )

        status_atual = "Sem status"
        data_ultima_movimentacao = ""
        autuacoes = dados.get("autuacoes", [])
        if autuacoes:
            # Pega a última autuação (geralmente só tem uma)
            situacoes = autuacoes[-1].get("situacoes", [])
            if situacoes:
                # Percorre de trás pra frente para pegar o status MAIS RECENTE que tenha descrição
                for s in reversed(situacoes):
                    desc = s.get("descricao") or s.get("DescricaoSituacao")
                    data = s.get("inicio") or s.get("DataSituacao")
                    if desc:
                        status_atual = desc
                        data_ultima_movimentacao = data or ""
                        break

        tipo = ""
        numero = 0
        ano = 0
        if identificacao and " " in identificacao:
            parts = identificacao.split(" ")
            tipo = parts[0]
            if len(parts) > 1 and "/" in parts[1]:
                num_str, ano_str = parts[1].split("/", 1)
                numero = int(num_str) if num_str.isdigit() else 0
                ano = int(ano_str) if ano_str.isdigit() else 0

        if not data_ultima_movimentacao:
            data_ultima_movimentacao = data_apresentacao

        # ML variables
        # numero_assinaturas:
        numero_assinaturas = (
            len(autoria) if isinstance(autoria, list) else (1 if autoria else 0)
        )
        bloco_legislativo = (
            autoria[0].get("partido", "N/A")
            if autoria and isinstance(autoria, list)
            else "N/A"
        )

        # Determine parecer_ccj_favoravel from situations (most recent first)
        parecer_ccj_favoravel = None
        if autuacoes:
            for aut in reversed(autuacoes):
                situacoes = aut.get("situacoes", [])
                for s in reversed(situacoes):
                    # No Senado, o órgão costuma estar em enteAdministrativo ou colegiado
                    orgao = ""
                    if s.get("enteAdministrativo"):
                        orgao = (s["enteAdministrativo"].get("sigla") or "").upper()
                    elif s.get("colegiado"):
                        orgao = (s["colegiado"].get("sigla") or "").upper()

                    if orgao == "CCJ":
                        desc = (s.get("descricao") or "").upper()
                        if "PARECER" in desc and (
                            "DESFAVORÁVEL" in desc
                            or "CONTRÁR" in desc
                            or "CONTRA" in desc
                        ):
                            parecer_ccj_favoravel = False
                            break
                        elif "PARECER" in desc and "FAVORÁVEL" in desc:
                            parecer_ccj_favoravel = True
                            break
                if parecer_ccj_favoravel is not None:
                    break

        # Classify power exec and theme via Domain functions
        autor_e_poder_executivo = identificar_autor_executivo(autor_nome)
        tema_economico = classificar_tema_economico(ementa)

        return Proposicao(
            id=f"senado:{id_materia}",
            tipo=tipo,
            numero=str(numero),
            ano=ano,
            autor=autor_nome,
            uf_autor="N/A",
            orgao_origem="Senado Federal",
            status=status_atual,
            ementa=ementa,
            data_apresentacao=data_apresentacao,
            data_ultima_movimentacao=data_ultima_movimentacao,
            orgao_atual="Senado Federal",
            link_oficial=f"https://wwws.senado.leg.br/ecidadania/visualizacaomateria?id={id_materia}",
            regime_tramitacao="ORDINARIO",
            tags=[],
            numero_assinaturas=numero_assinaturas,
            numero_emendas=numero_emendas,
            autor_e_poder_executivo=autor_e_poder_executivo,
            tema_economico=tema_economico,
            bloco_legislativo=bloco_legislativo,
            parecer_ccj_favoravel=parecer_ccj_favoravel,
        )
