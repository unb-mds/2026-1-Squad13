import logging
from infrastructure.database import init_db, engine
from sqlmodel import Session, select
from infrastructure.database.models.user_model import UserModel
from infrastructure.adapters.security_adapter import get_password_hash

# Importando modelos para registro no metadata
from infrastructure.database.models.proposicao_model import ProposicaoModel  # noqa: F401

logger = logging.getLogger(__name__)


def seed_demo_user():
    logger.info("Verificando usuário de demonstração...")
    with Session(engine) as session:
        statement = select(UserModel).where(UserModel.email == "demo@lextrack.gov.br")
        demo_user = session.exec(statement).first()

        if not demo_user:
            logger.info("Criando usuário de demonstração (demo@lextrack.gov.br)...")
            user = UserModel(
                nome="Demo User",
                email="demo@lextrack.gov.br",
                hashed_password=get_password_hash("demo123"),
                perfil="analista",
            )
            session.add(user)
            session.commit()
            logger.info("Usuário de demonstração criado!")
        else:
            logger.info("Usuário de demonstração já existe.")


def run():
    logger.info("Criando tabelas no banco de dados...")
    init_db()
    seed_demo_user()
    logger.info("Tabelas e dados iniciais configurados com sucesso!")


if __name__ == "__main__":
    run()
