"""
Seed do banco de dados com dados reais das APIs legislativas.
Versão aprimorada com diversidade histórica (anos variados) e detecção de base já povoada.

Ordem de execução:
1. Criar tabelas e usuário demo (via init_db)
2. Seed de tabelas de lookup (fases e órgãos)
3. Buscar proposições históricas e recentes (Câmara e Senado)
4. Processar eventos de tramitação para gerar massa de dados analítica
"""

import argparse
from sqlmodel import Session, select, func
from infrastructure.adapters.camara_adapter import CamaraAdapter
from infrastructure.adapters.senado_adapter import SenadoAdapter
from infrastructure.database import init_db, get_session, get_redis_connection, engine
from infrastructure.database.models.proposicao_model import ProposicaoModel
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
from infrastructure.repositories.sql_apensamento_repository import (
    SQLApensamentoRepository,
)
from infrastructure.cache.redis_client import RedisClient
from application.services.listar_movimentacoes_service import ListarMovimentacoesService
from application.services.dashboard_service import DashboardService
from init_db import seed_demo_user


def seed_lookup_tables():
    print("📋 Inserindo tabelas de referência...")
    with next(get_session()) as session:
        SQLFaseAnaliticaRepository(session).seed_fases()
        SQLOrgaoLegislativoRepository(session).seed_orgaos()


def get_varied_ids(camara, senado):
    anos = [2021, 2023, 2025, 2026]
    tipos = ["PL", "PEC"]
    qtd_por_lote = 8

    ids_c = []
    ids_s = []

    print(f"🔍 Coletando IDs da Câmara e Senado para os anos {anos}...")
    for ano in anos:
        for tipo in tipos:
            ids_c.extend(camara.listar_recentes(tipo, qtd_por_lote, ano))
            ids_s.extend(senado.listar_recentes(tipo, qtd_por_lote, ano))

    return list(dict.fromkeys(ids_c)), list(dict.fromkeys(ids_s))


def generate_tags(ementa):
    temas = {
        "saúde": ["Saúde", "SUS", "Hospitais"],
        "educação": ["Educação", "Ensino", "Escolas"],
        "economia": ["Economia", "Financeiro", "Mercado"],
        "tribut": ["Tributário", "Impostos", "Fiscomania"],
        "ambiente": ["Meio Ambiente", "Ecologia", "Sustentabilidade"],
        "mulher": ["Direitos Humanos", "Mulheres", "Gênero"],
        "segurança": ["Segurança Pública", "Polícia", "Justiça"],
        "trabalho": ["Trabalhista", "Emprego", "Previdência"],
        "tecnologia": ["Tecnologia", "Digital", "Inovação"],
        "indígena": ["Social", "Indígenas", "Minorias"],
        "agro": ["Agronegócio", "Rural", "Terra"],
    }
    tags = []
    ementa_lower = ementa.lower()
    for chave, valores in temas.items():
        if chave in ementa_lower:
            tags.extend(valores)
    return list(set(tags))[:5] or ["Geral", "Legislativo"]


def run(force=False) -> None:
    print("🚀 Iniciando Seed Estruturado...")

    # 1. Preparação
    init_db()
    seed_demo_user()

    with Session(engine) as session:
        count = session.exec(select(func.count(ProposicaoModel.id))).one()
        if count > 50 and not force:
            print(
                f"✅ O banco já possui {count} proposições. Pulando seed (use --force para atualizar)."
            )
            return

    seed_lookup_tables()

    camara = CamaraAdapter()
    senado = SenadoAdapter()

    # 2. Coleta de IDs
    ids_c, ids_s = get_varied_ids(camara, senado)

    # 3. Busca de detalhes
    proposicoes = []
    print(f"📥 Buscando detalhes de {len(ids_c)} (Câmara) e {len(ids_s)} (Senado)...")

    for id_p in ids_c:
        p = camara.buscar_por_id(id_p)
        if p and p.tipo in ["PL", "PEC"]:
            p.atualizar_metricas()
            p.normalizar_campo_status()
            proposicoes.append(p)

    for id_p in ids_s:
        p = senado.buscar_por_id(id_p)
        if p and p.tipo in ["PL", "PEC"]:
            p.atualizar_metricas()
            p.normalizar_campo_status()
            proposicoes.append(p)

    # 4. Persistência e Processamento Analítico
    inseridos = 0
    atualizados = 0

    print("\n💾 Processando e populando eventos (isso pode levar alguns minutos)...")
    with next(get_session()) as session:
        repo = SQLProposicaoRepository(session)
        evento_repo = SQLEventoTramitacaoRepository(session)
        fase_repo = SQLFaseAnaliticaRepository(session)
        orgao_repo = SQLOrgaoLegislativoRepository(session)
        apensamento_repo = SQLApensamentoRepository(session)

        listar_service = ListarMovimentacoesService(
            evento_repo,
            repo,
            fase_repo,
            orgao_repo,
            camara,
            senado,
            apensamento_repo=apensamento_repo,
        )
        dashboard_service = DashboardService(repo, evento_repo)

        for p in proposicoes:
            try:
                p.tags = generate_tags(p.ementa)
                if not p.ementa_resumida:
                    p.ementa_resumida = (
                        p.ementa[:150] + "..." if len(p.ementa) > 150 else p.ementa
                    )

                prop_db = repo.buscar_por_id(p.id)
                if prop_db is None:
                    prop_db = repo.salvar(p)
                    inseridos += 1
                else:
                    prop_db.ementa_resumida = p.ementa_resumida
                    prop_db.tags = p.tags
                    prop_db.status = p.status
                    prop_db.normalizar_campo_status()
                    repo.salvar(prop_db)
                    atualizados += 1

                # Massa de dados: Eventos
                eventos = listar_service.executar(str(prop_db.id))

                # Atualiza métricas reais baseadas no histórico completo
                tempo = dashboard_service._calcular_tempo_total(eventos, prop_db.tempo_total_dias or 0, prop_db)
                status = dashboard_service._extrair_status_atual(eventos, prop_db.status)

                prop_db.tempo_total_dias = tempo
                prop_db.tem_atraso = (tempo > 180) and (prop_db.data_encerramento is None)
                prop_db.status = status

                repo.salvar(prop_db)

                print(f"  [OK] {p.nome_canonico}", end="\r")

            except Exception as e:
                session.rollback()
                print(f"\n❌ Erro em {p.id}: {str(e)}")

    print(f"\n\n✨ Seed Finalizado! Inseridos: {inseridos}, Atualizados: {atualizados}")

    # 5. Invalidação de Cache
    try:
        redis_conn = get_redis_connection()
        RedisClient(redis_conn).invalidate("dashboard:")
        print("✅ Cache limpo.")
    except Exception:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--force",
        action="store_true",
        help="Força a execução mesmo se o banco já estiver povoado",
    )
    args = parser.parse_args()
    run(force=args.force)
