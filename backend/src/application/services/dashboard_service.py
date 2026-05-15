from typing import Dict, List
from infrastructure.repositories.sql_proposicao_repository import SQLProposicaoRepository

class DashboardService:
    """
    Serviço de Aplicação para calcular métricas e dados do dashboard.
    Centraliza a lógica de agregação que antes estava no frontend.
    """
    def __init__(self, repository: SQLProposicaoRepository):
        self.repository = repository

    def _agrupar_status(self, status_raw: str) -> str:
        status = status_raw.lower()
        
        # 1. Aprovadas / Concluídas positivamente
        if any(term in status for term in [
            "aprovad", "sancionad", "norma jurídica", "promulgad", 
            "transformad", "enviado à sanção", "ofício ao senado - sancionado"
        ]):
            return "Aprovada/Sancionada"
            
        # 2. Rejeitadas / Concluídas negativamente / Arquivadas
        if any(term in status for term in [
            "rejeitad", "arquivad", "retirad", "prejudicad", 
            "indiferid", "devolvida", "negado", "materia despachada"
        ]):
            return "Rejeitada/Arquivada"
            
        # 3. Em tramitação / Ativas
        if any(term in status for term in [
            "tramitação", "análise", "votação", "pauta", "apresentação", 
            "mesa", "relator", "parecer", "aguardando", "comissão", 
            "ofício", "recebimento", "leitura", "despacho", "relatório"
        ]) or status == "sem status":
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
                "comissaoMaiorTempoMedia": 0
            }

        total = len(todas)
        aprovadas = [p for p in todas if self._agrupar_status(p.status) == "Aprovada/Sancionada"]
        em_tramitacao = [p for p in todas if self._agrupar_status(p.status) == "Em tramitação"]
        rejeitadas = [p for p in todas if self._agrupar_status(p.status) == "Rejeitada/Arquivada"]
        com_atraso = [p for p in todas if p.atraso_critico]
        
        tempos = [p.tempo_total_dias for p in todas if p.tempo_total_dias is not None]
        tempo_medio = sum(tempos) / len(tempos) if tempos else 0

        # Agrupamento por órgão para identificar a comissão mais lenta
        orgaos: Dict[str, List[int]] = {}
        for p in todas:
            if p.orgao_atual and p.tempo_total_dias is not None:
                if p.orgao_atual not in orgaos:
                    orgaos[p.orgao_atual] = []
                orgaos[p.orgao_atual].append(p.tempo_total_dias)
        
        medias_orgaos = {org: sum(t)/len(t) for org, t in orgaos.items()}
        pior_orgao = max(medias_orgaos, key=medias_orgaos.get) if medias_orgaos else "N/A"
        pior_media = medias_orgaos.get(pior_orgao, 0)

        return {
            "tempoMedioTramitacao": int(tempo_medio),
            "totalProposicoes": total,
            "proposicoesComAtraso": len(com_atraso),
            "totalAprovadas": len(aprovadas),
            "totalEmTramitacao": len(em_tramitacao),
            "totalRejeitadas": len(rejeitadas),
            "comissaoMaiorTempo": pior_orgao,
            "comissaoMaiorTempoMedia": int(pior_media)
        }

    def obter_dados_tipo(self) -> List[Dict]:
        todas = self.repository.filtrar()
        tipos: Dict[str, Dict] = {}
        for p in todas:
            if p.tipo not in tipos:
                tipos[p.tipo] = {"tipo": p.tipo, "tempos": [], "quantidade": 0}
            tipos[p.tipo]["quantidade"] += 1
            if p.tempo_total_dias is not None:
                tipos[p.tipo]["tempos"].append(p.tempo_total_dias)
        
        resultado = []
        for info in tipos.values():
            tempo_medio = sum(info["tempos"]) / len(info["tempos"]) if info["tempos"] else 0
            resultado.append({
                "tipo": info["tipo"],
                "tempoMedio": int(tempo_medio),
                "quantidade": info["quantidade"]
            })
        return sorted(resultado, key=lambda x: x["quantidade"], reverse=True)

    def obter_dados_comissao(self) -> List[Dict]:
        todas = self.repository.filtrar()
        orgaos: Dict[str, Dict] = {}
        for p in todas:
            orgao = p.orgao_atual or "Desconhecido"
            if orgao not in orgaos:
                orgaos[orgao] = {"comissao": orgao, "tempos": [], "quantidade": 0}
            orgaos[orgao]["quantidade"] += 1
            if p.tempo_total_dias is not None:
                orgaos[orgao]["tempos"].append(p.tempo_total_dias)
        
        resultado = []
        for info in orgaos.values():
            tempo_medio = sum(info["tempos"]) / len(info["tempos"]) if info["tempos"] else 0
            resultado.append({
                "comissao": info["comissao"],
                "tempoMedio": int(tempo_medio),
                "quantidade": info["quantidade"]
            })
        return sorted(resultado, key=lambda x: x["tempoMedio"], reverse=True)[:10]

    def obter_dados_status(self) -> List[Dict]:
        todas = self.repository.filtrar()
        if not todas:
            return []
        
        total = len(todas)
        contagem: Dict[str, int] = {}
        for p in todas:
            status_agrupado = self._agrupar_status(p.status)
            contagem[status_agrupado] = contagem.get(status_agrupado, 0) + 1
            
        resultado = [
            {
                "status": status,
                "quantidade": qtd,
                "percentual": round((qtd / total) * 100)
            }
            for status, qtd in contagem.items()
        ]
        return sorted(resultado, key=lambda x: x["quantidade"], reverse=True)

    def obter_gargalos(self) -> List[Dict]:
        todas = self.repository.filtrar()
        orgaos: Dict[str, Dict] = {}
        for p in todas:
            orgao = p.orgao_atual or "Desconhecido"
            if orgao not in orgaos:
                orgaos[orgao] = {"orgao": orgao, "tempos": [], "proposicoes": 0, "atrasos": 0}
            
            orgaos[orgao]["proposicoes"] += 1
            if p.atraso_critico:
                orgaos[orgao]["atrasos"] += 1
            if p.tempo_total_dias is not None:
                orgaos[orgao]["tempos"].append(p.tempo_total_dias)
        
        resultado = []
        for info in orgaos.values():
            # Converte dias para meses (média de 30 dias)
            tempo_medio_meses = (sum(info["tempos"]) / len(info["tempos"]) / 30) if info["tempos"] else 0
            taxa_atraso = (info["atrasos"] / info["proposicoes"] * 100) if info["proposicoes"] else 0
            
            resultado.append({
                "orgao": info["orgao"],
                "tempoMedioMeses": round(tempo_medio_meses, 1),
                "quantidadeProposicoes": info["proposicoes"],
                "taxaAtraso": round(taxa_atraso)
            })
        
        return sorted(resultado, key=lambda x: x["taxaAtraso"], reverse=True)

    def obter_comparacao_temas(self) -> List[Dict]:
        todas = self.repository.filtrar()
        temas: Dict[str, Dict] = {}
        
        for p in todas:
            if not p.tags:
                continue
                
            for tag in p.tags:
                tag_formatada = tag.capitalize()
                if tag_formatada not in temas:
                    temas[tag_formatada] = {
                        "tema": tag_formatada,
                        "tempos": [],
                        "total": 0,
                        "aprovadas": 0
                    }
                
                temas[tag_formatada]["total"] += 1
                if p.tempo_total_dias is not None:
                    temas[tag_formatada]["tempos"].append(p.tempo_total_dias)
                
                if self._agrupar_status(p.status) == "Aprovada/Sancionada":
                    temas[tag_formatada]["aprovadas"] += 1
        
        resultado = []
        for info in temas.values():
            tempo_medio = sum(info["tempos"]) / len(info["tempos"]) if info["tempos"] else 0
            taxa_aprovacao = (info["aprovadas"] / info["total"] * 100) if info["total"] else 0
            
            velocidade = "medio"
            if tempo_medio < 300:
                velocidade = "rapido"
            elif tempo_medio > 600:
                velocidade = "lento"
                
            resultado.append({
                "tema": info["tema"],
                "tempoMedioDias": int(tempo_medio),
                "taxaAprovacao": round(taxa_aprovacao),
                "velocidade": velocidade
            })
            
        return sorted(resultado, key=lambda x: x["tempoMedioDias"])
