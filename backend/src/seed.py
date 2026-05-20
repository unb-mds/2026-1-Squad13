"""
Seed do banco de dados com dados reais das APIs legislativas.
Versão inteligente com Menu Interativo e controle total.
"""

import argparse
import asyncio
import logging
import sys
from typing import List
import httpx
from sqlmodel import Session, select, func

from infrastructure.adapters.camara_adapter import CamaraAdapter
from infrastructure.adapters.senado_adapter import SenadoAdapter
from infrastructure.database import init_db, get_session, get_redis_client, engine
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
from domain.constants import LIMITE_DIAS_ATRASO
from init_db import seed_demo_user

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("seed")


def seed_lookup_tables():
    logger.info("📋 Inserindo tabelas de referência (Fases e Órgãos)...")
    with next(get_session()) as session:
        SQLFaseAnaliticaRepository(session).seed_fases()
        SQLOrgaoLegislativoRepository(session).seed_orgaos()


async def get_varied_ids(
    camara: CamaraAdapter,
    senado: SenadoAdapter,
    client: httpx.AsyncClient,
    sources: List[str],
    years: List[int],
    types: List[str],
    limit_per_batch: int,
):
    logger.info(
        f"🔍 Coletando IDs (Fontes: {sources}, Anos: {years}, Tipos: {types})..."
    )

    sem_c = asyncio.Semaphore(4)
    sem_s = asyncio.Semaphore(1)

    async def sem_listar_c(t, q, a):
        async with sem_c:
            return await camara.listar_recentes(t, q, a, client=client)

    async def sem_listar_s(t, q, a):
        async with sem_s:
            return await senado.listar_recentes(t, q, a, client=client)

    tasks_c = []
    tasks_s = []

    for ano in years:
        for tipo in types:
            if "camara" in sources:
                tasks_c.append(sem_listar_c(tipo, limit_per_batch, ano))
            if "senado" in sources:
                tasks_s.append(sem_listar_s(tipo, 1 if limit_per_batch > 1 else 1, ano))

    try:
        logger.info("⏳ Aguardando respostas das APIs...")
        results_c = await asyncio.gather(*tasks_c) if tasks_c else []
        results_s = await asyncio.gather(*tasks_s) if tasks_s else []
    except Exception as e:
        logger.error(f"❌ Falha na coleta inicial de IDs: {e}")
        return [], []

    ids_c = [id_p for sublist in results_c for id_p in sublist]
    ids_s = [id_p for sublist in results_s for id_p in sublist]

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
    ementa_lower = (ementa or "").lower()
    for chave, valores in temas.items():
        if chave in ementa_lower:
            tags.extend(valores)
    return list(set(tags))[:5] or ["Geral", "Legislativo"]


async def run(force=False, sources=None, years=None, types=None, limit=5) -> None:
    sources = sources or ["camara"]
    years = years or [2025, 2026]
    types = types or ["PL", "PEC"]

    logger.info(f"🚀 Iniciando Seed (Fontes: {sources}, Limite: {limit})...")

    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        # 1. Preparação
        init_db()
        seed_demo_user()

        with Session(engine) as session:
            count = session.exec(select(func.count(ProposicaoModel.id))).one()
            if count > 500 and not force:
                logger.info(f"✅ O banco já possui {count} proposições. Pulando seed.")
                return

        seed_lookup_tables()

        camara = CamaraAdapter()
        senado = SenadoAdapter()

        # 2. Coleta de IDs
        ids_c, ids_s = await get_varied_ids(
            camara, senado, client, sources, years, types, limit
        )

        # 3. Busca de detalhes
        proposicoes = []

        if ids_c:
            logger.info(
                f"📥 Buscando detalhes de {len(ids_c)} proposições da Câmara..."
            )
            for id_p in ids_c:
                try:
                    p = await camara.buscar_por_id(id_p, client=client)
                    if p and p.tipo in types:
                        p.atualizar_metricas()
                        p.normalizar_campo_status()
                        proposicoes.append(p)
                except Exception as e:
                    logger.warning(f"⚠️ Erro Câmara ID {id_p}: {e}")

        if ids_s:
            logger.info(
                f"📥 Buscando detalhes de {len(ids_s)} proposições do Senado..."
            )
            senado_errors = 0
            for id_p in ids_s:
                if senado_errors >= 3:
                    logger.error("🚫 Muitos erros no Senado. Pulando restante.")
                    break
                try:
                    p = await senado.buscar_por_id(id_p, client=client)
                    if p and p.tipo in types:
                        p.atualizar_metricas()
                        p.normalizar_campo_status()
                        proposicoes.append(p)
                    else:
                        senado_errors += 1
                except Exception as e:
                    senado_errors += 1
                    logger.warning(f"⚠️ Erro Senado ID {id_p}: {e}")

        # 4. Persistência e Processamento
        inseridos = 0
        atualizados = 0

        if not proposicoes:
            logger.warning("⚠️ Nenhuma proposição coletada.")
            return

        logger.info(f"💾 Processando {len(proposicoes)} itens...")
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
                            p.ementa[:150] + "..."
                            if p.ementa and len(p.ementa) > 150
                            else p.ementa
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
                    eventos = await listar_service.executar(str(prop_db.id), client=client)

                    # Atualiza métricas reais baseadas no histórico completo
                    tempo = dashboard_service._calcular_tempo_total(
                        eventos, prop_db.tempo_total_dias or 0, prop_db
                    )
                    status = dashboard_service._extrair_status_atual(
                        eventos, prop_db.status
                    )

                    prop_db.tempo_total_dias = tempo
                    prop_db.tem_atraso = (tempo > LIMITE_DIAS_ATRASO) and (
                        prop_db.data_encerramento is None
                    )
                    prop_db.status = status

                    repo.salvar(prop_db)

                    if (inseridos + atualizados) % 5 == 0:
                        print(
                            f"  [Progress] {inseridos + atualizados}/{len(proposicoes)}... (OK: {p.nome_canonico})",
                            end="\r",
                        )

                except Exception as e:
                    session.rollback()
                    logger.error(f"❌ Erro em {p.id}: {e}")

        logger.info(
            f"\n✨ Finalizado! Inseridos: {inseridos}, Atualizados: {atualizados}"
        )

        try:
            redis_conn = get_redis_client()
            RedisClient(redis_conn).invalidate("dashboard:")
            logger.info("✅ Cache limpo.")
        except Exception:
            pass


def interactive_menu():
    """Exibe um menu interativo no terminal."""
    print("\n" + "=" * 40)
    print(" 🏛️  MONITOR LEGISLATIVO - SEED TOOL")
    print("=" * 40)

    print("\n1. Escolha a FONTE dos dados:")
    print("   [1] Câmara dos Deputados (Rápida)")
    print("   [2] Senado Federal (Lenta/Instável)")
    print("   [3] Ambos")
    choice = input("\n> Opção [1]: ") or "1"

    sources = ["camara"]
    if choice == "2":
        sources = ["senado"]
    elif choice == "3":
        sources = ["camara", "senado"]

    print("\n2. Escolha o LIMITE de proposições por lote:")
    limit = int(input("> Limite [5]: ") or "5")

    print("\n3. Escolha os ANOS (separados por espaço):")
    years_str = input("> Anos [2025 2026]: ") or "2025 2026"
    years = [int(y) for y in years_str.split()]

    print("\n4. Escolha os TIPOS (separados por espaço):")
    types_str = input("> Tipos [PL PEC]: ") or "PL PEC"
    types = [t.upper() for t in types_str.split()]

    print("\n" + "-" * 40)
    print(f"Configuração: {sources} | Anos: {years} | Tipos: {types} | Limite: {limit}")
    confirm = input("Confirmar execução? (S/n): ").lower()

    if confirm == "n":
        print("Operação cancelada.")
        sys.exit(0)

    return sources, years, types, limit


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script de Seed Inteligente")
    parser.add_argument("--force", action="store_true", help="Força execução")
    parser.add_argument("--source", choices=["camara", "senado", "ambos"], help="Fonte")
    parser.add_argument("--limit", type=int, help="Limite")
    parser.add_argument("--years", type=int, nargs="+", help="Anos")
    parser.add_argument("--types", type=str, nargs="+", help="Tipos")

    args = parser.parse_args()

    # Se não passou argumentos de fonte, abre o menu
    if not args.source:
        sources, years, types, limit = interactive_menu()
    else:
        sources = ["camara", "senado"] if args.source == "ambos" else [args.source]
        years = args.years or [2025, 2026]
        types = args.types or ["PL", "PEC"]
        limit = args.limit or 5

    try:
        asyncio.run(
            run(
                force=args.force, sources=sources, years=years, types=types, limit=limit
            )
        )
    except KeyboardInterrupt:
        logger.info("\n🛑 Seed interrompido.")
        sys.exit(0)
