"""
Seed do banco de dados com dados reais das APIs legislativas.

Ordem de execução:
1. Criar tabelas (init_db)
2. Criar usuário demo
3. Seed de fases analíticas (8 registros fixos)
4. Seed de órgãos legislativos (3 registros mínimos)
5. Limpar proposições fora de escopo (apenas PL e PEC)
6. Buscar e inserir/atualizar proposições via adapters
"""

from sqlmodel import text
from infrastructure.adapters.camara_adapter import CamaraAdapter
from infrastructure.adapters.senado_adapter import SenadoAdapter
from infrastructure.database import init_db, get_session
from infrastructure.repositories.sql_proposicao_repository import (
    SQLProposicaoRepository,
)
from infrastructure.repositories.sql_fase_analitica_repository import (
    SQLFaseAnaliticaRepository,
)
from infrastructure.repositories.sql_orgao_legislativo_repository import (
    SQLOrgaoLegislativoRepository,
)
from infrastructure.repositories.sql_evento_tramitacao_repository import (
    SQLEventoTramitacaoRepository,
)
from application.services.listar_movimentacoes_service import ListarMovimentacoesService
from application.services.dashboard_service import DashboardService
from init_db import seed_demo_user


def run() -> None:
    print("Inicializando tabelas e realizando seed com dados reais...")
    init_db()
    seed_demo_user()

    # --- Seed de lookup tables ---
    print("Inserindo fases analíticas...")
    with next(get_session()) as session:
        fase_repo = SQLFaseAnaliticaRepository(session)
        fase_repo.seed_fases()
        fases = fase_repo.buscar_todas()
        print(f"  {len(fases)} fases analíticas no banco.")

    print("Inserindo órgãos legislativos básicos...")
    with next(get_session()) as session:
        orgao_repo = SQLOrgaoLegislativoRepository(session)
        orgao_repo.seed_orgaos()
        print("  Órgãos legislativos básicos inseridos.")

    # --- Limpeza de proposições fora de escopo ---
    print("Limpando dados fora de escopo (apenas PL e PEC são permitidos)...")
    with next(get_session()) as session:
        # Limpar eventos de tramitação de proposições fora de escopo
        session.exec(
            text(
                "DELETE FROM evento_tramitacao WHERE proposicao_id IN "
                "(SELECT id FROM proposicao WHERE tipo NOT IN ('PL', 'PEC'))"
            )
        )
        # Deletar proposições que não são PL ou PEC
        session.exec(text("DELETE FROM proposicao WHERE tipo NOT IN ('PL', 'PEC')"))
        session.commit()

    # --- Busca de proposições via adapters ---
    camara = CamaraAdapter()
    senado = SenadoAdapter()

    print("Obtendo IDs recentes da Câmara (PL e PEC)...")
    ids_camara_pl = camara.listar_recentes("PL", 15)
    ids_camara_pec = camara.listar_recentes("PEC", 10)
    ids_camara = list(set(ids_camara_pl + ids_camara_pec))

    print("Obtendo IDs recentes do Senado (PL e PEC)...")
    ids_senado_pl = senado.listar_recentes("PL", 15)
    ids_senado_pec = senado.listar_recentes("PEC", 10)
    ids_senado = list(set(ids_senado_pl + ids_senado_pec))

    proposicoes = []

    print(f"Buscando detalhes de {len(ids_camara)} proposições na Câmara...")
    for id_p in ids_camara:
        p = camara.buscar_por_id(id_p)
        if p and p.tipo in ["PL", "PEC"]:
            p.atualizar_metricas()
            p.normalizar_campo_status()
            proposicoes.append(p)
            print(f"  [OK] Câmara ID {id_p} - {p.nome_canonico}")

    print(f"Buscando detalhes de {len(ids_senado)} matérias no Senado...")
    for id_p in ids_senado:
        p = senado.buscar_por_id(id_p)
        if p and p.tipo in ["PL", "PEC"]:
            p.atualizar_metricas()
            p.normalizar_campo_status()
            proposicoes.append(p)
            print(f"  [OK] Senado ID {id_p} - {p.nome_canonico}")
    inseridos = 0
    pulados = 0

    print("\nProcessando e salvando proposições...")
    with next(get_session()) as session:
        repo = SQLProposicaoRepository(session)
        evento_repo = SQLEventoTramitacaoRepository(session)
        fase_repo = SQLFaseAnaliticaRepository(session)
        orgao_repo = SQLOrgaoLegislativoRepository(session)
        listar_service = ListarMovimentacoesService(
            evento_repo, repo, fase_repo, orgao_repo, camara, senado
        )
        dashboard_service = DashboardService(repo, evento_repo)

        for p in proposicoes:
            # Gerar ementa resumida se não houver
            if not p.ementa_resumida and p.ementa:
                p.ementa_resumida = (
                    p.ementa[:100] + "..." if len(p.ementa) > 100 else p.ementa
                )

            # Gerar tags simples baseadas no conteúdo (Exemplo)
            if not p.tags or any(t.lower() in ["pl", "pec"] for t in p.tags):
                tags = []
                palavras_chave = [
                    "saúde",
                    "educação",
                    "economia",
                    "tributo",
                    "indígena",
                    "mulher",
                    "segurança",
                    "trabalho",
                    "ambiente",
                ]
                for palavra in palavras_chave:
                    if palavra in p.ementa.lower():
                        tags.append(palavra)

                # Se não achou nenhuma palavra chave, coloca uma tag genérica útil ou deixa vazio
                p.tags = tags[:3]

            prop_db = repo.buscar_por_id(p.id)
            if prop_db is None:
                repo.salvar(p)
                print(f"[INSERT] {p.nome_canonico} (id={p.id})")
                inseridos += 1
                prop_db = p
            else:
                # Se já existe, atualizamos para incluir as novas tags, ementa e status normalizado
                prop_db.ementa_resumida = p.ementa_resumida
                prop_db.tags = p.tags
                prop_db.status = p.status
                prop_db.normalizar_campo_status()
                session.add(prop_db)
                session.commit()
                print(f"[UPDATE] {prop_db.nome_canonico} (id={prop_db.id})")
                pulados += 1

            # --- Etapa Analítica (Duração On-the-fly) ---
            try:
                # 1. Baixa e normaliza os eventos
                eventos = listar_service.executar(str(prop_db.id))

                # 2. Calcula métricas na hora
                tempo = dashboard_service._calcular_tempo_total(
                    eventos, prop_db.tempo_total_dias or 0
                )
                status = dashboard_service._extrair_status_atual(
                    eventos, prop_db.status
                )

                # 3. Atualiza cache da Proposicao para queries rápidas no endpoint de Listagem
                prop_db.tempo_total_dias = tempo
                prop_db.tem_atraso = tempo > 180
                prop_db.status = status
                session.add(prop_db)
                session.commit()
            except Exception as e:
                print(f"  [ERRO] Falha ao sincronizar eventos de {prop_db.id}: {e}")

    # Invalidação do cache após a carga em lote
    print("\nInvalidando cache do dashboard...")
    from infrastructure.cache.redis_client import RedisClient

    try:
        redis_client = RedisClient()
        redis_client.invalidate("dashboard:")
        print("  Cache invalidado com sucesso.")
    except Exception as e:
        print(f"  [AVISO] Falha ao invalidar cache: {e}")

    print(f"\nSeed concluído — inseridos: {inseridos}, atualizados: {pulados}")


if __name__ == "__main__":
    run()
