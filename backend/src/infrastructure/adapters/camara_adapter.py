import requests
import logging
from typing import Optional, List
from domain.entities.proposicao import Proposicao
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class CamaraAdapter:
    """
    Adaptador para a API de Dados Abertos da Câmara dos Deputados.
    Documentação: https://dadosabertos.camara.leg.br/swagger/recursos.html
    """

    def __init__(self):
        self.base_url = "https://dadosabertos.camara.leg.br/api/v2"
        self.session = requests.Session()

        # Configuração de retry para resiliência (5 tentativas com backoff exponencial)
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.timeout = 20  # Timeout aumentado para lidar com lentidão eventual

    def buscar_por_id(self, id_proposicao: int) -> Optional[Proposicao]:
        url_proposicao = f"{self.base_url}/proposicoes/{id_proposicao}"
        url_autores = f"{url_proposicao}/autores"

        try:
            resp_prop = self.session.get(url_proposicao, timeout=self.timeout)
            resp_prop.raise_for_status()
            dados = resp_prop.json()["dados"]

            resp_autores = self.session.get(url_autores, timeout=self.timeout)
            resp_autores.raise_for_status()
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

        except requests.exceptions.RequestException as e:
            logger.error(
                f"Erro de rede ao buscar proposição {id_proposicao} na Câmara: {e}"
            )
            return None
        except (KeyError, IndexError) as e:
            logger.error(
                f"Erro ao processar dados da Câmara para ID {id_proposicao}: {e}"
            )
            return None

    def listar_recentes(
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
        try:
            resp = self.session.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            dados = resp.json()["dados"]
            return [d["id"] for d in dados]
        except Exception as e:
            logger.error(
                f"Erro ao listar proposições na Câmara (tipo={tipo}, ano={ano}): {e}"
            )
            return []

    def buscar_tramitacoes_brutas(self, id_proposicao: int) -> List[dict]:
        """
        Retorna payload bruto de cada tramitação da Câmara.
        """
        url = f"{self.base_url}/proposicoes/{id_proposicao}/tramitacoes"
        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
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
