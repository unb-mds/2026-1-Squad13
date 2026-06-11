import logging
import os

from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlmodel import Session

from application.services.reconstruir_periodos_service import ReconstruirPeriodosService
from infrastructure.database import engine
from infrastructure.database.models.periodo_fase_model import PeriodoFaseModel

# Importando modelos para registro no metadata
from infrastructure.database.models.proposicao_model import (
    ProposicaoModel,  # noqa: F401
)
from infrastructure.repositories.sql_evento_tramitacao_repository import (
    SQLEventoTramitacaoRepository,
)
from infrastructure.repositories.sql_fase_analitica_repository import (
    SQLFaseAnaliticaRepository,
)
from infrastructure.repositories.sql_orgao_legislativo_repository import (
    SQLOrgaoLegislativoRepository,
)
from infrastructure.repositories.sql_periodo_fase_repository import (
    SQLPeriodoFaseRepository,
)
from infrastructure.repositories.sql_proposicao_repository import (
    SQLProposicaoRepository,
)

logger = logging.getLogger(__name__)


def run_migrations():
    logger.info("🔍 Iniciando run_migrations()...")
    alembic_ini_path = "alembic.ini"
    if not os.path.exists(alembic_ini_path):
        alembic_ini_path = "../alembic.ini"
        if not os.path.exists(alembic_ini_path):
            alembic_ini_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "alembic.ini"
            )

    if not os.path.exists(alembic_ini_path):
        logger.error(
            f"❌ Arquivo alembic.ini não encontrado no caminho: {alembic_ini_path}"
        )
        raise FileNotFoundError("Arquivo alembic.ini não encontrado!")

    logger.info(f"📂 Usando config: {alembic_ini_path}")
    alembic_cfg = Config(alembic_ini_path)
    try:
        logger.info("⚙️  Chamando command.upgrade(alembic_cfg, 'head')...")
        command.upgrade(alembic_cfg, "head")
        logger.info("✅ Migrações do Alembic executadas com sucesso!")
    except Exception as e:
        logger.exception(f"💥 Falha catastrófica nas migrações do Alembic: {e}")
        raise e


def seed_lookup_tables():
    logger.info("📋 Iniciando seed_lookup_tables()...")
    with Session(engine) as session:
        try:
            SQLFaseAnaliticaRepository(session).seed_fases()
            SQLOrgaoLegislativoRepository(session).seed_orgaos()
            logger.info("✅ Tabelas de referência populadas.")
        except Exception as e:
            logger.exception(f"❌ Erro ao popular tabelas de referência: {e}")
            raise e


def seed_bootstrap_baselines():
    logger.info("📊 Iniciando seed_bootstrap_baselines()...")
    # ... (restante do código igual, mas com try/except e logs)
    seed_file_path = os.path.join(
        os.path.dirname(__file__),
        "infrastructure",
        "database",
        "seeds",
        "bootstrap_seeds.sql",
    )
    # ...
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
            logger.error(f"❌ Arquivo de seed não encontrado: {seed_file_path}")
            raise FileNotFoundError(f"Arquivo de seed não encontrado: {seed_file_path}")

    logger.info(f"📜 Lendo arquivo SQL: {seed_file_path}")
    with open(seed_file_path, encoding="utf-8") as f:
        sql_content = f.read()

    with Session(engine) as session:
        try:
            session.execute(text(sql_content))
            session.commit()
            logger.info(
                "✅ Seed de Bootstrap para baseline_tramitacao aplicado com sucesso!"
            )
        except Exception as e:
            session.rollback()
            logger.exception(f"❌ Erro ao aplicar o seed de Bootstrap: {e}")
            raise e


def garantir_integridade_analitica():
    """
    Identifica proposições sem períodos analíticos e reconstrói o estoque.
    Essencial para migração de bases antigas para o modelo R2.
    """
    logger.info("🛠️ Verificando integridade dos dados analíticos...")
    from sqlmodel import select

    with Session(engine) as session:
        try:
            # Busca proposições que não possuem nenhum período cadastrado
            subquery = select(PeriodoFaseModel.proposicao_id)
            statement = select(ProposicaoModel).where(
                ProposicaoModel.id.not_in(subquery)
            )
            props_faltantes = session.exec(statement).all()

            if not props_faltantes:
                logger.info("✅ Todos os dados analíticos estão íntegros.")
                return

            logger.info(
                f"⚠️ Detectadas {len(props_faltantes)} proposições sem períodos analíticos."
            )
            logger.info("🚀 Iniciando reconstrução automática (Self-Healing)...")

            # Inicializa serviços necessários
            periodo_repo = SQLPeriodoFaseRepository(session)
            evento_repo = SQLEventoTramitacaoRepository(session)
            fase_repo = SQLFaseAnaliticaRepository(session)
            prop_repo = SQLProposicaoRepository(session)

            reconstruir_service = ReconstruirPeriodosService(
                periodo_repo, evento_repo, fase_repo, prop_repo
            )

            sucesso_count = 0
            for i, prop in enumerate(props_faltantes):
                try:
                    reconstruir_service.reconstruir_para_proposicao(prop.id)
                    sucesso_count += 1
                    if (i + 1) % 100 == 0:
                        logger.info(
                            f"⏳ Processadas {i + 1} de {len(props_faltantes)}..."
                        )
                except Exception as e:
                    logger.error(f"❌ Falha ao reconstruir proposição {prop.id}: {e}")

            logger.info(
                f"✨ Reconstrução finalizada com sucesso. Total reconstruído: {sucesso_count}/{len(props_faltantes)} itens."
            )
        except Exception as e:
            logger.exception(f"❌ Erro durante verificação de integridade: {e}")


def run():
    logger.info("🚀 [init_db] Iniciando processo de inicialização...")
    run_migrations()
    seed_lookup_tables()
    seed_bootstrap_baselines()
    garantir_integridade_analitica()
    logger.info("✨ [init_db] Inicialização completa!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
