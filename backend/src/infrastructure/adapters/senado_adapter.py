import requests
from typing import Optional, List
from domain.entities.proposicao import Proposicao
from domain.entities.tramitacao import Tramitacao

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
        Tenta primeiro o endpoint de matéria (legado mas compatível com idMateria)
        e depois o de processo se necessário.
        """
        # A API de matéria é tecnicamente legada mas é a que aceita o CodigoMateria diretamente.
        url = f"{self.base_url}/materia/{id_materia}"
        headers = {"Accept": "application/json"}

        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 404:
                # Se não encontrou em materia/, tenta em processo/ (pode ser um idProcesso)
                url = f"{self.base_url}/processo/{id_materia}?v=1"
                resp = requests.get(url, headers=headers, timeout=10)
            
            resp.raise_for_status()
            dados_brutos = resp.json()
            
            # Normaliza a estrutura: a API de matéria vem aninhada em DetalheMateria/Materia,
            # a de processo vem flat no topo.
            if "DetalheMateria" in dados_brutos and "Materia" in dados_brutos["DetalheMateria"]:
                dados = dados_brutos["DetalheMateria"]["Materia"]
                identificacao_obj = dados.get("IdentificacaoMateria", {})
                identificacao = identificacao_obj.get("DescricaoIdentificacaoMateria", "")
                
                # Se tiver IdentificacaoProcesso, chama a API de processo para dados mais ricos (status real)
                id_processo = identificacao_obj.get("IdentificacaoProcesso")
                if id_processo:
                    try:
                        resp_proc = requests.get(f"{self.base_url}/processo/{id_processo}?v=1", headers=headers, timeout=5)
                        if resp_proc.status_code == 200:
                            # Recorre à estrutura flat do processo
                            dados_proc = resp_proc.json()
                            return self._processar_dados_processo(dados_proc, str(id_materia))
                    except Exception:
                        pass # Fallback para o que já temos se falhar
                
                ementa = dados.get("DadosBasicosMateria", {}).get("EmentaMateria", "Sem ementa")
                data_apresentacao = dados.get("DadosBasicosMateria", {}).get("DataApresentacao", "")
                autor_nome = dados.get("DadosBasicosMateria", {}).get("Autor", "Não informado")
                # No DetalheMateria, a situação fica em SituacaoAtual
                situacao_atual_obj = dados.get("SituacaoAtual", {}).get("Autuacoes", {}).get("Autuacao", {})
                if isinstance(situacao_atual_obj, list): 
                    situacao_atual_obj = situacao_atual_obj[0] if situacao_atual_obj else {}
                situacao = situacao_atual_obj.get("Situacao", {})
                status_atual = situacao.get("DescricaoSituacao", "Sem status")
                data_ultima_movimentacao = situacao.get("DataSituacao", "")
            elif "DetalheMateria" in dados_brutos and "Materia" not in dados_brutos["DetalheMateria"]:
                # Pode ser um idProcesso passado para o endpoint de materia, 
                # ou simplesmente não encontrado. Tenta endpoint de processo.
                url_proc = f"{self.base_url}/processo/{id_materia}?v=1"
                resp_proc = requests.get(url_proc, headers=headers, timeout=10)
                if resp_proc.status_code == 200:
                    return self._processar_dados_processo(resp_proc.json(), str(id_materia))
                return None
            else:
                return self._processar_dados_processo(dados_brutos, str(id_materia))

            # Tenta extrair tipo, numero e ano do "PL 123/2023"
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

            # Fallback para data de apresentação se última movimentação estiver vazia
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
                tags=[]
            )

        except requests.exceptions.RequestException as e:
            print(f"Erro de rede ao buscar matéria {id_materia} no Senado: {e}")
            return None
        except Exception as e:
            print(f"Erro inesperado ao processar dados do Senado para ID {id_materia}: {e}")
            return None

    def listar_recentes(self, tipo: str, quantidade: int = 10) -> List[int]:
        """Busca uma lista de IDs das matérias mais recentes de um determinado tipo no Senado."""
        url = f"{self.base_url}/materia/pesquisa/lista"
        params = {
            "sigla": tipo,
            "sort": "desc"
        }
        headers = {"Accept": "application/json"}
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            resp.raise_for_status()
            dados = resp.json()
            
            materias = dados.get("ListaMaterias", {}).get("Materia", [])
            if not isinstance(materias, list):
                materias = [materias] if materias else []
                
            return [int(m["CodigoMateria"]) for m in materias[:quantidade]]
        except Exception as e:
            print(f"Erro ao listar matérias recentes no Senado: {e}")
            return []

    def buscar_tramitacoes(self, id_materia: int) -> List[Tramitacao]:
        """Busca as tramitações de uma proposição no Senado."""
        url = f"{self.base_url}/processo/{id_materia}?v=1"
        headers = {"Accept": "application/json"}
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            dados = resp.json()

            tramitacoes = []
            autuacoes = dados.get('autuacoes', [])
            seq = 1
            if autuacoes:
                situacoes = autuacoes[0].get('situacoes', [])
                for s in situacoes:
                    tramitacoes.append(Tramitacao(
                        proposicao_id=str(id_materia),
                        data_hora=s.get("inicio", ""),
                        sequencia=seq,
                        sigla_orgao="Senado",
                        descricao_tramitacao=s.get("descricao", ""),
                        status=s.get("descricao", "")
                    ))
                    seq += 1
            
            # Ordenar por data descendente para ser consistente com o padrão
            tramitacoes.sort(key=lambda x: x.data_hora, reverse=True)
            return tramitacoes
        except Exception as e:
            print(f"Erro ao buscar tramitações do Senado para ID {id_materia}: {e}")
            return []
    def _processar_dados_processo(self, dados: dict, id_materia: str) -> Proposicao:
        """Processa a estrutura flat retornada pelo endpoint /processo."""
        identificacao = dados.get("identificacao", "")
        ementa = dados.get("conteudo", {}).get("ementa") or dados.get("documento", {}).get("ementa", "Sem ementa")
        data_apresentacao = dados.get("documento", {}).get("dataApresentacao", "")
        autoria = dados.get("autoriaIniciativa", [])
        autor_nome = autoria[0].get("autor", "Não informado") if autoria else "Não informado"
        
        status_atual = "Sem status"
        data_ultima_movimentacao = ""
        autuacoes = dados.get('autuacoes', [])
        if autuacoes:
            # Pega a autuação que tem situação atual
            # Normalmente a primeira autuação é a principal
            situacoes = autuacoes[0].get('situacoes', [])
            if situacoes:
                # Pega a última situação que tenha data de início
                for s in reversed(situacoes):
                    if s.get('inicio'):
                        data_ultima_movimentacao = s['inicio']
                        status_atual = s.get('descricao', status_atual)
                        break

        # Tenta extrair tipo, numero e ano do "PL 123/2023"
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

        # Fallback para data de apresentação se última movimentação estiver vazia
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
            tags=[]
        )
