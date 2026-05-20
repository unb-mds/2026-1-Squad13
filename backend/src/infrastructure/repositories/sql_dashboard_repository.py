from typing import Any

from sqlalchemy import and_, case, func, or_
from sqlmodel import Session, select

from domain.constants import LIMITE_DIAS_ATRASO
from infrastructure.database.models.proposicao_model import ProposicaoModel


class SQLDashboardRepository:
    def __init__(self, session: Session):
        self.session = session

    def _aplicar_filtros(self, statement: Any, filtros: dict | None) -> Any:
        if not filtros:
            return statement

        busca = filtros.get("busca")
        tipo = filtros.get("tipo")
        status = filtros.get("status")
        orgao_origem = filtros.get("orgao_origem")
        data_inicio = filtros.get("data_inicio")
        data_fim = filtros.get("data_fim")

        if tipo:
            statement = statement.where(
                func.lower(ProposicaoModel.tipo) == tipo.lower()
            )
        if status:
            statement = statement.where(
                func.lower(ProposicaoModel.status) == status.lower()
            )
        if orgao_origem:
            statement = statement.where(
                func.lower(ProposicaoModel.orgao_origem) == orgao_origem.lower()
            )
        if data_inicio:
            statement = statement.where(
                ProposicaoModel.data_apresentacao >= data_inicio
            )
        if data_fim:
            statement = statement.where(ProposicaoModel.data_apresentacao <= data_fim)
        if busca:
            termo = f"%{busca}%"
            statement = statement.where(
                (ProposicaoModel.ementa.ilike(termo))
                | (ProposicaoModel.numero.ilike(termo))
                | (ProposicaoModel.autor.ilike(termo))
            )

        return statement

    def _status_agrupado_case(self):
        return case(
            (
                or_(
                    ProposicaoModel.status.ilike("%aprovad%"),
                    ProposicaoModel.status.ilike("%sancionad%"),
                    ProposicaoModel.status.ilike("%norma jurídica%"),
                    ProposicaoModel.status.ilike("%promulgad%"),
                    ProposicaoModel.status.ilike("%transformad%"),
                    ProposicaoModel.status.ilike("%enviado à sanção%"),
                    ProposicaoModel.status.ilike("%ofício ao senado - sancionado%"),
                ),
                "Aprovada/Sancionada",
            ),
            (
                or_(
                    ProposicaoModel.status.ilike("%rejeitad%"),
                    ProposicaoModel.status.ilike("%arquivad%"),
                    ProposicaoModel.status.ilike("%retirad%"),
                    ProposicaoModel.status.ilike("%prejudicad%"),
                    ProposicaoModel.status.ilike("%indiferid%"),
                    ProposicaoModel.status.ilike("%devolvida%"),
                    ProposicaoModel.status.ilike("%negado%"),
                    ProposicaoModel.status.ilike("%materia despachada%"),
                ),
                "Rejeitada/Arquivada",
            ),
            (
                or_(
                    ProposicaoModel.status.ilike("%tramitação%"),
                    ProposicaoModel.status.ilike("%análise%"),
                    ProposicaoModel.status.ilike("%votação%"),
                    ProposicaoModel.status.ilike("%pauta%"),
                    ProposicaoModel.status.ilike("%apresentação%"),
                    ProposicaoModel.status.ilike("%mesa%"),
                    ProposicaoModel.status.ilike("%relator%"),
                    ProposicaoModel.status.ilike("%parecer%"),
                    ProposicaoModel.status.ilike("%aguardando%"),
                    ProposicaoModel.status.ilike("%comissão%"),
                    ProposicaoModel.status.ilike("%ofício%"),
                    ProposicaoModel.status.ilike("%recebimento%"),
                    ProposicaoModel.status.ilike("%leitura%"),
                    ProposicaoModel.status.ilike("%despacho%"),
                    ProposicaoModel.status.ilike("%relatório%"),
                    ProposicaoModel.status.ilike("sem status"),
                ),
                "Em tramitação",
            ),
            else_="Outros",
        )

    def obter_metricas_gerais(self, filtros: dict | None) -> dict:
        status_agrupado = self._status_agrupado_case()

        stmt = select(
            func.count().label("total"),
            func.coalesce(func.avg(ProposicaoModel.tempo_total_dias), 0).label(
                "tempo_medio"
            ),
            func.sum(
                case(
                    (
                        and_(
                            ProposicaoModel.tempo_total_dias > LIMITE_DIAS_ATRASO,
                            ProposicaoModel.data_encerramento.is_(None),
                        ),
                        1,
                    ),
                    else_=0,
                )
            ).label("com_atraso"),
            func.sum(
                case((status_agrupado == "Aprovada/Sancionada", 1), else_=0)
            ).label("aprovadas"),
            func.sum(case((status_agrupado == "Em tramitação", 1), else_=0)).label(
                "em_tramitacao"
            ),
            func.sum(
                case((status_agrupado == "Rejeitada/Arquivada", 1), else_=0)
            ).label("rejeitadas"),
        )
        stmt = self._aplicar_filtros(stmt, filtros)

        row = self.session.exec(stmt).first()
        if not row or row.total == 0:
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

        stmt_orgao = select(
            ProposicaoModel.orgao_atual,
            func.avg(ProposicaoModel.tempo_total_dias).label("media_tempo"),
        ).where(
            ProposicaoModel.orgao_atual.isnot(None),
            ProposicaoModel.tempo_total_dias.isnot(None),
        )
        stmt_orgao = self._aplicar_filtros(stmt_orgao, filtros)
        stmt_orgao = (
            stmt_orgao.group_by(ProposicaoModel.orgao_atual)
            .order_by(func.avg(ProposicaoModel.tempo_total_dias).desc())
            .limit(1)
        )

        pior_orgao_row = self.session.exec(stmt_orgao).first()

        return {
            "tempoMedioTramitacao": int(row.tempo_medio or 0),
            "totalProposicoes": row.total,
            "proposicoesComAtraso": int(row.com_atraso or 0),
            "totalAprovadas": int(row.aprovadas or 0),
            "totalEmTramitacao": int(row.em_tramitacao or 0),
            "totalRejeitadas": int(row.rejeitadas or 0),
            "comissaoMaiorTempo": pior_orgao_row.orgao_atual
            if pior_orgao_row
            else "N/A",
            "comissaoMaiorTempoMedia": int(pior_orgao_row.media_tempo or 0)
            if pior_orgao_row
            else 0,
        }

    def obter_dados_tipo(self, filtros: dict | None) -> list[dict]:
        stmt = select(
            ProposicaoModel.tipo,
            func.count().label("quantidade"),
            func.coalesce(func.avg(ProposicaoModel.tempo_total_dias), 0).label(
                "tempo_medio"
            ),
        ).group_by(ProposicaoModel.tipo)

        stmt = self._aplicar_filtros(stmt, filtros)
        stmt = stmt.order_by(func.count().desc())

        rows = self.session.exec(stmt).all()
        return [
            {
                "tipo": row.tipo,
                "tempoMedio": int(row.tempo_medio),
                "quantidade": row.quantidade,
            }
            for row in rows
        ]

    def obter_dados_comissao(self, filtros: dict | None) -> list[dict]:
        stmt = select(
            func.coalesce(ProposicaoModel.orgao_atual, "Desconhecido").label(
                "comissao"
            ),
            func.count().label("quantidade"),
            func.coalesce(func.avg(ProposicaoModel.tempo_total_dias), 0).label(
                "tempo_medio"
            ),
        ).group_by(func.coalesce(ProposicaoModel.orgao_atual, "Desconhecido"))

        stmt = self._aplicar_filtros(stmt, filtros)
        stmt = stmt.order_by(func.avg(ProposicaoModel.tempo_total_dias).desc()).limit(
            10
        )

        rows = self.session.exec(stmt).all()
        return [
            {
                "comissao": row.comissao,
                "tempoMedio": int(row.tempo_medio),
                "quantidade": row.quantidade,
            }
            for row in rows
        ]

    def obter_dados_status(self, filtros: dict | None) -> list[dict]:
        status_agrupado = self._status_agrupado_case()

        stmt_total = select(func.count()).select_from(ProposicaoModel)
        stmt_total = self._aplicar_filtros(stmt_total, filtros)
        total = self.session.exec(stmt_total).first() or 1

        stmt = select(
            status_agrupado.label("status"), func.count().label("quantidade")
        ).group_by(status_agrupado)

        stmt = self._aplicar_filtros(stmt, filtros)
        stmt = stmt.order_by(func.count().desc())

        rows = self.session.exec(stmt).all()
        return [
            {
                "status": row.status,
                "quantidade": row.quantidade,
                "percentual": int((row.quantidade / total) * 100) if total > 0 else 0,
            }
            for row in rows
        ]

    def obter_gargalos(self, filtros: dict | None) -> list[dict]:
        stmt = select(
            func.coalesce(ProposicaoModel.orgao_atual, "Desconhecido").label("orgao"),
            func.count().label("quantidade"),
            func.sum(
                case(
                    (
                        and_(
                            ProposicaoModel.tempo_total_dias > LIMITE_DIAS_ATRASO,
                            ProposicaoModel.data_encerramento.is_(None),
                        ),
                        1,
                    ),
                    else_=0,
                )
            ).label("atrasos"),
            func.coalesce(func.avg(ProposicaoModel.tempo_total_dias), 0).label(
                "tempo_medio"
            ),
        ).group_by(func.coalesce(ProposicaoModel.orgao_atual, "Desconhecido"))

        stmt = self._aplicar_filtros(stmt, filtros)

        rows = self.session.exec(stmt).all()
        resultado = []
        for row in rows:
            taxa_atraso = (
                (row.atrasos / row.quantidade * 100) if row.quantidade > 0 else 0
            )
            tempo_meses = (row.tempo_medio / 30.0) if row.tempo_medio else 0
            resultado.append(
                {
                    "orgao": row.orgao,
                    "tempoMedioMeses": round(tempo_meses, 1),
                    "quantidadeProposicoes": row.quantidade,
                    "taxaAtraso": round(taxa_atraso),
                }
            )

        return sorted(resultado, key=lambda x: x["taxaAtraso"], reverse=True)

    def obter_proposicoes_para_temas(self, filtros: dict | None) -> list[dict]:
        status_agrupado = self._status_agrupado_case()
        stmt = select(
            ProposicaoModel.tags,
            ProposicaoModel.tempo_total_dias,
            status_agrupado.label("status_agrupado"),
        ).where(ProposicaoModel.tags.isnot(None))
        stmt = self._aplicar_filtros(stmt, filtros)
        rows = self.session.exec(stmt).all()
        return [
            {
                "tags": row.tags,
                "tempo_total_dias": row.tempo_total_dias,
                "status_agrupado": row.status_agrupado,
            }
            for row in rows
        ]
