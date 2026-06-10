"""
Seed do banco de dados com dados reais das APIs legislativas.
Versão Gap-Filler: Preenchimento dinâmico de buracos + Paralelismo.
"""

import argparse
import asyncio
import logging
import sys
from datetime import datetime

import httpx
from sqlmodel import Session, func, select

import init_db
from application.services.dashboard_service import DashboardService
from application.services.listar_movimentacoes_service import ListarMovimentacoesService
from application.services.reconstruir_periodos_service import ReconstruirPeriodosService
from domain.constants import LIMITE_DIAS_ATRASO
from domain.value_objects.modo_movimentacao import ModoMovimentacao
from infrastructure.adapters.camara_adapter import CamaraAdapter
from infrastructure.adapters.senado_adapter import SenadoAdapter
from infrastructure.cache.redis_client import RedisClient
from infrastructure.database import engine, get_redis_client, get_session
from infrastructure.database.models.proposicao_model import ProposicaoModel
from infrastructure.repositories.sql_apensamento_repository import (
    SQLApensamentoRepository,
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


# Configuração de logging
def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )
    logging.getLogger("httpx").setLevel(logging.INFO)
    logging.getLogger("application.services").setLevel(logging.WARNING)


configure_logging()
logger = logging.getLogger("seed")


def seed_lookup_tables():
    logger.info("📋 Sincronizando tabelas de referência...")
    with next(get_session()) as session:
        SQLFaseAnaliticaRepository(session).seed_fases()
        SQLOrgaoLegislativoRepository(session).seed_orgaos()


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


async def run(sources=None, years=None, types=None, limit=5, tasks=None) -> None:
    """Executa a coleta de dados com lógica de Gap-Filling."""
    sources = sources or ["camara", "senado"]
    years = years or [datetime.now().year]
    types = types or ["PL", "PEC"]

    logger.info("🚀 Iniciando Motor de Ingestão Legislativa (Gap-Filler Mode)...")

    async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
        init_db.run()
        configure_logging()
        seed_lookup_tables()

        camara = CamaraAdapter()
        senado = SenadoAdapter()

        # 2. Construção do Plano de Trabalho Inteligente
        work_plan = tasks or []
        if not work_plan:
            for ano in years:
                for tipo in types:
                    for source in sources:
                        work_plan.append(
                            {
                                "source": source,
                                "year": ano,
                                "type": tipo,
                                "limit": limit,
                            }
                        )

        # 3. Execução Paralela
        sem = asyncio.Semaphore(3)
        all_proposicoes = []

        async def process_task(task):
            async with sem:
                source = task["source"]
                adapter = camara if source == "camara" else senado
                try:
                    # Lógica de Paginação/Offset baseada no que já temos
                    local_offset = task.get("local_count", 0)
                    page = (local_offset // task.get("limit", limit)) + 1

                    logger.info(
                        f"   🔎 Buscando {task['type']} {task['year']} na {source.upper()} (Offset: {local_offset}, Página: {page})..."
                    )

                    if source == "camara":
                        ids = await adapter.listar_recentes(
                            tipo=task["type"],
                            quantidade=task.get("limit", limit),
                            ano=task["year"],
                            client=client,
                            pagina=page,
                        )
                    else:
                        # Senado não tem página, buscamos um pouco mais e filtramos
                        ids_raw = await adapter.listar_recentes(
                            tipo=task["type"],
                            quantidade=task.get("limit", limit) + local_offset + 5,
                            ano=task["year"],
                            client=client,
                        )
                        # Remove os primeiros que provavelmente já temos
                        ids = ids_raw[
                            local_offset : local_offset + task.get("limit", limit)
                        ]

                    batch = []
                    for id_p in ids:
                        try:
                            p = await adapter.buscar_por_id(id_p, client=client)
                            if p:
                                p.atualizar_metricas()
                                p.normalizar_campo_status()
                                batch.append(p)
                        except Exception:
                            continue
                    return batch
                except Exception as e:
                    logger.error(
                        f"   ❌ Erro na {source.upper()} ({task['type']} {task['year']}): {e}"
                    )
                    return []

        results = await asyncio.gather(*(process_task(t) for t in work_plan))
        for batch in results:
            all_proposicoes.extend(batch)

        # 4. Persistência
        if not all_proposicoes:
            logger.warning("🏁 Nenhuma proposição nova identificada.")
            return

        logger.info(f"💾 Processando e analisando {len(all_proposicoes)} itens...")
        inseridos = 0
        atualizados = 0

        with next(get_session()) as session:
            repo = SQLProposicaoRepository(session)
            evento_repo = SQLEventoTramitacaoRepository(session)
            fase_repo = SQLFaseAnaliticaRepository(session)
            orgao_repo = SQLOrgaoLegislativoRepository(session)
            apensamento_repo = SQLApensamentoRepository(session)
            periodo_repo = SQLPeriodoFaseRepository(session)

            reconstruir_service = ReconstruirPeriodosService(
                periodo_repo, evento_repo, fase_repo, repo
            )

            listar_service = ListarMovimentacoesService(
                evento_repo,
                repo,
                fase_repo,
                orgao_repo,
                camara,
                senado,
                apensamento_repo=apensamento_repo,
                reconstruir_service=reconstruir_service,
            )
            dashboard_service = DashboardService(repo, evento_repo)

            for p in all_proposicoes:
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
                        prop_db.status = p.status
                        prop_db.normalizar_campo_status()
                        repo.salvar(prop_db)
                        atualizados += 1

                    eventos = await listar_service.executar(
                        str(prop_db.id), modo=ModoMovimentacao.COMPLETO, client=client
                    )
                    prop_db.tempo_total_dias = dashboard_service._calcular_tempo_total(
                        eventos, prop_db.tempo_total_dias or 0, prop_db
                    )
                    prop_db.status = dashboard_service._extrair_status_atual(
                        eventos, prop_db.status
                    )
                    prop_db.tem_atraso = (
                        prop_db.tempo_total_dias > LIMITE_DIAS_ATRASO
                    ) and (prop_db.data_encerramento is None)
                    repo.salvar(prop_db)
                except Exception as e:
                    logger.error(f"❌ Erro em {p.id}: {e}")

        logger.info(
            f"✨ Ciclo Finalizado! Inseridos: {inseridos}, Atualizados: {atualizados}"
        )
        try:
            # Invalida o cache do dashboard para refletir os novos dados imediatamente
            redis_conn = get_redis_client()
            RedisClient(redis_conn).invalidate("dashboard:")
            logger.info("✅ Cache do dashboard invalidado.")
        except Exception as e:
            logger.warning(f"⚠️ Falha ao invalidar cache: {e}")


async def analyze_database_gaps(sources, years, types):
    """Análise de cobertura avançada."""
    logger.info("🔍 Analisando estado atual do banco...")
    camara = CamaraAdapter()
    senado = SenadoAdapter()
    results = []
    failed_sources = set()

    # Timeout granular: 3s para conectar, 10s total
    timeout_config = httpx.Timeout(10.0, connect=3.0)
    async with httpx.AsyncClient(follow_redirects=True, timeout=timeout_config) as client:
        with Session(engine) as session:
            for ano in sorted(years, reverse=True):
                for tipo in types:
                    for source in sources:
                        if source in failed_sources:
                            continue
                        orgao_nome = (
                            "Câmara dos Deputados"
                            if source == "camara"
                            else "Senado Federal"
                        )
                        local_count = session.exec(
                            select(func.count(ProposicaoModel.id)).where(
                                ProposicaoModel.ano == ano,
                                ProposicaoModel.tipo == tipo,
                                ProposicaoModel.orgao_origem == orgao_nome,
                            )
                        ).one()
                        try:
                            adapter = camara if source == "camara" else senado
                            api_total = await adapter.obter_total(
                                tipo, ano, client=client
                            )
                            # Corrige lógica de 0% ou Erro
                            if api_total == 0 and local_count > 0:
                                coverage = (
                                    100.0  # Provável inconsistência na API ou tipo raro
                                )
                            else:
                                coverage = (
                                    (local_count / api_total * 100)
                                    if api_total > 0
                                    else 0
                                )

                            results.append(
                                {
                                    "ano": ano,
                                    "tipo": tipo,
                                    "fonte": source.upper(),
                                    "local": local_count,
                                    "api": api_total,
                                    "coverage": coverage,
                                    "error": False
                                }
                            )
                        except Exception as e:
                            logger.warning(f"🔌 Fonte {source.upper()} instável ({tipo} {ano}): {str(e) or type(e).__name__}")
                            results.append(
                                {
                                    "ano": ano,
                                    "tipo": tipo,
                                    "fonte": source.upper(),
                                    "local": local_count,
                                    "api": "ERR",
                                    "coverage": 0,
                                    "error": True
                                }
                            )

    if results:
        print("\n" + "=" * 80)
        print(
            f"{'ANO':<6} | {'TIPO':<6} | {'FONTE':<10} | {'LOCAL':<8} | {'API (TOT)':<10} | {'COBERTURA':<10}"
        )
        print("-" * 80)
        for r in sorted(results, key=lambda x: (x["ano"], x["fonte"]), reverse=True):
            if r["error"]:
                status = "❌"
                api_str = "ERROR"
                cov_str = "N/A"
            else:
                status = (
                    "✅" if r["coverage"] >= 80 else "⚠️" if r["coverage"] >= 30 else "🚨"
                )
                if r["api"] == 0 and r["local"] == 0:
                    status = "⚪"  # Sem dados em ambos
                api_str = str(r["api"])
                cov_str = f"{r['coverage']:>8.1f}%"

            print(
                f"{r['ano']:<6} | {r['tipo']:<6} | {r['fonte']:<10} | {r['local']:<8} | {api_str:<10} | {cov_str} {status}"
            )
        print("=" * 80)

    gaps = [r for r in results if not r.get("error") and r["coverage"] < 95 and r["api"] != "ERR" and r["api"] > 0]
    return [
        {
            "source": g["fonte"].lower(),
            "year": g["ano"],
            "type": g["tipo"],
            "local_count": g["local"],
        }
        for g in gaps
    ], failed_sources


async def interactive_menu():
    """Menu Interativo Inteligente."""
    print("\n" + "🏛️  MONITOR LEGISLATIVO - ASSISTENTE DE DADOS".center(60))
    print("=" * 60)

    current_year = datetime.now().year
    default_years = list(range(current_year - 2, current_year + 1))
    gaps, failed = await analyze_database_gaps(
        ["camara", "senado"], default_years, ["PL", "PEC"]
    )

    if gaps:
        print(f"\n💡 Identificamos {len(gaps)} buracos de cobertura.")
        if (
            input(
                "> Deseja que eu preencha esses buracos automaticamente? (S/n): "
            ).lower()
            != "n"
        ):
            limit = int(input("> Quantos itens novos por buraco? [15]: ") or "15")
            for g in gaps:
                g["limit"] = limit
            return None, None, None, None, gaps

    print("\n--- CONFIGURAÇÃO MANUAL ---")
    sources = ["camara", "senado"]
    if failed:
        sources = [s for s in sources if s not in failed]
    y_str = input(f"> Anos [2000-{current_year}]: ").strip()
    years = (
        [int(y) for y in y_str.split()]
        if y_str
        else list(range(2000, current_year + 1))
    )
    types = (input("> Tipos [PL PEC]: ") or "PL PEC").upper().split()
    limit = int(input("> Limite por lote? [10]: ") or "10")
    return sources, years, types, limit, None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor Legislativo - Seed Tool")
    parser.add_argument("--source", choices=["camara", "senado", "ambos"], help="Fonte")
    parser.add_argument("--limit", type=int, help="Limite")
    parser.add_argument("--years", type=int, nargs="+", help="Anos")
    parser.add_argument("--types", type=str, nargs="+", help="Tipos")
    args = parser.parse_args()

    async def main():
        if not args.source:
            sources, years, types, limit, tasks = await interactive_menu()
        else:
            sources = ["camara", "senado"] if args.source == "ambos" else [args.source]
            years = args.years or [datetime.now().year]
            types = args.types or ["PL", "PEC"]
            limit = args.limit or 5
            tasks = None
        await run(sources=sources, years=years, types=types, limit=limit, tasks=tasks)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        logger.exception(f"💥 Erro fatal: {e}")
        sys.exit(1)
