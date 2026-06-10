from typing import Protocol


class DashboardRepositoryPort(Protocol):
    """
    Interface (Port) para o repositório de Métricas do Dashboard.
    """

    def obter_metricas_gerais(self, filtros: dict | None) -> dict:
        """Obtém métricas gerais agregadas para o dashboard."""
        ...

    def obter_dados_tipo(self, filtros: dict | None) -> list[dict]:
        """Obtém dados de tramitação agrupados por tipo de proposição."""
        ...

    def obter_dados_comissao(self, filtros: dict | None) -> list[dict]:
        """Obtém contagem e tempo médio de proposições por órgão atual (comissão)."""
        ...

    def obter_dados_status(self, filtros: dict | None) -> list[dict]:
        """Obtém dados de proposições agrupados por status de tramitação."""
        ...

    def obter_gargalos(self, filtros: dict | None) -> list[dict]:
        """Identifica órgãos (comissões) com maior tempo médio de retenção de matérias."""
        ...

    def obter_proposicoes_para_temas(self, filtros: dict | None) -> list[dict]:
        """Busca proposições para compor a comparação de temas/tags."""
        ...

    def obter_evolucao_temporal(self, filtros: dict | None) -> list[dict]:
        """Calcula a evolução temporal das proposições."""
        ...

    def obter_transicoes_casas(self, filtros: dict | None) -> dict:
        """Calcula a contagem de transições de proposições entre a Câmara e o Senado."""
        ...

    def obter_estoque_fases(self, filtros: dict | None) -> list[dict]:
        """Obtém contagem de proposições ativas por fase analítica atual."""
        ...

    def obter_mediana_handoff(self, filtros: dict | None) -> dict:
        """Calcula métricas de handoff/trâmite entre casas."""
        ...

    def obter_tempo_por_fase(self, filtros: dict | None) -> list[dict]:
        """Calcula mediana de tempo de permanência por fase analítica."""
        ...

    def obter_qualidade_base(self, filtros: dict | None) -> dict:
        """Calcula a completude geral e qualidade da base local."""
        ...

