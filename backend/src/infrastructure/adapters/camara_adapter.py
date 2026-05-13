import requests
from typing import Optional
from domain.entities.proposicao import Proposicao

class CamaraAdapter:
    """
    Adaptador para a API de Dados Abertos da Câmara dos Deputados.
    Documentação: https://dadosabertos.camara.leg.br/swagger/recursos.html
    """
    def __init__(self):
        self.base_url = "https://dadosabertos.camara.leg.br/api/v2"

    def buscar_por_id(self, id_proposicao: int) -> Optional[Proposicao]:
        url_proposicao = f"{self.base_url}/proposicoes/{id_proposicao}"
        url_autores = f"{url_proposicao}/autores"

        try:
            resp_prop = requests.get(url_proposicao, timeout=10)
            resp_prop.raise_for_status()
            dados = resp_prop.json()["dados"]

            resp_autores = requests.get(url_autores, timeout=10)
            resp_autores.raise_for_status()
            autores_dados = resp_autores.json()["dados"]

            # Processamento de autores
            nomes = [a["nome"] for a in autores_dados]
            autor_principal = nomes[0] if nomes else "Não informado"
            uf_autor = autores_dados[0].get("siglaUf", "N/A") if autores_dados else "N/A"

            status_info = dados.get("statusProposicao", {})
            
            # Normalização para a entidade Proposicao
            return Proposicao(
                id=str(id_proposicao),
                tipo=dados.get("siglaTipo", ""),
                numero=str(dados.get("numero", 0)),
                ano=dados.get("ano", 0),
                autor=autor_principal,
                uf_autor=uf_autor,
                orgao_origem="Câmara dos Deputados",
                status=status_info.get("despacho") or status_info.get("descricaoSituacao") or "Sem status",
                ementa=dados.get("ementa", "") or "Sem ementa",
                data_apresentacao=dados.get("dataApresentacao", ""),
                data_ultima_movimentacao=status_info.get("dataHora", ""),
                orgao_atual=status_info.get("siglaOrgao", "N/A"),
                link_oficial=f"https://www.camara.leg.br/proposicoesWeb/fichadetramitacao?idProposicao={id_proposicao}",
                tags=[]
            )

        except requests.exceptions.RequestException as e:
            # TODO: Implementar logging adequado
            print(f"Erro de rede ao buscar proposição {id_proposicao} na Câmara: {e}")
            return None
        except (KeyError, IndexError) as e:
            print(f"Erro ao processar dados da Câmara para ID {id_proposicao}: {e}")
            return None
