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
        self.timeout = 25  # Timeout aumentado para lidar com lentidão da API

    async def _get_with_retry(
        self,
        client: httpx.AsyncClient,
        url: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> httpx.Response:
        """Helper para realizar GET com retry básico em caso de erros temporários."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                resp = await client.get(
                    url, params=params, headers=headers, timeout=self.timeout
                )
                if (
                    resp.status_code in [429, 500, 502, 503, 504]
                    and attempt < max_retries - 1
                ):
                    wait_time = (attempt + 1) * 2
                    logger.warning(
                        f"Erro {resp.status_code} no Senado. Tentativa {attempt + 1}/{max_retries}. Aguardando {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                    continue
                # Se for 404, não faz sentido dar raise se quisermos tratar o fallback
                if resp.status_code != 404:
                    resp.raise_for_status()
                return resp
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    logger.warning(
                        f"Falha na conexão com Senado: {e}. Tentativa {attempt + 1}/{max_retries}. Aguardando {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    raise
        raise httpx.RequestError("Máximo de tentativas excedido")

    async def buscar_por_id(self, id_materia: int) -> Optional[Proposicao]:
        """
        Busca detalhes de uma matéria legislativa no Senado.
        Tenta primeiro o endpoint de matéria (legado mas compatível com idMateria)
        e depois o de processo se necessário.
        """
        url = f"{self.base_url}/materia/{id_materia}"
        headers = {"Accept": "application/json"}

        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                resp = await self._get_with_retry(client, url, headers=headers)
                if resp.status_code == 404:
                    url = f"{self.base_url}/processo/{id_materia}?v=1"
                    resp = await self._get_with_retry(client, url, headers=headers)

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
                            resp_proc = await client.get(
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
                    resp_proc = await client.get(
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

    async def listar_recentes(
        self, tipo: str, quantidade: int = 10, ano: Optional[int] = None
    ) -> List[int]:
        """Busca uma lista de IDs das matérias de um determinado tipo no Senado, opcionalmente por ano."""
        url = f"{self.base_url}/processo"

        if not ano:
            from datetime import date

            ano = date.today().year

        params = {
            "sigla": tipo,
            "ano": ano,
        }
        headers = {"Accept": "application/json"}
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                resp = await self._get_with_retry(
                    client, url, params=params, headers=headers
                )
                resp.raise_for_status()
                dados = resp.json()

                if not isinstance(dados, list):
                    dados = [dados] if dados else []

                if not dados and not ano:
                    params["ano"] = ano - 1
                    resp = await client.get(
                        url, params=params, headers=headers, timeout=self.timeout
                    )
                    if resp.status_code == 200:
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
                    f"Erro ao listar matérias no Senado (tipo={tipo}, ano={ano}): {e}"
                )
                return []

    async def buscar_tramitacoes_brutas(self, id_materia: int) -> List[dict]:
        """
        Retorna payload bruto de cada tramitação do Senado.
        """
        headers = {"Accept": "application/json"}

        id_processo = id_materia
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                url_mat = f"{self.base_url}/materia/{id_materia}"
                resp_mat = await client.get(url_mat, headers=headers, timeout=10)
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
                resp = await self._get_with_retry(client, url, headers=headers)
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
        limite = params.get("itens", 100)
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
