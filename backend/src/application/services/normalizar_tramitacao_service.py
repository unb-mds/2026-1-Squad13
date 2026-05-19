"""
Serviço de aplicação para normalização de tramitações brutas.

Transforma dados das APIs (Câmara/Senado) em eventos analíticos estruturados.
"""

import re
from datetime import datetime, date
from typing import List, Optional

from domain.entities.evento_tramitacao import EventoTramitacao
from domain.entities.orgao_legislativo import CasaLegislativa
from domain.entities.tipo_evento import TipoEvento
from domain.classificar_evento import (
    classificar_tipo_evento,
    determinar_fase_analitica,
)
from infrastructure.repositories.sql_fase_analitica_repository import (
    SQLFaseAnaliticaRepository,
)
from infrastructure.repositories.sql_orgao_legislativo_repository import (
    SQLOrgaoLegislativoRepository,
)


from infrastructure.repositories.sql_apensamento_repository import (
    SQLApensamentoRepository,
)


class NormalizarTramitacaoService:
    """
    Orquestra a transformação de tramitações brutas em EventoTramitacao.
    """

    def __init__(
        self,
        fase_repo: SQLFaseAnaliticaRepository,
        orgao_repo: SQLOrgaoLegislativoRepository,
        apensamento_repo: Optional[SQLApensamentoRepository] = None,
        casa_padrao: CasaLegislativa = CasaLegislativa.CAMARA,
    ):
        self.fase_repo = fase_repo
        self.orgao_repo = orgao_repo
        self.apensamento_repo = apensamento_repo
        self.casa_padrao = casa_padrao

        # Pre-cache das fases para não bater no banco a cada evento
        todas_fases = self.fase_repo.buscar_todas()
        self._fase_id_map = {f.codigo: f.id for f in todas_fases}

    def normalizar(
        self, proposicao_id: str, dados_brutos: List[dict]
    ) -> List[EventoTramitacao]:
        """
        Recebe a lista cronológica de dicts (data_hora, sequencia, sigla_orgao, descricao, payload_bruto)
        e retorna uma lista de EventoTramitacao normalizados.
        """
        eventos = []
        fase_anterior = None
        orgao_anterior = None
        orgaos_cacheados = set()

        for item in dados_brutos:
            descricao = item.get("descricao", "")

            # 1. Classificar o tipo
            tipo_evento = classificar_tipo_evento(descricao)

            # 2. Determinar a fase
            codigo_fase = determinar_fase_analitica(tipo_evento, fase_anterior)
            codigo_fase_str = codigo_fase.value if codigo_fase else None
            fase_analitica_id = self._fase_id_map.get(codigo_fase_str)

            # 3. Determinar flags analíticas
            deliberativo = tipo_evento in {
                TipoEvento.VOTACAO_COMISSAO,
                TipoEvento.VOTACAO_PLENARIO,
                TipoEvento.APROVACAO,
                TipoEvento.REJEICAO,
            }

            # NAO_CLASSIFICADO nunca altera a fase
            if tipo_evento == TipoEvento.NAO_CLASSIFICADO:
                mudou_fase = False
            else:
                mudou_fase = (fase_anterior is not None) and (
                    codigo_fase != fase_anterior
                )

            sigla_orgao = item.get("sigla_orgao")
            mudou_orgao = (orgao_anterior is not None) and (
                sigla_orgao != orgao_anterior
            )

            remessa_ou_retorno: Optional[str] = None
            marca_apensacao = False
            if tipo_evento in {
                TipoEvento.REMESSA_OUTRA_CASA,
                TipoEvento.ENVIO_EXECUTIVO,
            }:
                remessa_ou_retorno = "REMESSA"
            elif tipo_evento in {
                TipoEvento.RETORNO_INICIADORA,
                TipoEvento.RECEBIMENTO_OUTRA_CASA,
            }:
                remessa_ou_retorno = "RETORNO"
            elif tipo_evento == TipoEvento.APENSAMENTO:
                marca_apensacao = True
                # Tenta extrair ID da principal (Heurística: busca padrões como PEC 221/2019)
                if self.apensamento_repo:
                    match = re.search(r"([A-Z]{2,3})\s*(\d+)/(\d{4})", descricao)
                    if match:
                        sigla, numero, ano = match.groups()
                        principal_id = (
                            f"{sigla}{numero}{ano}"  # Formato simplificado da Câmara
                        )
                        from domain.entities.apensamento import Apensamento

                        apensamento = Apensamento(
                            materia_apensada_id=proposicao_id,
                            materia_principal_id=principal_id,
                            data_apensacao=item.get("data_hora", "")[:10],
                            casa=self.casa_padrao.value,
                            fonte_endpoint="CamaraAPI/Tramitacoes",
                            payload_bruto=item.get("payload_bruto"),
                            confianca=0.9,
                        )
                        self.apensamento_repo.salvar(apensamento)

            # 4. Resolver órgão (upsert para garantir que existe) apenas 1 vez por lote
            if sigla_orgao and sigla_orgao not in orgaos_cacheados:
                self.orgao_repo.buscar_ou_criar(
                    sigla=sigla_orgao,
                    casa=self.casa_padrao,
                )
                orgaos_cacheados.add(sigla_orgao)

            # 5. Instanciar a entidade
            evento = EventoTramitacao(
                proposicao_id=proposicao_id,
                data_evento=item.get("data_hora", ""),
                sequencia=item.get("sequencia", 0),
                sigla_orgao=sigla_orgao,
                descricao_original=descricao,
                tipo_evento=tipo_evento.value,
                fase_analitica_id=fase_analitica_id,
                deliberativo=deliberativo,
                mudou_fase=mudou_fase,
                mudou_orgao=mudou_orgao,
                remessa_ou_retorno=remessa_ou_retorno,
                marca_apensacao=marca_apensacao,
                payload_bruto=item.get("payload_bruto"),
            )
            eventos.append(evento)

            # Atualiza o estado para o próximo evento (apenas se não for NAO_CLASSIFICADO para fase)
            if tipo_evento != TipoEvento.NAO_CLASSIFICADO:
                fase_anterior = codigo_fase
            orgao_anterior = sigla_orgao

        # 6. Cálculo de tempos (dias_na_etapa) e atrasos
        # Como os eventos vêm em ordem cronológica ASC, o tempo na etapa de um evento
        # é a diferença para o evento seguinte.
        hoje = date.today()
        for i in range(len(eventos)):
            atual = eventos[i]
            data_atual = datetime.fromisoformat(atual.data_evento[:10]).date()

            if i + 1 < len(eventos):
                proximo = eventos[i + 1]
                data_prox = datetime.fromisoformat(proximo.data_evento[:10]).date()
                dias = (data_prox - data_atual).days
            else:
                # Último evento: tempo acumulado até hoje
                dias = (hoje - data_atual).days

            atual.dias_na_etapa = max(0, dias)
            # Regra de negócio: mais de 180 dias sem movimentação é considerado atraso
            atual.tem_atraso = atual.dias_na_etapa > 180

        return eventos
