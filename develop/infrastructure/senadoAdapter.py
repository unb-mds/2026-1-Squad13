import requests
from domain.entidades import LeiNormalizada

class SenadoAdapter:
    def __init__(self):
        self.urlApi = "https://legis.senado.leg.br/dadosabertos"

    def buscarLeiPorID(self, idProcesso):
        url = f"{self.urlApi}/processo/{idProcesso}?v=1"
        headers = {"Accept": "application/json"}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            dadosIdProcesso = response.json()
            if not dadosIdProcesso or 'id' not in dadosIdProcesso:
                return None

            tituloFormatado = dadosIdProcesso.get("identificacao")

            autoria = dadosIdProcesso.get("autoriaIniciativa", [])
            nomes = [autor.get('autor', 'Desconhecido') for autor in autoria]
            autoresFormatados = ", ".join(nomes) if nomes else "Autor não informado"

            dadosDocumento = dadosIdProcesso.get("documento", {})
            ementa = dadosDocumento.get("ementa", "Sem ementa")
            dataApresentacao = dadosDocumento.get("dataApresentacao")

            statusAtual = "Sem status"
            autuacoes = dadosIdProcesso.get('autuacoes', [])
            if autuacoes:
                situacoes = autuacoes[0].get('situacoes', [])
                if situacoes:
                    statusAtual = situacoes[-1].get('descricao', 'Sem status')
            
            return LeiNormalizada(
                idOrigem=idProcesso,
                titulo=tituloFormatado,
                autores=autoresFormatados,
                status=statusAtual,
                ementa=ementa,
                dataApresentacao=dataApresentacao,
                casaOrigem="Senado Federal"
            )

        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar a API do Senado: {e}")
            return None

