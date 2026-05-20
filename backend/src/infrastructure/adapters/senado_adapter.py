import httpx
import logging
import asyncio
from typing import Optional, List
from domain.entities.proposicao import Proposicao

logger = logging.getLogger(__name__)


class SenadoAdapter:
    """
    Adaptador para a API de Dados Abertos do Senado Federal.
    Documentação: https://legis.senado.leg.br/dadosabertos/docs/
    """

    def __init__(self):
        self.base_url = "https://legis.senado.leg.br/dadosabertos"
        self.timeout = (
            15  # Reduzido para 15s para não travar o frontend se o Senado estiver fora
        )
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 (MonitorLegislativo/1.0)",
        }

    async def _get_with_retry(
        self,
        client: httpx.AsyncClient,
        url: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        timeout: Optional[int] = None,
    ) -> httpx.Response:
        """Helper para realizar GET com retry básico em caso de erros temporários."""
        max_retries = 2
        # Merge de headers padrão com específicos da chamada
        req_headers = self.headers.copy()
        if headers:
            req_headers.update(headers)

        req_timeout = timeout or self.timeout

        for attempt in range(max_retries):
            try:
                resp = await client.get(
                    url, params=params, headers=req_headers, timeout=req_timeout
                )
                # Erros 5xx ou 429 (Rate Limit) configuram instabilidade/limitação para retry
                if (
                    resp.status_code >= 500 or resp.status_code == 429
                ) and attempt < max_retries - 1:
                    wait_time = 2**attempt  # Backoff exponencial: 1s, 2s, 4s
                    logger.warning(
                        f"⚠️ Erro {resp.status_code} no Senado. Tentativa {attempt + 1}/{max_retries}. Aguardando {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                    continue

                if resp.status_code != 404:
                    resp.raise_for_status()
                return resp
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                # Se for erro de status 4xx (exceto 429 que já tratamos acima), não fazemos retry
                if (
                    isinstance(e, httpx.HTTPStatusError)
                    and e.response.status_code < 500
                    and e.response.status_code != 429
                ):
                    raise

                if attempt < max_retries - 1:
                    wait_time = 2**attempt
                    error_type = type(e).__name__
                    logger.warning(
                        f"🔄 Falha [{error_type}] no Senado: {e}. Tentativa {attempt + 1}/{max_retries}. Aguardando {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    raise
        raise httpx.RequestError("Máximo de tentativas excedido no Senado")

    async def buscar_por_id(
        self, id_materia: int, client: Optional[httpx.AsyncClient] = None
    ) -> Optional[Proposicao]:
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
                                return self._processar_dados_processo(
                                    dados_proc, str(id_materia)
                                )
                        except Exception:
                            pass

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
                    tags=[],
                )

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

    async def listar_recentes(
        self,
        tipo: str,
        quantidade: int = 10,
        ano: Optional[int] = None,
        client: Optional[httpx.AsyncClient] = None,
        numero: Optional[str] = None,
    ) -> List[int]:
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
                logger.error(
                    f"Erro ao listar matérias no Senado (tipo={tipo}, ano={ano}, num={numero}): {e}"
                )
                return []
        finally:
            if client is None:
                await _client.aclose()

    async def buscar_id_por_identificacao(
        self, tipo: str, numero: str, ano: int, client: Optional[httpx.AsyncClient] = None
    ) -> Optional[int]:
        """Localiza o ID interno do Senado para uma matéria conhecida."""
        ids = await self.listar_recentes(tipo, 1, ano, client=client, numero=numero)
        return ids[0] if ids else None

    async def buscar_tramitacoes_brutas(
        self,
        id_materia: int,
        client: Optional[httpx.AsyncClient] = None,
        timeout: Optional[int] = None,
    ) -> List[dict]:
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
                seq = 1
                if autuacoes:
                    situacoes = autuacoes[0].get("situacoes", [])

                    for s in reversed(situacoes):
                        sigla_orgao = s.get("colegiado", {}).get("sigla") or "Senado"
                        descricao = s.get("descricao", "").strip()
                        if descricao:
                            descricao = descricao.capitalize()

                        brutas.append(
                            {
                                "data_hora": s.get("inicio", ""),
                                "sequencia": seq,
                                "sigla_orgao": sigla_orgao,
                                "descricao": descricao,
                                "payload_bruto": s,
                            }
                        )
                        seq += 1

                return brutas
            except Exception as e:
                logger.error(
                    f"Erro ao buscar tramitações brutas do Senado para ID {id_materia} (Processo {id_processo}): {e}"
                )
                return []
        finally:
            if client is None:
                await _client.aclose()

    async def coletar_em_lote(self, params: Optional[dict] = None) -> List[Proposicao]:
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
            situacoes = autuacoes[0].get("situacoes", [])
            if situacoes:
                for s in reversed(situacoes):
                    if s.get("inicio"):
                        data_ultima_movimentacao = s["inicio"]
                        status_atual = s.get("descricao", status_atual)
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
            id=id_materia,
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
            tags=[],
        )
