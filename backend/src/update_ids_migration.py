import logging

from sqlalchemy import create_engine, text

from infrastructure.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def update_proposicoes_ids():
    engine = create_engine(settings.database_url)
    with engine.begin() as conn:
        # Desabilita temporariamente a verificação de chaves estrangeiras no PostgreSQL
        logger.info(
            "Desabilitando temporariamente as restrições de chave estrangeira..."
        )
        conn.execute(text("SET session_replication_role = 'replica';"))

        try:
            logger.info("Atualizando IDs de proposições da Câmara...")
            result_camara = conn.execute(
                text("""
                UPDATE proposicao
                SET id = 'camara:' || id
                WHERE orgao_origem = 'Câmara dos Deputados'
                  AND id NOT LIKE 'camara:%'
                  AND id NOT LIKE 'senado:%';
            """)
            )
            logger.info(f"{result_camara.rowcount} proposições da Câmara atualizadas.")

            logger.info("Atualizando IDs de proposições do Senado...")
            result_senado = conn.execute(
                text("""
                UPDATE proposicao
                SET id = 'senado:' || id
                WHERE orgao_origem = 'Senado Federal'
                  AND id NOT LIKE 'senado:%'
                  AND id NOT LIKE 'camara:%';
            """)
            )
            logger.info(f"{result_senado.rowcount} proposições do Senado atualizadas.")

            logger.info("Atualizando IDs em evento_tramitacao...")
            result_evento = conn.execute(
                text("""
                UPDATE evento_tramitacao
                SET proposicao_id = p.id
                FROM proposicao p
                WHERE evento_tramitacao.proposicao_id = replace(replace(p.id, 'camara:', ''), 'senado:', '')
                  AND (p.id LIKE 'camara:%' OR p.id LIKE 'senado:%')
                  AND evento_tramitacao.proposicao_id NOT LIKE 'camara:%'
                  AND evento_tramitacao.proposicao_id NOT LIKE 'senado:%';
            """)
            )
            logger.info(f"{result_evento.rowcount} eventos atualizados.")

            # Update apensamento (both materia_principal_id and materia_apensada_id)
            logger.info("Atualizando IDs em apensamento (materia_principal_id)...")
            result_apensamento1 = conn.execute(
                text("""
                UPDATE apensamento
                SET materia_principal_id = p.id
                FROM proposicao p
                WHERE apensamento.materia_principal_id = replace(replace(p.id, 'camara:', ''), 'senado:', '')
                  AND (p.id LIKE 'camara:%' OR p.id LIKE 'senado:%')
                  AND apensamento.materia_principal_id NOT LIKE 'camara:%'
                  AND apensamento.materia_principal_id NOT LIKE 'senado:%';
            """)
            )
            logger.info(
                f"{result_apensamento1.rowcount} apensamentos (materia_principal_id) atualizados."
            )

            logger.info("Atualizando IDs em apensamento (materia_apensada_id)...")
            result_apensamento2 = conn.execute(
                text("""
                UPDATE apensamento
                SET materia_apensada_id = p.id
                FROM proposicao p
                WHERE apensamento.materia_apensada_id = replace(replace(p.id, 'camara:', ''), 'senado:', '')
                  AND (p.id LIKE 'camara:%' OR p.id LIKE 'senado:%')
                  AND apensamento.materia_apensada_id NOT LIKE 'camara:%'
                  AND apensamento.materia_apensada_id NOT LIKE 'senado:%';
            """)
            )
            logger.info(
                f"{result_apensamento2.rowcount} apensamentos (materia_apensada_id) atualizados."
            )
        finally:
            logger.info("Reabilitando as restrições de chave estrangeira...")
            conn.execute(text("SET session_replication_role = 'origin';"))


if __name__ == "__main__":
    update_proposicoes_ids()
