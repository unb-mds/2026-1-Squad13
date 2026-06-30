import asyncio
import sys

from sqlmodel import Session, select

sys.path.append("/app/src")

from infrastructure.database import engine
from infrastructure.database.models.evento_tramitacao_model import EventoTramitacaoModel
from infrastructure.database.models.proposicao_model import ProposicaoModel


def formatarDataBr(dataStr):
    if not dataStr:
        return ""
    # Retorna DD/MM/AAAA
    parts = dataStr.split("T")[0].split("-")
    if len(parts) == 3:
        return f"{parts[2]}/{parts[1]}/{parts[0]}"
    return dataStr


def mapMovimentacoesToTransitSteps(movs):
    steps = []
    if len(movs) == 0:
        return [{"casa": "Câmara", "tipo": "origem", "dataEntrada": "Apresentação"}]

    # Ordena cronologicamente
    sortedMovs = sorted(movs, key=lambda x: x["dataEvento"])

    # Primeira casa
    first_sigla = sortedMovs[0].get("siglaOrgao") or ""
    first_orgao = sortedMovs[0].get("orgao") or ""

    is_senado = (
        "sf" in first_sigla.lower()
        or "sf" in first_orgao.lower()
        or "senado" in first_orgao.lower()
    )
    currentCasa = "Senado" if is_senado else "Câmara"

    steps.push_val = lambda val: steps.append(val)

    steps.push_val(
        {
            "casa": currentCasa,
            "tipo": "origem",
            "dataEntrada": formatarDataBr(sortedMovs[0]["dataEvento"]),
            "duracaoDias": 0,
        }
    )

    for i in range(1, len(sortedMovs)):
        m = sortedMovs[i]
        sigla = m.get("siglaOrgao") or ""
        orgao = m.get("orgao") or ""

        m_is_senado = (
            "sf" in sigla.lower() or "sf" in orgao.lower() or "senado" in orgao.lower()
        )
        mCasa = "Senado" if m_is_senado else "Câmara"

        if mCasa != currentCasa:
            steps[-1]["dataSaida"] = formatarDataBr(m["dataEvento"])
            start = datetime_from_str(sortedMovs[i - 1]["dataEvento"])
            end = datetime_from_str(m["dataEvento"])
            steps[-1]["duracaoDias"] = max(
                1, int((end - start).total_seconds() / (24 * 3600))
            )

            currentCasa = mCasa
            steps.push_val(
                {
                    "casa": currentCasa,
                    "tipo": "revisora" if len(steps) == 1 else "retorno",
                    "dataEntrada": formatarDataBr(m["dataEvento"]),
                    "duracaoDias": 0,
                }
            )

    # Último step duracao
    start = datetime_from_str(sortedMovs[-1]["dataEvento"])
    import datetime

    now = datetime.datetime.now(datetime.UTC)
    steps[-1]["duracaoDias"] = max(1, int((now - start).total_seconds() / (24 * 3600)))

    return steps


def datetime_from_str(s):
    s = s.replace("Z", "").replace(" ", "T")
    if "T" in s:
        date_part, time_part = s.split("T")
        # remove timezone offset if any
        time_part = time_part.split("+")[0].split("-")[0]
        # pad time part if truncated
        if len(time_part) == 5:
            time_part += ":00"
        s = f"{date_part}T{time_part}"
    else:
        s += "T00:00:00"
    import datetime

    return datetime.datetime.fromisoformat(s).replace(tzinfo=datetime.UTC)


async def main():
    print("=== SIMULANDO MAPEAMENTO DE TRÂNSITO PARA PEC 35/2011 ===")
    with Session(engine) as session:
        # Busca a proposicao
        prop = session.exec(
            select(ProposicaoModel).where(
                ProposicaoModel.tipo == "PEC",
                ProposicaoModel.numero == "35",
                ProposicaoModel.ano == 2011,
                ProposicaoModel.orgao_origem == "Senado Federal",
            )
        ).first()

        if not prop:
            print("Proposição não encontrada no banco local.")
            return

        print(f"ID Proposição: {prop.id}")

        # Busca eventos
        eventos = session.exec(
            select(EventoTramitacaoModel).where(
                EventoTramitacaoModel.proposicao_id == prop.id
            )
        ).all()

        print(f"Total de Eventos no Banco Local: {len(eventos)}")

        movs = []
        for e in eventos:
            movs.append(
                {
                    "siglaOrgao": e.sigla_orgao,
                    "dataEvento": e.data_evento,
                    "descricao": e.descricao_original,
                }
            )

        for m in sorted(movs, key=lambda x: x["dataEvento"]):
            print(f"  [{m['dataEvento']}] [{m['siglaOrgao']}] {m['descricao'][:50]}")

        steps = mapMovimentacoesToTransitSteps(movs)
        print("\n=== Passos de Trânsito Gerados ===")
        for s in steps:
            print(s)


if __name__ == "__main__":
    asyncio.run(main())
