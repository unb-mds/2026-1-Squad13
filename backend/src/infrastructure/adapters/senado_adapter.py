import asyncio
import logging

import httpx

from domain.entities.proposicao import Proposicao

logger = logging.getLogger(__name__)


class SenadoAdapter:
    """
    Adaptador para a API de Dados Abertos do Senado Federal.
    Realiza a coleta e normalização de matérias e tramitações.
    """

    def __init__(self, base_url: str = "https://legis.senado.leg.br/dadosabertos"):
        self.base_url = base_url
        self.timeout = 12  # Reduzido para falhar mais rápido em caso de instabilidade

    async def _get_with_retry(
        self,
        client: httpx.AsyncClient,
        url: str,
        params=None,
        headers=None,
        timeout=None,
    ) -> httpx.Response:
        """Helper para realizar requisições com retry rápido em caso de erro."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                resp = await client.get(
                    url, params=params, headers=headers, timeout=timeout or self.timeout
                )

                if resp.status_code == 429:
                    wait_time = 3 * (attempt + 1)
                    logger.warning(f"⏳ Senado aplicando Rate Limit. Aguardando {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue

                if resp.status_code >= 500 and attempt < max_retries - 1:
                    logger.warning(f"🔄 Senado instável (Erro {resp.status_code}). Tentativa {attempt + 1}/{max_retries}...")
                    await asyncio.sleep(1)
                    continue

                if resp.status_code != 404:
                    resp.raise_for_status()
                return resp
            except (httpx.ConnectTimeout, httpx.ConnectError):
                if attempt < max_retries - 1:
                    logger.warning(f"🔌 Erro de conexão com Senado. Tentando reconectar ({attempt + 1}/{max_retries})...")
                    await asyncio.sleep(1)
                else:
                    raise
            except httpx.TimeoutException:
                if attempt < max_retries - 1:
                    logger.warning(f"🕒 Timeout no Senado. Tentando novamente ({attempt + 1}/{max_retries})...")
                    await asyncio.sleep(1)
                else:
                    raise
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"🔄 Falha inesperada no Senado: {type(e).__name__}. Retentando...")
                    await asyncio.sleep(1)
                else:
                    raise
        raise httpx.RequestError("Senado indisponível após múltiplas tentativas")

    async def buscar_por_id(
        self, id_materia: int, client: httpx.AsyncClient | None = None
    ) -> Proposicao | None:
        """
        Busca detalhes de uma matéria legislativa no Senado.
        Tenta primeiro o endpoint de matéria (legado mas compatível com idMateria)
        e depois o de processo se necessário.
        """
        url = f"{self.base_url}/materia/{id_materia}"
        headers = {"Accept": "application/json"}

        _client = client or httpx.AsyncClient(follow_redirects=True)
        try:
            try:
                resp = await self._get_with_retry(_client, url, headers=headers)
                if resp.status_code == 404:
                    url = f"{self.base_url}/processo/{id_materia}?v=1"
                    resp = await self._get_with_retry(_client, url, headers=headers)

                resp.raise_for_status()
                dados_brutos = resp.json()

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
                            # Formato canônico: "PL 2681/1996"
                            tags.append(f"{sigla} {int(num)}/{ano_on}")

                    id_processo = identificacao_obj.get("IdentificacaoProcesso")
                    if id_processo:
                        try:
                            resp_proc = await _client.get(
                                f"{self.base_url}/processo/{id_processo}?v=1",
                                headers=headers,
                                timeout=10,
                            )
                            if resp_proc.status_code == 200:
                                dados_proc = resp_proc.json()
                                prop = self._processar_dados_processo(
                                    dados_proc, str(id_materia)
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

                    return Proposicao(
                        id=str(id_materia),
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
                    )
                elif (
                    "DetalheMateria" in dados_brutos
                    and "Materia" not in dados_brutos["DetalheMateria"]
                ):
                    url_proc = f"{self.base_url}/processo/{id_materia}?v=1"
                    resp_proc = await _client.get(
                        url_proc, headers=headers, timeout=self.timeout
                    )
                    if resp_proc.status_code == 200:
                        return self._processar_dados_processo(
                            resp_proc.json(), str(id_materia)
                        )
                    return None
                else:
                    return self._processar_dados_processo(dados_brutos, str(id_materia))

            except httpx.ConnectError:
                logger.error(
                    f"❌ Erro de CONEXÃO com o Senado para ID {id_materia}. Verifique se o container tem acesso à internet (DNS/Firewall)."
                )
                return None
            except httpx.TimeoutException:
                logger.error(
                    f"⏳ TIMEOUT ao acessar Senado para ID {id_materia} após {self.timeout}s."
                )
                return None
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                logger.error(
                    f"Erro de rede ao buscar proposição {id_materia} no Senado: {e}"
                )
                return None
            except Exception as e:
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
            logger.error(f"Erro ao obter total do Senado ({tipo}, {ano}): {e}")
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
                    if "codigoMateria" in m:
                        ids.append(int(m["codigoMateria"]))
                    elif "id" in m:
                        ids.append(int(m["id"]))

                    if len(ids) >= quantidade:
                        break
                return ids
            except Exception as e:
                logger.error(f"Erro ao listar recentes do Senado: {e}")
                return []
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
                    url_mat, headers=headers, timeout=timeout or 10
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
                    if "codigoMateria" in m:
                        ids_coletados.append(int(m["codigoMateria"]))
                    elif "id" in m:
                        ids_coletados.append(int(m["id"]))

                    if len(ids_coletados) >= limite:
                        break

            except Exception as e:
                logger.error(f"Erro na listagem em lote do Senado: {e}")

        proposicoes_completas = []
        # Limite menor para o Senado pois a API costuma ser mais lenta/instável
        semaphore = asyncio.Semaphore(5)

        async def fetch_full(id_prop: int):
            async with semaphore:
                return await self.buscar_por_id(id_prop)

        tasks = [fetch_full(id_prop) for id_prop in ids_coletados]
        resultados = await asyncio.gather(*tasks, return_exceptions=True)

        for res in resultados:
            if isinstance(res, Proposicao):
                proposicoes_completas.append(res)
            elif isinstance(res, Exception):
                logger.error(f"Erro na coleta em lote de proposição do Senado: {res}")

        return proposicoes_completas

    def _processar_dados_processo(self, dados: dict, id_materia: str) -> Proposicao:
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

        return Proposicao(
            id=str(id_materia),
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
        )
