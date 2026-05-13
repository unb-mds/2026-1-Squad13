from typing import Dict, List
from infrastructure.repositories.sql_proposicao_repository import SQLProposicaoRepository

class DashboardService:
    """
    Serviço de Aplicação para calcular métricas e dados do dashboard.
    Centraliza a lógica de agregação que antes estava no frontend.
    """
    def __init__(self, repository: SQLProposicaoRepository):
        self.repository = repository

    def obter_metricas(self) -> Dict:
        # Busca todas as proposições para calcular métricas globais
        # Em um sistema real, usaríamos consultas SQL de agregação (COUNT, AVG)
        # para performance, mas para o MVP acadêmico, processar a lista é didático.
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
        aprovadas = [p for p in todas if p.status in ["Aprovada", "Sancionada"]]
        em_tramitacao = [p for p in todas if p.status in ["Em tramitação", "Em análise", "Aguardando votação"]]
        rejeitadas = [p for p in todas if p.status in ["Rejeitada", "Arquivada"]]
        com_atraso = [p for p in todas if p.atraso_critico]
        
        tempos = [p.tempo_total_dias for p in todas if p.tempo_total_dias is not None]
        tempo_medio = sum(tempos) / len(tempos) if tempos else 0

        # Lógica simplificada para "comissão mais lenta" baseada no orgao_atual
        # Agrupamos por órgão e calculamos a média de tempo
        orgaos: Dict[str, List[int]] = {}
        for p in todas:
            if p.orgao_atual and p.tempo_total_dias:
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
