"""
Serviço de aplicação para listar as movimentações (eventos) de uma proposição.

Substitui o antigo ListarTramitacoesService. Orquestra a busca no banco (cache),
fallback para a API externa via adapter, e normalização de tramitações.
"""

from typing import List

from application.services.normalizar_tramitacao_service import (
    NormalizarTramitacaoService,
)
from domain.entities.evento_tramitacao import EventoTramitacao
from domain.entities.orgao_legislativo import CasaLegislativa
from infrastructure.adapters.camara_adapter import CamaraAdapter
from infrastructure.adapters.senado_adapter import SenadoAdapter
from infrastructure.repositories.sql_evento_tramitacao_repository import (
    SQLEventoTramitacaoRepository,
)
from infrastructure.repositories.sql_fase_analitica_repository import (
    SQLFaseAnaliticaRepository,
)
from infrastructure.repositories.sql_orgao_legislativo_repository import (
    SQLOrgaoLegislativoRepository,
)
from infrastructure.repositories.sql_proposicao_repository import (
    SQLProposicaoRepository,
)


class ListarMovimentacoesService:
    """Busca eventos normalizados, consultando adapters e cache."""

    def __init__(
        self,
        evento_repo: SQLEventoTramitacaoRepository,
        proposicao_repo: SQLProposicaoRepository,
        fase_repo: SQLFaseAnaliticaRepository,
        orgao_repo: SQLOrgaoLegislativoRepository,
        camara_adapter: CamaraAdapter,
        senado_adapter: SenadoAdapter,
    ):
        self.evento_repo = evento_repo
        self.proposicao_repo = proposicao_repo
        self.fase_repo = fase_repo
        self.orgao_repo = orgao_repo
        self.camara_adapter = camara_adapter
        self.senado_adapter = senado_adapter

    def executar(self, proposicao_id: str) -> List[EventoTramitacao]:
        """
        Retorna a lista de eventos normalizados para a proposição solicitada.
        Se não existirem no cache, busca na API, normaliza e salva.
        """
        # 0. Resolução de slug se necessário (PL-1-2024)
        real_id = proposicao_id
        if "-" in proposicao_id:
            partes = proposicao_id.split("-")
            if len(partes) == 3:
                tipo, numero, ano_str = partes
                try:
                    ano = int(ano_str)
                    p = self.proposicao_repo.buscar_por_codigo(tipo, numero, ano)
                    if p:
                        real_id = str(p.id)
                except ValueError:
                    pass

        # 1. Tentar cache (banco de dados)
        eventos = self.evento_repo.buscar_por_proposicao(real_id)
        if eventos:
            return eventos

        # 2. Se não está no cache, precisa saber a origem
        proposicao = self.proposicao_repo.buscar_por_id(real_id)
        
        # Determina o adapter e a casa padrão com base na proposição ou tenta fallback
        dados_brutos = []
        casa_padrao = CasaLegislativa.CAMARA

        if not proposicao:
            # Fallback numérico
            if not real_id.isdigit():
                return []

            dados_brutos = self.camara_adapter.buscar_tramitacoes_brutas(int(real_id))
            if not dados_brutos:
                dados_brutos = self.senado_adapter.buscar_tramitacoes_brutas(int(real_id))
                casa_padrao = CasaLegislativa.SENADO
        else:
            if "Câmara" in (proposicao.orgao_origem or ""):
                dados_brutos = self.camara_adapter.buscar_tramitacoes_brutas(int(real_id))
                casa_padrao = CasaLegislativa.CAMARA
            else:
                dados_brutos = self.senado_adapter.buscar_tramitacoes_brutas(int(real_id))
                casa_padrao = CasaLegislativa.SENADO

        if not dados_brutos:
            return []

        # 3. Normalizar
        normalizer = NormalizarTramitacaoService(
            fase_repo=self.fase_repo,
            orgao_repo=self.orgao_repo,
            casa_padrao=casa_padrao,
        )
        eventos_novos = normalizer.normalizar(real_id, dados_brutos)

        # 4. Salvar no cache
        if eventos_novos:
            self.evento_repo.salvar_lote(eventos_novos)

        return eventos_novos
