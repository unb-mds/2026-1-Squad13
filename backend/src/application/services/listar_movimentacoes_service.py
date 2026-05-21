"""
Serviço de aplicação para listar as movimentações (eventos) de uma proposição.

Substitui o antigo ListarTramitacoesService. Orquestra a busca no banco (cache),
fallback para a API externa via adapter, e normalização de tramitações.
"""

import logging
from typing import Any, List, Optional, Union
import httpx

from application.services.normalizar_tramitacao_service import (
    NormalizarTramitacaoService,
)
from application.services.agregar_por_fase_service import AgregarPorFaseService
from domain.entities.evento_tramitacao import EventoTramitacao
from domain.entities.orgao_legislativo import CasaLegislativa
from domain.value_objects.periodo_fase import PeriodoFase
from domain.value_objects.modo_movimentacao import ModoMovimentacao
from infrastructure.adapters.camara_adapter import CamaraAdapter
from infrastructure.adapters.senado_adapter import SenadoAdapter
from infrastructure.repositories.sql_apensamento_repository import (
    SQLApensamentoRepository,
)
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

logger = logging.getLogger(__name__)


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
        apensamento_repo: Optional[SQLApensamentoRepository] = None,
    ):
        self.evento_repo = evento_repo
        self.proposicao_repo = proposicao_repo
        self.fase_repo = fase_repo
        self.orgao_repo = orgao_repo
        self.camara_adapter = camara_adapter
        self.senado_adapter = senado_adapter
        self.apensamento_repo = apensamento_repo
        self._agregar_service = AgregarPorFaseService(fase_repo)

    async def executar(
        self,
        proposicao_id: str,
        modo: ModoMovimentacao = ModoMovimentacao.RESUMIDO,
        client: Optional[httpx.AsyncClient] = None,
    ) -> Union[List[PeriodoFase], List[EventoTramitacao]]:
        """
        Retorna a lista de eventos normalizados para a proposição solicitada.
        Se não existirem no cache, busca na API, normaliza e salva.
        """
        proposicao = None
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

        # 2. Se não está no cache, busca na API (Fail-fast de 5s para o usuário)
        if not eventos:
            proposicao = self.proposicao_repo.buscar_por_id(real_id)

            # Timeout curto para a Web (5s), mas permite maior se for via client (Seed)
            req_timeout = 5 if client is None else 30

            # Determina o adapter e a casa padrão
            dados_brutos = []

            # Se for PL ou PEC, tentamos buscar em AMBAS as casas para unificar o histórico
            tipos_unificaveis = {"PL", "PEC", "PLP", "MPV"}

            tipo_prop = proposicao.tipo if proposicao else None
            numero_prop = proposicao.numero if proposicao else None
            ano_prop = proposicao.ano if proposicao else None

            if not proposicao and real_id.isdigit():
                # Tenta descobrir o tipo se não tiver proposicao (fallback para IDs diretos)
                # Neste caso mantemos a lógica sequencial original
                dados_brutos = await self.camara_adapter.buscar_tramitacoes_brutas(
                    int(real_id), client=client
                )
                casa_padrao = CasaLegislativa.CAMARA
                if not dados_brutos:
                    dados_brutos = await self.senado_adapter.buscar_tramitacoes_brutas(
                        int(real_id), client=client, timeout=req_timeout
                    )
                    casa_padrao = CasaLegislativa.SENADO
            elif proposicao and tipo_prop in tipos_unificaveis:
                # LÓGICA DE UNIFICAÇÃO (CROSSOVER)
                logger.info(
                    f"Iniciando busca unificada para {proposicao.nome_canonico}"
                )

                # 1. Buscar IDs em ambas as casas
                id_camara = None
                id_senado = None

                if "Câmara" in (proposicao.orgao_origem or ""):
                    id_camara = int(proposicao.id)
                    # Tenta achar o correspondente no Senado
                    id_senado = await self.senado_adapter.buscar_id_por_identificacao(
                        tipo_prop, numero_prop, ano_prop, client=client
                    )
                else:
                    id_senado = int(proposicao.id)
                    # Tenta achar o correspondente na Câmara
                    id_camara = await self.camara_adapter.buscar_id_por_identificacao(
                        tipo_prop, numero_prop, ano_prop, client=client
                    )

                # 2. Coletar tramitações de onde encontramos ID
                tramitacoes_camara = []
                tramitacoes_senado = []

                if id_camara:
                    tramitacoes_camara = (
                        await self.camara_adapter.buscar_tramitacoes_brutas(
                            id_camara, client=client
                        )
                    )
                if id_senado:
                    tramitacoes_senado = (
                        await self.senado_adapter.buscar_tramitacoes_brutas(
                            id_senado, client=client, timeout=req_timeout
                        )
                    )

                # 3. Normalizar separadamente (pois cada uma tem sua casa_padrao)
                eventos_unificados = []

                if tramitacoes_camara:
                    norm_c = NormalizarTramitacaoService(
                        self.fase_repo,
                        self.orgao_repo,
                        self.apensamento_repo,
                        CasaLegislativa.CAMARA,
                    )
                    eventos_unificados.extend(
                        norm_c.normalizar(real_id, tramitacoes_camara)
                    )

                if tramitacoes_senado:
                    norm_s = NormalizarTramitacaoService(
                        self.fase_repo,
                        self.orgao_repo,
                        self.apensamento_repo,
                        CasaLegislativa.SENADO,
                    )
                    eventos_unificados.extend(
                        norm_s.normalizar(real_id, tramitacoes_senado)
                    )

                # 4. Ordenar e deduplicar
                # Ordena por data e depois por sequencia
                eventos_unificados.sort(key=lambda e: (e.data_evento, e.sequencia))

                # Deduplicação por data e descrição (caso as casas repitam o mesmo evento de trânsito)
                vistos = set()
                eventos_finais = []
                for e in eventos_unificados:
                    chave = (e.data_evento[:16], e.descricao_original[:50].lower())
                    if chave not in vistos:
                        vistos.add(chave)
                        eventos_finais.append(e)

                eventos = eventos_finais
                # Forçamos a sequencia correta após unificar
                for i, e in enumerate(eventos):
                    e.sequencia = i + 1

                # Sincroniza a proposição
                if eventos:
                    self.evento_repo.salvar_lote(eventos)
                    self._sincronizar_proposicao(proposicao, eventos)
                    self.proposicao_repo.salvar(proposicao)
            else:
                # Fallback para tipos não unificáveis (ou sem proposição)
                if proposicao and "Câmara" in (proposicao.orgao_origem or ""):
                    dados_brutos = await self.camara_adapter.buscar_tramitacoes_brutas(
                        int(real_id), client=client
                    )
                    casa_padrao = CasaLegislativa.CAMARA
                else:
                    dados_brutos = await self.senado_adapter.buscar_tramitacoes_brutas(
                        int(real_id), client=client, timeout=req_timeout
                    )
                    casa_padrao = CasaLegislativa.SENADO

            if not eventos and dados_brutos:
                # Normalizar e salvar (lógica original)
                normalizer = NormalizarTramitacaoService(
                    fase_repo=self.fase_repo,
                    orgao_repo=self.orgao_repo,
                    apensamento_repo=self.apensamento_repo,
                    casa_padrao=casa_padrao,
                )
                eventos = normalizer.normalizar(real_id, dados_brutos)
                if eventos:
                    self.evento_repo.salvar_lote(eventos)
                    if proposicao:
                        self._sincronizar_proposicao(proposicao, eventos)
                        self.proposicao_repo.salvar(proposicao)

        # 5. Aplica a lógica do modo
        if modo == ModoMovimentacao.RESUMIDO:
            # Se já temos a proposição carregada, usamos ela; caso contrário buscamos
            prop_resumo = proposicao or self.proposicao_repo.buscar_por_id(real_id)

            data_encerramento_obj = None
            if prop_resumo and prop_resumo.data_encerramento:
                try:
                    from datetime import datetime

                    data_encerramento_obj = datetime.fromisoformat(
                        prop_resumo.data_encerramento[:10]
                    ).date()
                except (ValueError, TypeError):
                    pass

            return self._agregar_service.executar(
                eventos,
                proposicao_encerrada=data_encerramento_obj is not None,
                data_encerramento=data_encerramento_obj,
            )

        if modo == ModoMovimentacao.RELEVANTE:
            return [e for e in eventos if e.relevante]

        return eventos

    def _sincronizar_proposicao(self, proposicao: Any, eventos: List[EventoTramitacao]):
        """Atualiza campos da proposição baseando-se no histórico de eventos."""
        if not eventos:
            return

        # 1. Determinar Encerramento
        ultimo_evento_terminal = None
        for e in reversed(eventos):
            if e.eh_evento_terminal:
                ultimo_evento_terminal = e
                break

        if ultimo_evento_terminal:
            proposicao.data_encerramento = ultimo_evento_terminal.data_evento[:10]
            # Se terminou, o status deve refletir isso
            proposicao.status = ultimo_evento_terminal.descricao_original
        else:
            proposicao.data_encerramento = None
            # Se não terminou, pega o último status relevante ou o último de todos
            for e in reversed(eventos):
                if e.relevante or e.deliberativo:
                    proposicao.status = e.descricao_original
                    break

        # 2. Atualizar órgão atual
        if eventos[-1].sigla_orgao:
            proposicao.orgao_atual = eventos[-1].sigla_orgao

        # 3. Normalizar e recalcular

        # Garante que temos os métodos de domínio se for um model
        if hasattr(proposicao, "normalizar_campo_status"):
            proposicao.normalizar_campo_status()
            proposicao.atualizar_metricas()
