import logging
import os

from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlmodel import Session, select

from infrastructure.adapters.security_adapter import get_password_hash
from infrastructure.database import engine

# Importando modelos para registro no metadata
from infrastructure.database.models.proposicao_model import (
    ProposicaoModel,  # noqa: F401
)
from infrastructure.database.models.user_model import UserModel
from infrastructure.repositories.sql_fase_analitica_repository import (
    SQLFaseAnaliticaRepository,
)
from infrastructure.repositories.sql_orgao_legislativo_repository import (
    SQLOrgaoLegislativoRepository,
)

logger = logging.getLogger(__name__)


def run_migrations():
    logger.info("Executando migrações do Alembic (upgrade head)...")
    alembic_ini_path = "alembic.ini"
    if not os.path.exists(alembic_ini_path):
        alembic_ini_path = "../alembic.ini"
        if not os.path.exists(alembic_ini_path):
            alembic_ini_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "alembic.ini"
            )

    if not os.path.exists(alembic_ini_path):
        raise FileNotFoundError("Arquivo alembic.ini não encontrado!")

    alembic_cfg = Config(alembic_ini_path)
    try:
        command.upgrade(alembic_cfg, "head")
        logger.info("Migrações do Alembic executadas com sucesso!")
    except Exception as e:
        logger.error(f"Falha ao executar migrações do Alembic: {e}")
        raise e


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


def seed_lookup_tables():
    logger.info("Inserindo tabelas de referência (Fases e Órgãos)...")
    with Session(engine) as session:
        SQLFaseAnaliticaRepository(session).seed_fases()
        SQLOrgaoLegislativoRepository(session).seed_orgaos()


def seed_bootstrap_baselines():
    logger.info("Aplicando seed de Bootstrap para baseline_tramitacao...")
    seed_file_path = os.path.join(
        os.path.dirname(__file__),
        "infrastructure",
        "database",
        "seeds",
        "bootstrap_seeds.sql",
    )
    if not os.path.exists(seed_file_path):
        # Tenta também caso esteja rodando de outra estrutura
        seed_file_path = os.path.join(
            os.path.dirname(__file__),
            "backend",
            "src",
            "infrastructure",
            "database",
            "seeds",
            "bootstrap_seeds.sql",
        )
        if not os.path.exists(seed_file_path):
            raise FileNotFoundError(f"Arquivo de seed não encontrado: {seed_file_path}")

    with open(seed_file_path, encoding="utf-8") as f:
        sql_content = f.read()

    with Session(engine) as session:
        try:
            session.execute(text(sql_content))
            session.commit()
            logger.info(
                "Seed de Bootstrap para baseline_tramitacao aplicado com sucesso!"
            )
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao aplicar o seed de Bootstrap: {e}")
            raise e


def run():
    logger.info("Inicializando banco de dados...")
    run_migrations()
    seed_demo_user()
    seed_lookup_tables()
    seed_bootstrap_baselines()
    logger.info("Tabelas e dados iniciais configurados com sucesso!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
