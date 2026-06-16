import asyncio
import logging

import httpx

from domain.classificacao_preditiva import (
    classificar_tema_economico,
    identificar_autor_executivo,
)
from domain.entities.proposicao import Proposicao
from domain.exceptions import (
    ApiConnectionError,
    ApiRateLimitError,
    ApiServerError,
    ApiTimeoutError,
)

logger = logging.getLogger(__name__)


class CamaraAdapter:
    """
    Adaptador para a API de Dados Abertos da Câmara dos Deputados.
    Documentação: https://dadosabertos.camara.leg.br/swagger/recursos.html
    """

    def __init__(self):
        self.base_url = "https://dadosabertos.camara.leg.br/api/v2"
        # Timeout granular: 3s para conectar (Fail Fast), 8s para ler os dados
        self.default_timeout = httpx.Timeout(8.0, connect=3.0)
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "MonitorLegislativo/1.0",
        }

    async def _get_with_retry(
        self, client: httpx.AsyncClient, url: str, params: dict | None = None
    ) -> httpx.Response:
        """Helper para realizar GET com retry otimizado."""
        max_retries = 3

        for attempt in range(max_retries):
            # Escala connect de 3.0s até 6.0s (3.0 -> 4.5 -> 6.0)
            connect_timeout = min(3.0 + (attempt * 1.5), 6.0)
            timeout_dinamico = httpx.Timeout(8.0, connect=connect_timeout)
            try:
                resp = await client.get(
                    url,
                    params=params,
                    headers=self.headers,
                    timeout=timeout_dinamico,
                )
                if resp.status_code == 429:
                    retry_after = resp.headers.get("Retry-After")
                    if attempt < max_retries - 1:
                        wait_time = 2 * (attempt + 1)
                        logger.warning(
                            f"⏳ Câmara aplicando Rate Limit. Aguardando {wait_time}s..."
                        )
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        raise ApiRateLimitError(
                            "Câmara com limite de requisições excedido",
                            retry_after=retry_after,
                        )

                if resp.status_code >= 500:
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"🔄 Câmara instável (Erro {resp.status_code}). Tentativa {attempt + 1}/{max_retries}..."
                        )
                        await asyncio.sleep(1)
                        continue
                    else:
                        raise ApiServerError(
                            f"Erro no servidor da Câmara: {resp.status_code}",
                            resp.status_code,
                        )

                resp.raise_for_status()
                return resp
            except httpx.TimeoutException as e:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"🕒 Timeout na Câmara (connect={connect_timeout}s). Tentando novamente ({attempt + 1}/{max_retries})..."
                    )
                    await asyncio.sleep(1)
                else:
                    raise ApiTimeoutError("Timeout na API da Câmara") from e
            except httpx.RequestError as e:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"🔌 Falha de conexão/rede na Câmara ({type(e).__name__}, connect={connect_timeout}s). Retentando..."
                    )
                    await asyncio.sleep(1)
                else:
                    raise ApiConnectionError(
                        f"Falha de conexão com a Câmara: {type(e).__name__}"
                    ) from e
        raise ApiConnectionError("Câmara indisponível")

    async def buscar_por_id(
        self, id_proposicao: int, client: httpx.AsyncClient | None = None, cache=None
    ) -> Proposicao | None:
        url_proposicao = f"{self.base_url}/proposicoes/{id_proposicao}"
        url_autores = f"{url_proposicao}/autores"
        url_tramitacoes = f"{url_proposicao}/tramitacoes"

        _client = client or httpx.AsyncClient(follow_redirects=True)
        try:
            try:
                # Dispara as quatro requisições em paralelo
                task_prop = self._get_with_retry(_client, url_proposicao)
                task_autores = self._get_with_retry(_client, url_autores)
                task_relacionadas = self._get_with_retry(
                    _client, f"{url_proposicao}/relacionadas"
                )
                task_tramitacoes = self._get_with_retry(_client, url_tramitacoes)

                res_prop, res_autores, res_relacionadas, res_tramitacoes = (
                    await asyncio.gather(
                        task_prop,
                        task_autores,
                        task_relacionadas,
                        task_tramitacoes,
                        return_exceptions=True,
                    )
                )

                if isinstance(res_prop, Exception):
                    logger.error(
                        f"Erro ao obter dados básicos da Câmara para ID {id_proposicao}: {res_prop}"
                    )
                    raise res_prop

                dados = res_prop.json()["dados"]

                # Processamento de autores (resiliente a falhas)
                if isinstance(res_autores, Exception):
                    logger.warning(
                        f"Erro ao obter autores da Câmara para ID {id_proposicao}: {res_autores}"
                    )
                    autores_dados = []
                else:
                    autores_dados = res_autores.json().get("dados", [])

                nomes = [a["nome"] for a in autores_dados]
                autor_principal = nomes[0] if nomes else "Não informado"
                uf_autor = (
                    autores_dados[0].get("siglaUf", "N/A") if autores_dados else "N/A"
                )
                bloco_legislativo = (
                    autores_dados[0].get("siglaPartido", "N/A") if autores_dados else "N/A"
                )

                status_info = dados.get("statusProposicao", {})
                data_ultima_movimentacao = status_info.get("dataHora", "")
                orgao_atual = status_info.get("siglaOrgao", "N/A")

                if orgao_atual and any(
                    orgao_atual.startswith(prefix)
                    for prefix in ["PL", "PEC", "MPV", "PLP", "PDL"]
                ):
                    orgao_atual = f"Apensada ao {orgao_atual}"

                regime_raw = (dados.get("regime") or "").upper()
                regime_tramitacao = "URGENCIA" if "URG" in regime_raw else "ORDINARIO"

                # Fetch emendas gracefully via related propositions
                numero_emendas = None
                if isinstance(res_relacionadas, Exception):
                    logger.warning(
                        f"⚠️ Não foi possível buscar emendas para {id_proposicao} na Câmara via /relacionadas: {res_relacionadas}"
                    )
                else:
                    relacionadas_dados = res_relacionadas.json().get("dados", [])
                    if isinstance(relacionadas_dados, list):
                        # Filter for amendments: siglas starting with EM (EMP, EMC, EMR, etc) or SBT (Substitutivos)
                        emendas = [
                            r
                            for r in relacionadas_dados
                            if (r.get("siglaTipo") or "").startswith("EM")
                            or (r.get("siglaTipo") or "") == "SBT"
                        ]
                        numero_emendas = len(emendas)
                        logger.info(
                            f"✅ API Câmara: {numero_emendas} emendas encontradas via /relacionadas para {id_proposicao}"
                        )

                # Classify power exec and theme via Domain functions
                autor_e_poder_executivo = identificar_autor_executivo(autor_principal)
                ementa_texto = dados.get("ementa", "") or ""
                tema_economico = classificar_tema_economico(ementa_texto)

                # Determine parecer_ccj_favoravel from tramitacoes
                parecer_ccj_favoravel = None
                if not isinstance(res_tramitacoes, Exception):
                    tramitacoes_dados = res_tramitacoes.json().get("dados", [])
                    for t in tramitacoes_dados:
                        sigla_orgao = (t.get("siglaOrgao") or "").upper()
                        if sigla_orgao in ["CCJ", "CCJR"]:
                            despacho = (t.get("despacho") or "").upper()
                            # Heurística simples: busca por "PARECER" e "FAVORÁVEL"
                            if "PARECER" in despacho and "FAVOR" in despacho:
                                parecer_ccj_favoravel = True
                                break
                            elif "PARECER" in despacho and ("CONTRÁR" in despacho or "CONTRA" in despacho):
                                parecer_ccj_favoravel = False
                                # Não para, pois pode haver um parecer favorável posterior

                return Proposicao(
                    id=f"camara:{id_proposicao}",
                    tipo=dados.get("siglaTipo", ""),
                    numero=str(dados.get("numero", 0)),
                    ano=dados.get("ano", 0),
                    autor=autor_principal,
                    uf_autor=uf_autor,
                    orgao_origem="Câmara dos Deputados",
                    status=status_info.get("despacho")
                    or status_info.get("descricaoSituacao")
                    or "Sem status",
                    ementa=ementa_texto or "Sem ementa",
                    data_apresentacao=dados.get("dataApresentacao", ""),
                    data_ultima_movimentacao=data_ultima_movimentacao,
                    orgao_atual=orgao_atual,
                    link_oficial=f"https://www.camara.leg.br/proposicoesWeb/fichadetramitacao?idProposicao={id_proposicao}",
                    regime_tramitacao=regime_tramitacao,
                    tags=[],
                    numero_assinaturas=len(autores_dados),
                    numero_emendas=numero_emendas,
                    autor_e_poder_executivo=autor_e_poder_executivo,
                    tema_economico=tema_economico,
                    bloco_legislativo=bloco_legislativo,
                    parecer_ccj_favoravel=parecer_ccj_favoravel,
                )

            except httpx.ConnectError:
                logger.error(
                    f"❌ Erro de CONEXÃO com a Câmara para ID {id_proposicao}. Verifique se o container tem acesso à internet (DNS/Firewall)."
                )
                return None
            except httpx.TimeoutException:
                logger.error(
                    f"⏳ TIMEOUT ao acessar Câmara para ID {id_proposicao} após {self.default_timeout}s."
                )
                return None
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                logger.error(
                    f"Erro de rede ao buscar proposição {id_proposicao} na Câmara: {e}"
                )
                return None
            except (KeyError, IndexError) as e:
                logger.error(
                    f"Erro ao processar dados da Câmara para ID {id_proposicao}: {e}"
                )
                return None
        finally:
            if client is None:
                await _client.aclose()

    async def obter_total(
        self, tipo: str, ano: int, client: httpx.AsyncClient | None = None
    ) -> int:
        """Obtém o total de proposições para um tipo e ano na API da Câmara."""
        url = f"{self.base_url}/proposicoes"
        params = {
            "siglaTipo": tipo,
            "ano": ano,
            "itens": 1,  # Só precisamos dos metadados de paginação
        }
        _client = client or httpx.AsyncClient(follow_redirects=True)
        try:
            resp = await self._get_with_retry(_client, url, params=params)
            # A API da Câmara não retorna o total absoluto de forma direta no 'dados',
            # mas podemos inferir pelo link 'last' se existir, ou apenas listar todos.
            # No entanto, a forma mais segura de obter o total para análise de gaps é
            # olhar os links da resposta.
            # Atualização: A API v2 retorna o total nos metadados de links ou podemos fazer uma busca sem limite de itens.
            # Para simplificar e ser rápido, vamos usar o fato de que se pedirmos 1 item,
            # os links 'last' terão o parâmetro 'pagina' que indica o total de itens (já que itens=1).
            links = resp.json().get("links", [])
            for link in links:
                if link["rel"] == "last":
                    from urllib.parse import parse_qs, urlparse

                    parsed = urlparse(link["href"])
                    qs = parse_qs(parsed.query)
                    return int(qs.get("pagina", [0])[0])
            # Se não tiver 'last', e tiver dados, o total é o tamanho de dados da página 1
            return len(resp.json().get("dados", []))
        except Exception as e:
            logger.error(f"Erro ao obter total da Câmara ({tipo}, {ano}): {e}")
            return 0
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
        """Busca uma lista de IDs das proposições filtrando por tipo, ano e opcionalmente número/página."""
        url = f"{self.base_url}/proposicoes"
        params = {
            "siglaTipo": tipo,
            "ordem": "DESC",
            "ordenarPor": "id",
            "itens": quantidade,
            "pagina": pagina,
        }
        if ano:
            params["ano"] = ano
        if numero:
            params["numero"] = numero

        _client = client or httpx.AsyncClient(follow_redirects=True)
        try:
            resp = await self._get_with_retry(_client, url, params=params)
            dados = resp.json()["dados"]
            return [d["id"] for d in dados]
        except Exception as e:
            logger.error(
                f"Erro ao listar proposições na Câmara (tipo={tipo}, ano={ano}, num={numero}): {e}"
            )
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
        """Localiza o ID interno da Câmara para uma proposição conhecida."""
        ids = await self.listar_recentes(tipo, 1, ano, client=client, numero=numero)
        return ids[0] if ids else None

    async def buscar_tramitacoes_brutas(
        self, id_proposicao: int, client: httpx.AsyncClient | None = None
    ) -> list[dict]:
        """
        Retorna payload bruto de cada tramitação da Câmara.
        """
        url = f"{self.base_url}/proposicoes/{id_proposicao}/tramitacoes"
        _client = client or httpx.AsyncClient(follow_redirects=True)
        try:
            try:
                resp = await self._get_with_retry(_client, url)
                dados = resp.json()["dados"]

                brutas = []
                for d in dados:
                    desc_tram = d.get("descricaoTramitacao", "").strip()
                    despacho = d.get("despacho", "").strip()

                    descricao_partes = []
                    if desc_tram:
                        descricao_partes.append(desc_tram)
                    if despacho and despacho != desc_tram:
                        descricao_partes.append(despacho)

                    descricao_consolidada = " - ".join(descricao_partes)
                    if descricao_consolidada:
                        descricao_consolidada = descricao_consolidada.capitalize()

                    brutas.append(
                        {
                            "data_hora": d.get("dataHora", ""),
                            "sequencia": d.get("sequencia", 0),
                            "sigla_orgao": d.get("siglaOrgao", "N/A"),
                            "descricao": descricao_consolidada,
                            "payload_bruto": d,
                        }
                    )

                return brutas
            except Exception as e:
                logger.error(
                    f"Erro ao buscar tramitações brutas da Câmara para ID {id_proposicao}: {e}"
                )
                return []
        finally:
            if client is None:
                await _client.aclose()

    async def coletar_em_lote(self, params: dict | None = None) -> list[Proposicao]:
        """
        Busca proposições em lote utilizando paginação automática (máximo 100 itens/página).
        Garante o retorno completo dos objetos Proposicao buscando os detalhes de cada um.
        """
        url = f"{self.base_url}/proposicoes"
        if params is None:
            params = {}

        # Otimiza paginação para o limite máximo da API da Câmara (100)
        limite_total = params.get("limite_total", 500)

        # Cria uma cópia para não poluir os parâmetros passados com dados internos
        api_params = params.copy()
        if "limite_total" in api_params:
            del api_params["limite_total"]

        api_params["itens"] = 100
        api_params["pagina"] = 1

        ids_coletados = []

        async with httpx.AsyncClient(follow_redirects=True) as client:
            while len(ids_coletados) < limite_total:
                try:
                    resp = await self._get_with_retry(client, url, params=api_params)
                    dados = resp.json().get("dados", [])

                    if not dados:
                        break

                    ids_coletados.extend([d["id"] for d in dados])

                    # Corta se exceder o limite solicitado
                    if len(ids_coletados) >= limite_total:
                        ids_coletados = ids_coletados[:limite_total]
                        break

                    # Verifica se há próxima página baseando-se nos links de HATEOAS
                    links = resp.json().get("links", [])
                    has_next = any(link.get("rel") == "next" for link in links)

                    if not has_next:
                        break

                    api_params["pagina"] += 1
                except Exception as e:
                    logger.error(
                        f"Erro na paginação da Câmara (página {params.get('pagina')}): {e}"
                    )
                    break

        # Deduplica os IDs coletados antes de buscar os detalhes externos
        ids_unicos = list(dict.fromkeys(ids_coletados))

        # Busca os detalhes completos para montar as entidades Proposicao
        proposicoes_completas = []
        semaphore = asyncio.Semaphore(
            15
        )  # Limite de concorrência para não sobrecarregar

        async def fetch_full(id_prop: int):
            async with semaphore:
                return await self.buscar_por_id(id_prop)

        tasks = [fetch_full(id_prop) for id_prop in ids_unicos]
        resultados = await asyncio.gather(*tasks, return_exceptions=True)

        for res in resultados:
            if isinstance(res, Proposicao):
                proposicoes_completas.append(res)
            elif isinstance(res, Exception):
                logger.error(f"Erro na coleta em lote de proposição: {res}")

        return proposicoes_completas
