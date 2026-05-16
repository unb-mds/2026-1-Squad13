"""
Script de auditoria da transição para o Modelo Analítico (Etapa 3/Final).

Garante que o banco de dados esteja consistente, identificando:
- Proposições com atraso na tramitação (cache atualizado)
- Eventos de tramitação órfãos (sem proposição)
- Eventos ainda marcados como 'NAO_CLASSIFICADO'
- Estatísticas de uso das Fases Analíticas
"""

from collections import Counter
from sqlmodel import select
from infrastructure.database import get_session
from domain.entities.proposicao import Proposicao
from domain.entities.evento_tramitacao import EventoTramitacao
from domain.entities.fase_analitica import FaseAnalitica


def audit_db() -> None:
    print("=== Auditoria do Modelo Analítico ===")
    with next(get_session()) as session:
        # 1. Total de Proposições vs com atraso
        proposicoes = session.exec(select(Proposicao)).all()
        com_atraso = [p for p in proposicoes if p.tem_atraso]
        print("\n[Proposições]")
        print(f"Total: {len(proposicoes)}")
        print(f"Com atraso (> 180 dias): {len(com_atraso)}")

        # 2. Total de Eventos e Órfãos
        eventos = session.exec(select(EventoTramitacao)).all()
        prop_ids = {str(p.id) for p in proposicoes}
        orfaos = [e for e in eventos if e.proposicao_id not in prop_ids]
        print("\n[Eventos de Tramitação]")
        print(f"Total: {len(eventos)}")
        print(f"Órfãos (sem proposição válida): {len(orfaos)}")
        if orfaos:
            print("  ⚠️ ALERTA: Há eventos órfãos!")

        # 3. Tipos de Eventos
        tipos = Counter(e.tipo_evento for e in eventos)
        nao_classificados = tipos.get("NAO_CLASSIFICADO", 0)
        print("\n[Tipos de Eventos]")
        print(f"NAO_CLASSIFICADO: {nao_classificados} ({(nao_classificados/len(eventos)*100 if eventos else 0):.1f}%)")
        print(f"Diversidade de tipos mapeados: {len([t for t in tipos if t != 'NAO_CLASSIFICADO'])}")

        # 4. Uso de Fases Analíticas
        fases_banco = session.exec(select(FaseAnalitica)).all()
        print("\n[Fases Analíticas]")
        print(f"Total de fases mapeadas: {len(fases_banco)}")
        com_fase = sum(1 for e in eventos if e.fase_analitica_id is not None)
        print(f"Eventos vinculados a uma fase: {com_fase} ({(com_fase/len(eventos)*100 if eventos else 0):.1f}%)")

        print("\n=== Fim da Auditoria ===")

if __name__ == "__main__":
    audit_db()
