import sys

sys.path.append("src")

from sqlmodel import Session, select

from domain.entities.proposicao import Proposicao
from infrastructure.database import engine
from infrastructure.database.models.proposicao_model import ProposicaoModel


def corrigir_status():
    try:
        with Session(engine) as session:
            statement = select(ProposicaoModel)
            models = session.exec(statement).all()
            print(
                f"Encontradas {len(models)} proposições para correção no banco de dados."
            )

            corrigidas = 0
            for model in models:
                entity = Proposicao.model_validate(model.model_dump())
                status_anterior = entity.status

                # Executa a normalização de domínio do backend
                entity.normalizar_campo_status()

                # Se o status mudou ou o original foi preenchido/alterado
                if (
                    entity.status != status_anterior
                    or model.status_original != entity.status_original
                ):
                    model.status = entity.status
                    model.status_original = entity.status_original
                    session.add(model)
                    corrigidas += 1

            if corrigidas > 0:
                session.commit()
                print(
                    f"Sucesso: {corrigidas} proposições foram corrigidas e normalizadas no banco de dados local!"
                )
            else:
                print("Nenhuma proposição precisou ser corrigida.")
    except Exception as e:
        print("Erro ao executar script de correção de status:", e)


if __name__ == "__main__":
    corrigir_status()
