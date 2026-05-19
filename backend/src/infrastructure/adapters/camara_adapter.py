import httpx
import logging
import asyncio
from typing import Optional, List
from domain.entities.proposicao import Proposicao

logger = logging.getLogger(__name__)


class CamaraAdapter:
    """
    Adaptador para a API de Dados Abertos da Câmara dos Deputados.
    Documentação: https://dadosabertos.camara.leg.br/swagger/recursos.html
    """

    def __init__(self):
        self.base_url = "https://dadosabertos.camara.leg.br/api/v2"
        self.timeout = 20  # Timeout aumentado para lidar com lentidão eventual

    async def _get_with_retry(self, client: httpx.AsyncClient, url: str, params: Optional[dict] = None) -> httpx.Response:
        """Helper para realizar GET com retry básico em caso de erros temporários."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                resp = await client.get(url, params=params, timeout=self.timeout)
                if resp.status_code in [429, 500, 502, 503, 504] and attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    logger.warning(f"Erro {resp.status_code} na Câmara. Tentativa {attempt + 1}/{max_retries}. Aguardando {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                resp.raise_for_status()
                return resp
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    logger.warning(f"Falha na conexão com Câmara: {e}. Tentativa {attempt + 1}/{max_retries}. Aguardando {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    raise
        raise httpx.RequestError("Máximo de tentativas excedido")

    async def buscar_por_id(self, id_proposicao: int) -> Optional[Proposicao]:
        url_proposicao = f"{self.base_url}/proposicoes/{id_proposicao}"
        url_autores = f"{url_proposicao}/autores"

        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                resp_prop = await self._get_with_retry(client, url_proposicao)
                dados = resp_prop.json()["dados"]

                resp_autores = await self._get_with_retry(client, url_autores)
                autores_dados = resp_autores.json()["dados"]

                # Processamento de autores
                nomes = [a["nome"] for a in autores_dados]
                autor_principal = nomes[0] if nomes else "Não informado"
                uf_autor = (
                    autores_dados[0].get("siglaUf", "N/A") if autores_dados else "N/A"
                )

                status_info = dados.get("statusProposicao", {})
                data_ultima_movimentacao = status_info.get("dataHora", "")
                orgao_atual = status_info.get("siglaOrgao", "N/A")

                if orgao_atual and any(
                    orgao_atual.startswith(prefix)
                    for prefix in ["PL", "PEC", "MPV", "PLP", "PDL"]
                ):
                    orgao_atual = f"Apensada ao {orgao_atual}"

                return Proposicao(
                    id=str(id_proposicao),
                    tipo=dados.get("siglaTipo", ""),
                    numero=str(dados.get("numero", 0)),
                    ano=dados.get("ano", 0),
                    autor=autor_principal,
                    uf_autor=uf_autor,
                    orgao_origem="Câmara dos Deputados",
                    status=status_info.get("despacho")
                    or status_info.get("descricaoSituacao")
                    or "Sem status",
                    ementa=dados.get("ementa", "") or "Sem ementa",
                    data_apresentacao=dados.get("dataApresentacao", ""),
                    data_ultima_movimentacao=data_ultima_movimentacao,
                    orgao_atual=orgao_atual,
                    link_oficial=f"https://www.camara.leg.br/proposicoesWeb/fichadetramitacao?idProposicao={id_proposicao}",
                    tags=[],
                )

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

    async def listar_recentes(
        self, tipo: str, quantidade: int = 10, ano: Optional[int] = None
    ) -> List[int]:
        """Busca uma lista de IDs das proposições de um determinado tipo, opcionalmente por ano."""
        url = f"{self.base_url}/proposicoes"
        params = {
            "siglaTipo": tipo,
            "ordem": "DESC",
            "ordenarPor": "ano",
            "itens": quantidade,
        }
        if ano:
            params["ano"] = ano
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                resp = await self._get_with_retry(client, url, params=params)
                dados = resp.json()["dados"]
                return [d["id"] for d in dados]
            except Exception as e:
                logger.error(
                    f"Erro ao listar proposições na Câmara (tipo={tipo}, ano={ano}): {e}"
                )
                return []

    async def buscar_tramitacoes_brutas(self, id_proposicao: int) -> List[dict]:
        """
        Retorna payload bruto de cada tramitação da Câmara.
        """
        url = f"{self.base_url}/proposicoes/{id_proposicao}/tramitacoes"
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                resp = await self._get_with_retry(client, url)
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
