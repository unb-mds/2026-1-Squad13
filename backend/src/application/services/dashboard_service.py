from typing import Dict, List
from datetime import datetime, date

from infrastructure.repositories.sql_proposicao_repository import (
    SQLProposicaoRepository,
)
from infrastructure.repositories.sql_evento_tramitacao_repository import (
    SQLEventoTramitacaoRepository,
)
from domain.entities.evento_tramitacao import EventoTramitacao
from domain.entities.tipo_evento import TipoEvento


class DashboardService:
    """
    Serviço de Aplicação para calcular métricas e dados do dashboard.
    Centraliza a lógica de agregação que antes estava no frontend.
    """

    def __init__(
        self,
        repository: SQLProposicaoRepository,
        evento_repo: SQLEventoTramitacaoRepository,
    ):
        self.repository = repository
        self.evento_repo = evento_repo

    def _calcular_tempo_total(
        self, eventos: List[EventoTramitacao], fallback_tempo: int
    ) -> int:
        if not eventos:
            return fallback_tempo

        # Encontrar o primeiro evento de APRESENTACAO
        primeiro_evento = None
        for e in eventos:
            if e.tipo_evento == TipoEvento.APRESENTACAO.value:
                primeiro_evento = e
                break

        if not primeiro_evento:
            primeiro_evento = eventos[0]

        # Encontrar último evento terminal (se houver)
        ultimo_evento_terminal = None
        terminais = {
            TipoEvento.APROVACAO.value,
            TipoEvento.REJEICAO.value,
            TipoEvento.ARQUIVAMENTO.value,
            TipoEvento.PREJUDICIALIDADE.value,
            TipoEvento.SANCAO_OU_VETO.value,
            TipoEvento.PROMULGACAO.value,
        }

        for e in reversed(eventos):
            if e.tipo_evento in terminais:
                ultimo_evento_terminal = e
                break

        try:
            inicio = datetime.fromisoformat(
                primeiro_evento.data_evento.replace("Z", "+00:00")
            ).date()
            if ultimo_evento_terminal:
                fim = datetime.fromisoformat(
                    ultimo_evento_terminal.data_evento.replace("Z", "+00:00")
                ).date()
            else:
                fim = date.today()
            return (fim - inicio).days
        except (ValueError, AttributeError):
            return fallback_tempo

    def _extrair_status_atual(
        self, eventos: List[EventoTramitacao], fallback_status: str
    ) -> str:
        if not eventos:
            return fallback_status

        # Mapeamento simples para display
        mapa_status = {
            TipoEvento.APRESENTACAO.value: "Apresentada",
            TipoEvento.DESPACHO.value: "Em Tramitação",
            TipoEvento.RECEBIMENTO_ORGAO.value: "Em Tramitação",
            TipoEvento.DESIGNACAO_RELATOR.value: "Em Relatoria",
            TipoEvento.PARECER.value: "Parecer emitido",
            TipoEvento.INCLUSAO_PAUTA.value: "Em Pauta",
            TipoEvento.VOTACAO_COMISSAO.value: "Em Votação",
            TipoEvento.VOTACAO_PLENARIO.value: "Em Votação",
            TipoEvento.APROVACAO.value: "Aprovada",
            TipoEvento.REJEICAO.value: "Rejeitada",
            TipoEvento.REMESSA_OUTRA_CASA.value: "Enviada à outra Casa",
            TipoEvento.ARQUIVAMENTO.value: "Arquivada",
            TipoEvento.SANCAO_OU_VETO.value: "Sancionada/Vetada",
            TipoEvento.PROMULGACAO.value: "Promulgada",
        }

        # Procura retroativamente o primeiro status com mapeamento caso o último seja NAO_CLASSIFICADO
        for e in reversed(eventos):
            if e.tipo_evento in mapa_status:
                return mapa_status[e.tipo_evento]

        return fallback_status

    def _obter_dados_em_lote(self, proposicoes) -> List[dict]:
        if not proposicoes:
            return []

        ids = [str(p.id) for p in proposicoes]
        mapa_eventos = self.evento_repo.buscar_por_multiplas_proposicoes(ids)

        dados = []
        for p in proposicoes:
            eventos = mapa_eventos.get(str(p.id), [])
            tempo = self._calcular_tempo_total(eventos, p.tempo_total_dias or 0)
            status = self._extrair_status_atual(eventos, p.status)
            atraso_critico = tempo > 180

            dados.append(
                {
                    "prop": p,
                    "tempo_total_dias": tempo,
                    "status": status,
                    "atraso_critico": atraso_critico,
                    "orgao_atual": p.orgao_atual,
                    "tipo": p.tipo,
                    "tags": p.tags,
                }
            )
        return dados

    def _agrupar_status(self, status_raw: str) -> str:
        status = status_raw.lower()

        # 1. Aprovadas / Concluídas positivamente
        if any(
            term in status
            for term in [
                "aprovad",
                "sancionad",
                "norma jurídica",
                "promulgad",
                "transformad",
                "enviado à sanção",
                "ofício ao senado - sancionado",
            ]
        ):
            return "Aprovada/Sancionada"

        # 2. Rejeitadas / Concluídas negativamente / Arquivadas
        if any(
            term in status
            for term in [
                "rejeitad",
                "arquivad",
                "retirad",
                "prejudicad",
                "indiferid",
                "devolvida",
                "negado",
                "materia despachada",
            ]
        ):
            return "Rejeitada/Arquivada"

        # 3. Em tramitação / Ativas
        if (
            any(
                term in status
                for term in [
                    "tramitação",
                    "análise",
                    "votação",
                    "pauta",
                    "apresentação",
                    "mesa",
                    "relator",
                    "parecer",
                    "aguardando",
                    "comissão",
                    "ofício",
                    "recebimento",
                    "leitura",
                    "despacho",
                    "relatório",
                ]
            )
            or status == "sem status"
        ):
            return "Em tramitação"

        return "Outros"

    def obter_metricas(self) -> Dict:
        todas = self.repository.filtrar()

        if not todas:
            return {
                "tempoMedioTramitacao": 0,
                "totalProposicoes": 0,
                "proposicoesComAtraso": 0,
                "totalAprovadas": 0,
                "totalEmTramitacao": 0,
                "totalRejeitadas": 0,
                "comissaoMaiorTempo": "N/A",
                "comissaoMaiorTempoMedia": 0,
            }

        dados = self._obter_dados_em_lote(todas)

        total = len(dados)
        aprovadas = [
            d
            for d in dados
            if self._agrupar_status(d["status"]) == "Aprovada/Sancionada"
        ]
        em_tramitacao = [
            d for d in dados if self._agrupar_status(d["status"]) == "Em tramitação"
        ]
        rejeitadas = [
            d
            for d in dados
            if self._agrupar_status(d["status"]) == "Rejeitada/Arquivada"
        ]
        com_atraso = [d for d in dados if d["atraso_critico"]]

        tempos = [
            d["tempo_total_dias"] for d in dados if d["tempo_total_dias"] is not None
        ]
        tempo_medio = sum(tempos) / len(tempos) if tempos else 0

        # Agrupamento por órgão para identificar a comissão mais lenta
        orgaos: Dict[str, List[int]] = {}
        for d in dados:
            if d["orgao_atual"] and d["tempo_total_dias"] is not None:
                if d["orgao_atual"] not in orgaos:
                    orgaos[d["orgao_atual"]] = []
                orgaos[d["orgao_atual"]].append(d["tempo_total_dias"])

        medias_orgaos = {org: sum(t) / len(t) for org, t in orgaos.items()}
        pior_orgao = (
            max(medias_orgaos, key=medias_orgaos.get) if medias_orgaos else "N/A"
        )
        pior_media = medias_orgaos.get(pior_orgao, 0)

        return {
            "tempoMedioTramitacao": int(tempo_medio),
            "totalProposicoes": total,
            "proposicoesComAtraso": len(com_atraso),
            "totalAprovadas": len(aprovadas),
            "totalEmTramitacao": len(em_tramitacao),
            "totalRejeitadas": len(rejeitadas),
            "comissaoMaiorTempo": pior_orgao,
            "comissaoMaiorTempoMedia": int(pior_media),
        }

    def obter_dados_tipo(self) -> List[Dict]:
        todas = self.repository.filtrar()
        dados = self._obter_dados_em_lote(todas)

        tipos: Dict[str, Dict] = {}
        for d in dados:
            if d["tipo"] not in tipos:
                tipos[d["tipo"]] = {"tipo": d["tipo"], "tempos": [], "quantidade": 0}
            tipos[d["tipo"]]["quantidade"] += 1
            if d["tempo_total_dias"] is not None:
                tipos[d["tipo"]]["tempos"].append(d["tempo_total_dias"])

        resultado = []
        for info in tipos.values():
            tempo_medio = (
                sum(info["tempos"]) / len(info["tempos"]) if info["tempos"] else 0
            )
            resultado.append(
                {
                    "tipo": info["tipo"],
                    "tempoMedio": int(tempo_medio),
                    "quantidade": info["quantidade"],
                }
            )
        return sorted(resultado, key=lambda x: x["quantidade"], reverse=True)

    def obter_dados_comissao(self) -> List[Dict]:
        todas = self.repository.filtrar()
        dados = self._obter_dados_em_lote(todas)

        orgaos: Dict[str, Dict] = {}
        for d in dados:
            orgao = d["orgao_atual"] or "Desconhecido"
            if orgao not in orgaos:
                orgaos[orgao] = {"comissao": orgao, "tempos": [], "quantidade": 0}
            orgaos[orgao]["quantidade"] += 1
            if d["tempo_total_dias"] is not None:
                orgaos[orgao]["tempos"].append(d["tempo_total_dias"])

        resultado = []
        for info in orgaos.values():
            tempo_medio = (
                sum(info["tempos"]) / len(info["tempos"]) if info["tempos"] else 0
            )
            resultado.append(
                {
                    "comissao": info["comissao"],
                    "tempoMedio": int(tempo_medio),
                    "quantidade": info["quantidade"],
                }
            )
        return sorted(resultado, key=lambda x: x["tempoMedio"], reverse=True)[:10]

    def obter_dados_status(self) -> List[Dict]:
        todas = self.repository.filtrar()
        if not todas:
            return []

        dados = self._obter_dados_em_lote(todas)
        total = len(dados)
        contagem: Dict[str, int] = {}
        for d in dados:
            status_agrupado = self._agrupar_status(d["status"])
            contagem[status_agrupado] = contagem.get(status_agrupado, 0) + 1

        resultado = [
            {
                "status": status,
                "quantidade": qtd,
                "percentual": round((qtd / total) * 100),
            }
            for status, qtd in contagem.items()
        ]
        return sorted(resultado, key=lambda x: x["quantidade"], reverse=True)

    def obter_gargalos(self) -> List[Dict]:
        todas = self.repository.filtrar()
        dados = self._obter_dados_em_lote(todas)

        orgaos: Dict[str, Dict] = {}
        for d in dados:
            orgao = d["orgao_atual"] or "Desconhecido"
            if orgao not in orgaos:
                orgaos[orgao] = {
                    "orgao": orgao,
                    "tempos": [],
                    "proposicoes": 0,
                    "atrasos": 0,
                }

            orgaos[orgao]["proposicoes"] += 1
            if d["atraso_critico"]:
                orgaos[orgao]["atrasos"] += 1
            if d["tempo_total_dias"] is not None:
                orgaos[orgao]["tempos"].append(d["tempo_total_dias"])

        resultado = []
        for info in orgaos.values():
            # Converte dias para meses (média de 30 dias)
            tempo_medio_meses = (
                (sum(info["tempos"]) / len(info["tempos"]) / 30)
                if info["tempos"]
                else 0
            )
            taxa_atraso = (
                (info["atrasos"] / info["proposicoes"] * 100)
                if info["proposicoes"]
                else 0
            )

            resultado.append(
                {
                    "orgao": info["orgao"],
                    "tempoMedioMeses": round(tempo_medio_meses, 1),
                    "quantidadeProposicoes": info["proposicoes"],
                    "taxaAtraso": round(taxa_atraso),
                }
            )

        return sorted(resultado, key=lambda x: x["taxaAtraso"], reverse=True)

    def obter_comparacao_temas(self) -> List[Dict]:
        todas = self.repository.filtrar()
        dados = self._obter_dados_em_lote(todas)

        temas: Dict[str, Dict] = {}

        for d in dados:
            if not d["tags"]:
                continue

            for tag in d["tags"]:
                tag_formatada = tag.capitalize()
                if tag_formatada not in temas:
                    temas[tag_formatada] = {
                        "tema": tag_formatada,
                        "tempos": [],
                        "total": 0,
                        "aprovadas": 0,
                    }

                temas[tag_formatada]["total"] += 1
                if d["tempo_total_dias"] is not None:
                    temas[tag_formatada]["tempos"].append(d["tempo_total_dias"])

                if self._agrupar_status(d["status"]) == "Aprovada/Sancionada":
                    temas[tag_formatada]["aprovadas"] += 1

        resultado = []
        for info in temas.values():
            tempo_medio = (
                sum(info["tempos"]) / len(info["tempos"]) if info["tempos"] else 0
            )
            taxa_aprovacao = (
                (info["aprovadas"] / info["total"] * 100) if info["total"] else 0
            )

            velocidade = "medio"
            if tempo_medio < 300:
                velocidade = "rapido"
            elif tempo_medio > 600:
                velocidade = "lento"

            resultado.append(
                {
                    "tema": info["tema"],
                    "tempoMedioDias": int(tempo_medio),
                    "taxaAprovacao": round(taxa_aprovacao),
                    "velocidade": velocidade,
                }
            )

        return sorted(resultado, key=lambda x: x["tempoMedioDias"])
