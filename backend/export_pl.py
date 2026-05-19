import json
import sys
import os
from sqlmodel import Session, select
from datetime import datetime, date

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.getcwd(), "src"))

from infrastructure.database import engine
from infrastructure.database.models.proposicao_model import ProposicaoModel
from infrastructure.database.models.evento_tramitacao_model import EventoTramitacaoModel

def export_to_json(numero, ano, output_file=None):
    with Session(engine) as session:
        p = session.exec(
            select(ProposicaoModel).where(ProposicaoModel.numero == numero, ProposicaoModel.ano == ano)
        ).first()

        if not p:
            return {"erro": "Proposição não encontrada"}

        events = session.exec(
            select(EventoTramitacaoModel)
            .where(EventoTramitacaoModel.proposicao_id == p.id)
            .order_by(EventoTramitacaoModel.data_evento.asc(), EventoTramitacaoModel.sequencia.asc())
        ).all()
        data = p.model_dump()
        data['historico_tramitacao'] = [e.model_dump() for e in events]
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Sucesso: Dados salvos em {output_file}")
        
        return data

if __name__ == "__main__":
    # Se houver um argumento, usa como nome do arquivo
    filename = sys.argv[1] if len(sys.argv) > 1 else "pl_4015_2023.json"
    export_to_json("4015", 2023, filename)
