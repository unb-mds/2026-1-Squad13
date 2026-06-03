from datetime import datetime

from infrastructure.repositories.sql_evento_tramitacao_repository import (
    SQLEventoTramitacaoRepository,
)
from infrastructure.repositories.sql_proposicao_repository import (
    SQLProposicaoRepository,
)


class ObterConfiabilidadeService:
    """
    Serviço que calcula os metadados de confiabilidade e cobertura de dados
    de uma proposição de forma dinâmica baseada no preenchimento de campos e eventos.
    """

    def __init__(
        self,
        repository: SQLProposicaoRepository,
        evento_repo: SQLEventoTramitacaoRepository,
    ):
        self.repository = repository
        self.evento_repo = evento_repo

    async def executar(self, id_proposicao: str) -> dict:
        # 1. Busca por ID
        proposicao = self.repository.buscar_por_id(id_proposicao)
        if not proposicao:
            # Tenta buscar por slug / código canônico se houver hífen
            if "-" in id_proposicao:
                partes = id_proposicao.split("-")
                if len(partes) == 3:
                    tipo, numero, ano_str = partes
                    try:
                        ano = int(ano_str)
                        proposicao = self.repository.buscar_por_codigo(
                            tipo, numero, ano
                        )
                    except ValueError:
                        pass

        if not proposicao:
            raise ValueError(f"Proposição {id_proposicao} não encontrada.")

        # 2. Verifica histórico de eventos no banco
        events = self.evento_repo.buscar_por_proposicao(str(proposicao.id))

        # Calcula cobertura de dados de forma determinística
        campos_validar = [
            proposicao.tipo,
            proposicao.numero,
            proposicao.ano,
            proposicao.ementa,
            proposicao.autor,
            proposicao.orgao_origem,
            proposicao.status,
            proposicao.orgao_atual,
            proposicao.data_apresentacao,
            proposicao.data_ultima_movimentacao,
            proposicao.link_oficial,
            proposicao.regime_tramitacao,
        ]
        preenchidos = sum(
            1 for c in campos_validar if c is not None and str(c).strip() != ""
        )
        proporcao = preenchidos / len(campos_validar)

        cobertura = 70 + int(proporcao * 25)
        if proposicao.tags:
            cobertura += 5
        cobertura = min(cobertura, 100)

        # Nível de Confiabilidade
        if cobertura >= 90:
            confiabilidade = "alta"
        elif cobertura >= 70:
            confiabilidade = "media"
        else:
            confiabilidade = "baixa"

        status_historico = "completo" if events else "parcial"

        # Formata data da última atualização
        dt_atualizacao = None
        if proposicao.data_calculo_metricas:
            dt_atualizacao = proposicao.data_calculo_metricas
        elif proposicao.data_ultima_movimentacao:
            try:
                dt_atualizacao = datetime.fromisoformat(
                    proposicao.data_ultima_movimentacao.replace("Z", "+00:00")
                )
            except ValueError:
                pass

        if not dt_atualizacao:
            dt_atualizacao = datetime.now()

        ultima_atualizacao = dt_atualizacao.strftime("%d/%m/%Y às %H:%M")

        fontes = [
            "Sistema de Tramitação do Congresso Nacional (API oficial)",
            "Portal da Legislação Federal",
        ]
        if proposicao.orgao_origem and "senado" in proposicao.orgao_origem.lower():
            fontes.append("Senado Federal (API Dados Abertos)")
        else:
            fontes.append("Câmara dos Deputados (API v2)")

        limitacoes = [
            "Eventos anteriores a 01/01/2020 podem ter registro parcial devido à migração de sistemas",
            "Despachos internos de comissões podem ter atraso de até 48h para publicação",
        ]
        if not events:
            limitacoes.append(
                "O histórico de eventos não pôde ser recuperado da API de origem"
            )

        return {
            "cobertura": cobertura,
            "statusHistorico": status_historico,
            "ultimaAtualizacao": ultima_atualizacao,
            "fontes": fontes,
            "limitacoes": limitacoes,
            "confiabilidade": confiabilidade,
        }
