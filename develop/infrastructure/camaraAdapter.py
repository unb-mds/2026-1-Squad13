import requests
import datetime
from domain.entidades import LeiNormalizada

class CamaraAdapter:
    def __init__(self):
            self.urlApi = "https://dadosabertos.camara.leg.br/api/v2"
    
    def buscarLeiPorID(self, idProposicao):

        urlIdProposicao = f"{self.urlApi}/proposicoes/{idProposicao}"
        urlAutores = f"{urlIdProposicao}/autores"

        try:
            
            responseIdProposicao = requests.get(urlIdProposicao)
            responseIdProposicao.raise_for_status()
            responseAutores = requests.get(urlAutores)
            responseAutores.raise_for_status()
            
            dadosIdProposicao = responseIdProposicao.json()["dados"]
            dadosAutores = responseAutores.json()["dados"]

            sigla = dadosIdProposicao.get("siglaTipo")
            numero = dadosIdProposicao.get("numero")
            ano = dadosIdProposicao.get("ano")
            tituloFormatado = f"{sigla} {numero}/{ano}"

            nomes = []
            for autor in dadosAutores:
                nomes.append(autor["nome"])
            autoresFormatados = ", ".join(nomes)

            status = dadosIdProposicao.get("statusProposicao", {})
            statusAtual = status.get("despacho", "Sem movimentação registrada")

            ementaProposicao = dadosIdProposicao.get("ementa")

            dataApresentacao = dadosIdProposicao.get("dataApresentacao")

            return LeiNormalizada(
                idOrigem=idProposicao,
                titulo=tituloFormatado,
                autores=autoresFormatados,
                status=statusAtual,
                ementa=ementaProposicao,
                dataApresentacao=dataApresentacao,
                casaOrigem="Câmara dos Deputados"
            )
        except requests.exceptions.RequestException as e:
                print(f"Erro ao acessar a API da Câmara: {e}")
                return None