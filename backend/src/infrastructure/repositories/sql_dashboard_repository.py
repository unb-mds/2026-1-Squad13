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
            func.coalesce(func.avg(ProposicaoModel.indice_atraso_relativo), 0).label(
                "iar_medio"
            ),
            func.coalesce(func.avg(ProposicaoModel.indice_espera_improdutiva), 0).label(
                "iei_medio"
            ),
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
                "iarMedio": 0.0,
                "ieiMedio": 0.0,
                "percentualAtrasadas": 0,
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
            "comissaoMaiorTempo": pior_orgao_row[0] if pior_orgao_row else "N/A",
            "comissaoMaiorTempoMedia": int(pior_orgao_row[1] or 0)
            if pior_orgao_row
            else 0,
            "iarMedio": round(float(row.iar_medio or 0.0), 2),
            "ieiMedio": round(float(row.iei_medio or 0.0), 2),
            "percentualAtrasadas": int((row.com_atraso or 0) / row.total * 100)
            if row.total > 0
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

    def obter_evolucao_temporal(self, filtros: dict | None) -> list[dict]:
        stmt = select(
            ProposicaoModel.data_apresentacao, ProposicaoModel.data_encerramento
        )
        stmt = self._aplicar_filtros(stmt, filtros)
        rows = self.session.exec(stmt).all()

        MONTH_MAP = {
            1: "Jan",
            2: "Fev",
            3: "Mar",
            4: "Abr",
            5: "Mai",
            6: "Jun",
            7: "Jul",
            8: "Ago",
            9: "Set",
            10: "Out",
            11: "Nov",
            12: "Dez",
        }

        from datetime import date

        hoje = date.today()
        meses_lista = []
        for i in range(6, -1, -1):
            ano_diff = (hoje.month - 1 - i) // 12
            mes_idx = (hoje.month - 1 - i) % 12 + 1
            ano_val = hoje.year + ano_diff
            meses_lista.append((ano_val, mes_idx))

        def format_month_key(year: int, month: int) -> str:
            short_year = str(year)[-2:]
            return f"{MONTH_MAP[month]}/{short_year}"

        counts = {
            format_month_key(y, m): {"entradas": 0, "saidas": 0} for y, m in meses_lista
        }

        for data_apr, data_enc in rows:
            if data_apr:
                try:
                    y_apr = int(data_apr[:4])
                    m_apr = int(data_apr[5:7])
                    key = format_month_key(y_apr, m_apr)
                    if key in counts:
                        counts[key]["entradas"] += 1
                except Exception:
                    pass
            if data_enc:
                try:
                    y_enc = int(data_enc[:4])
                    m_enc = int(data_enc[5:7])
                    key = format_month_key(y_enc, m_enc)
                    if key in counts:
                        counts[key]["saidas"] += 1
                except Exception:
                    pass

        result = []
        for y, m in meses_lista:
            key = format_month_key(y, m)
            result.append(
                {
                    "mes": key,
                    "entradas": counts[key]["entradas"],
                    "saidas": counts[key]["saidas"],
                }
            )
        return result

    def obter_transicoes_casas(self, filtros: dict | None) -> dict:
        stmt = select(
            ProposicaoModel.id,
            ProposicaoModel.orgao_origem,
            ProposicaoModel.orgao_atual,
            ProposicaoModel.status,
        )
        stmt = self._aplicar_filtros(stmt, filtros)
        props = self.session.exec(stmt).all()

        if not props:
            return {
                "transitions": [
                    {
                        "origem": "Câmara",
                        "destino": "Senado",
                        "quantidade": 0,
                        "tempoMedioTransicao": 0,
                    },
                    {
                        "origem": "Senado",
                        "destino": "Câmara",
                        "quantidade": 0,
                        "tempoMedioTransicao": 0,
                    },
                ],
                "totalCamara": 0,
                "totalSenado": 0,
            }

        total_camara = 0
        total_senado = 0
        ids = []

        for p in props:
            id_p, orgao_origem, orgao_atual, status = p
            ids.append(str(id_p))

            casa = "Câmara"
            if status in ("Sancionada", "Vetada"):
                casa = "Sanção"
            elif (orgao_origem and "senado" in orgao_origem.lower()) or (
                orgao_atual
                and ("sf" in orgao_atual.lower() or "senado" in orgao_atual.lower())
            ):
                casa = "Senado"

            if casa == "Câmara":
                total_camara += 1
            elif casa == "Senado":
                total_senado += 1

        from infrastructure.database.models.evento_tramitacao_model import (
            EventoTramitacaoModel,
        )

        events = []
        chunk_size = 500
        for i in range(0, len(ids), chunk_size):
            chunk_ids = ids[i : i + chunk_size]
            stmt_ev = (
                select(
                    EventoTramitacaoModel.proposicao_id,
                    EventoTramitacaoModel.data_evento,
                    EventoTramitacaoModel.sigla_orgao,
                    EventoTramitacaoModel.sequencia,
                )
                .where(EventoTramitacaoModel.proposicao_id.in_(chunk_ids))
                .order_by(
                    EventoTramitacaoModel.proposicao_id,
                    EventoTramitacaoModel.data_evento,
                    EventoTramitacaoModel.sequencia,
                )
            )
            events.extend(self.session.exec(stmt_ev).all())

        events_by_prop = {}
        for ev in events:
            pid, data_ev, sigla, seq = ev
            if pid not in events_by_prop:
                events_by_prop[pid] = []
            events_by_prop[pid].append((data_ev, sigla))

        trans_c_s = []
        trans_s_c = []

        for _pid, prop_events in events_by_prop.items():
            if len(prop_events) < 2:
                continue

            events_with_house = []
            for data_ev, sigla in prop_events:
                if not sigla:
                    house = None
                elif "sf" in sigla.lower() or "senado" in sigla.lower():
                    house = "Senado"
                else:
                    house = "Câmara"
                events_with_house.append((data_ev, house))

            last_known_house = None
            for _, house in events_with_house:
                if house:
                    last_known_house = house
                    break
            if not last_known_house:
                last_known_house = "Câmara"

            filled_events = []
            for data_ev, house in events_with_house:
                if house:
                    last_known_house = house
                filled_events.append((data_ev, last_known_house))

            current_house = filled_events[0][1]
            last_date_str = filled_events[0][0]

            for i in range(1, len(filled_events)):
                date_str, house = filled_events[i]
                if house != current_house:
                    try:
                        from datetime import datetime

                        d1 = datetime.fromisoformat(
                            last_date_str[:10].replace(" ", "T")
                        )
                        d2 = datetime.fromisoformat(date_str[:10].replace(" ", "T"))
                        diff_days = max(1, (d2 - d1).days)
                    except Exception:
                        diff_days = 1

                    if current_house == "Câmara" and house == "Senado":
                        trans_c_s.append(diff_days)
                    elif current_house == "Senado" and house == "Câmara":
                        trans_s_c.append(diff_days)

                    current_house = house
                last_date_str = date_str

        qty_c_s = len(trans_c_s)
        avg_c_s = int(sum(trans_c_s) / qty_c_s) if qty_c_s > 0 else 0

        qty_s_c = len(trans_s_c)
        avg_s_c = int(sum(trans_s_c) / qty_s_c) if qty_s_c > 0 else 0

        return {
            "transitions": [
                {
                    "origem": "Câmara",
                    "destino": "Senado",
                    "quantidade": qty_c_s,
                    "tempoMedioTransicao": avg_c_s,
                },
                {
                    "origem": "Senado",
                    "destino": "Câmara",
                    "quantidade": qty_s_c,
                    "tempoMedioTransicao": avg_s_c,
                },
            ],
            "totalCamara": total_camara,
            "totalSenado": total_senado,
        }
