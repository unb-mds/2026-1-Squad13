from sqlalchemy import create_engine, text
from infrastructure.config import DATABASE_URL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_proposicoes_ids():
    engine = create_engine(DATABASE_URL)
    with engine.begin() as conn:
        logger.info("Atualizando IDs de proposições da Câmara...")
        result_camara = conn.execute(text("""
            UPDATE proposicao
            SET id = 'camara:' || id
            WHERE orgao_origem = 'Câmara dos Deputados'
              AND id NOT LIKE 'camara:%'
              AND id NOT LIKE 'senado:%';
        """))
        logger.info(f"{result_camara.rowcount} proposições da Câmara atualizadas.")

        logger.info("Atualizando IDs de proposições do Senado...")
        result_senado = conn.execute(text("""
            UPDATE proposicao
            SET id = 'senado:' || id
            WHERE orgao_origem = 'Senado Federal'
              AND id NOT LIKE 'senado:%'
              AND id NOT LIKE 'camara:%';
        """))
        logger.info(f"{result_senado.rowcount} proposições do Senado atualizadas.")

        # Update dependent tables. We need to do this carefully if foreign keys have CASCADE
        # Let's check foreign key constraints first to see if ON UPDATE CASCADE is set.
        # It's better to recreate the foreign keys if we must manually update, but let's assume
        # there might be other tables like evento_tramitacao
        
        logger.info("Atualizando IDs em evento_tramitacao...")
        result_evento = conn.execute(text("""
            UPDATE evento_tramitacao
            SET proposicao_id = p.id
            FROM proposicao p
            WHERE evento_tramitacao.proposicao_id = replace(replace(p.id, 'camara:', ''), 'senado:', '')
              AND (p.id LIKE 'camara:%' OR p.id LIKE 'senado:%')
              AND evento_tramitacao.proposicao_id NOT LIKE 'camara:%'
              AND evento_tramitacao.proposicao_id NOT LIKE 'senado:%';
        """))
        logger.info(f"{result_evento.rowcount} eventos atualizados.")

        # Update apensamento (both proposicao_id and proposicao_apensada_id)
        logger.info("Atualizando IDs em apensamento (proposicao_id)...")
        result_apensamento1 = conn.execute(text("""
            UPDATE apensamento
            SET proposicao_id = p.id
            FROM proposicao p
            WHERE apensamento.proposicao_id = replace(replace(p.id, 'camara:', ''), 'senado:', '')
              AND (p.id LIKE 'camara:%' OR p.id LIKE 'senado:%')
              AND apensamento.proposicao_id NOT LIKE 'camara:%'
              AND apensamento.proposicao_id NOT LIKE 'senado:%';
        """))
        logger.info(f"{result_apensamento1.rowcount} apensamentos (proposicao_id) atualizados.")

        logger.info("Atualizando IDs em apensamento (proposicao_apensada_id)...")
        result_apensamento2 = conn.execute(text("""
            UPDATE apensamento
            SET proposicao_apensada_id = p.id
            FROM proposicao p
            WHERE apensamento.proposicao_apensada_id = replace(replace(p.id, 'camara:', ''), 'senado:', '')
              AND (p.id LIKE 'camara:%' OR p.id LIKE 'senado:%')
              AND apensamento.proposicao_apensada_id NOT LIKE 'camara:%'
              AND apensamento.proposicao_apensada_id NOT LIKE 'senado:%';
        """))
        logger.info(f"{result_apensamento2.rowcount} apensamentos (proposicao_apensada_id) atualizados.")

if __name__ == "__main__":
    update_proposicoes_ids()
