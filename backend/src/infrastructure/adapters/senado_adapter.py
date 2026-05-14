import requests
from typing import Optional
from domain.entities.proposicao import Proposicao

class SenadoAdapter:
    """
    Adaptador para a API de Dados Abertos do Senado Federal.
    Documentação: https://legis.senado.leg.br/dadosabertos/docs/
    """
    def __init__(self):
        self.base_url = "https://legis.senado.leg.br/dadosabertos"

    def buscar_por_id(self, id_materia: int) -> Optional[Proposicao]:
        """
        Busca detalhes de uma matéria legislativa no Senado.
        """
        url = f"{self.base_url}/processo/{id_materia}?v=1"
        headers = {"Accept": "application/json"}

        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            dados = resp.json()
            
            # O Senado pode retornar erro dentro do JSON com status 200 em alguns casos,
            # mas o código original não tratava isso. Vamos manter simples.
            
            identificacao = dados.get("identificacao", "")
            # Tenta extrair tipo, numero e ano do "PL 123/2023"
            tipo = ""
            numero = 0
            ano = 0
            if identificacao and " " in identificacao:
                tipo, resto = identificacao.split(" ", 1)
                if "/" in resto:
                    num_str, ano_str = resto.split("/", 1)
                    numero = int(num_str) if num_str.isdigit() else 0
                    ano = int(ano_str) if ano_str.isdigit() else 0

            autoria = dados.get("autoriaIniciativa", [])
            autor_nome = "Não informado"
            if autoria:
                autor_nome = autoria[0].get("autor", "Não informado")
            
            doc = dados.get("documento", {})
            ementa = doc.get("ementa", "Sem ementa")
            data_apresentacao = doc.get("dataApresentacao", "")

            # Extração de status e data da última movimentação via autuações
            status_atual = "Sem status"
            data_ultima_movimentacao = ""
            
            autuacoes = dados.get('autuacoes', [])
            if autuacoes:
                situacoes = autuacoes[0].get('situacoes', [])
                if situacoes:
                    ultima_situacao = situacoes[-1]
                    status_atual = ultima_situacao.get('descricao', 'Sem status')
                    data_ultima_movimentacao = ultima_situacao.get('inicio', "")

            # Fallback para data de apresentação se última movimentação estiver vazia
            if not data_ultima_movimentacao:
                data_ultima_movimentacao = data_apresentacao
            
            return Proposicao(
                id=str(id_materia),
                tipo=tipo,
                numero=str(numero),
                ano=ano,
                autor=autor_nome,
                uf_autor="N/A", # API de processo não detalha UF do autor diretamente
                orgao_origem="Senado Federal",
                status=status_atual,
                ementa=ementa,
                data_apresentacao=data_apresentacao,
                data_ultima_movimentacao=data_ultima_movimentacao,
                orgao_atual="Senado Federal",
                link_oficial=f"https://wwws.senado.leg.br/ecidadania/visualizacaomateria?id={id_materia}",
                tags=[]
            )

        except requests.exceptions.RequestException as e:
            print(f"Erro de rede ao buscar matéria {id_materia} no Senado: {e}")
            return None
        except Exception as e:
            print(f"Erro inesperado ao processar dados do Senado para ID {id_materia}: {e}")
            return None
