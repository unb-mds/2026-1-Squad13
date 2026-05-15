from sqlmodel import text
from infrastructure.adapters.camara_adapter import CamaraAdapter
from infrastructure.adapters.senado_adapter import SenadoAdapter
from infrastructure.database import init_db, engine, get_session
from infrastructure.repositories.sql_proposicao_repository import SQLProposicaoRepository
from init_db import seed_demo_user


def run() -> None:
    print("Inicializando tabelas e realizando seed com dados reais...")
    init_db()
    seed_demo_user()

    print("Limpando dados fora de escopo (apenas PL e PEC são permitidos)...")
    with next(get_session()) as session:
        # Deletar tramitações de proposições que não são PL ou PEC
        session.exec(text("DELETE FROM tramitacao WHERE proposicao_id IN (SELECT id FROM proposicao WHERE tipo NOT IN ('PL', 'PEC'))"))
        # Deletar proposições que não são PL ou PEC
        session.exec(text("DELETE FROM proposicao WHERE tipo NOT IN ('PL', 'PEC')"))
        session.commit()

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
        for p in proposicoes:
            # Gerar ementa resumida se não houver
            if not p.ementa_resumida and p.ementa:
                p.ementa_resumida = p.ementa[:100] + "..." if len(p.ementa) > 100 else p.ementa

            # Gerar tags simples baseadas no conteúdo (Exemplo)
            if not p.tags or any(t.lower() in ['pl', 'pec'] for t in p.tags):
                tags = []
                palavras_chave = ["saúde", "educação", "economia", "tributo", "indígena", "mulher", "segurança", "trabalho", "ambiente"]
                for palavra in palavras_chave:
                    if palavra in p.ementa.lower():
                        tags.append(palavra)
                
                # Se não achou nenhuma palavra chave, coloca uma tag genérica útil ou deixa vazio
                p.tags = tags[:3]

            if repo.buscar_por_id(p.id) is None:
                repo.salvar(p)
                print(f"[INSERT] {p.nome_canonico} (id={p.id})")
                inseridos += 1
            else:
                # Se já existe, atualizamos para incluir as novas tags, ementa e status normalizado
                existente = repo.buscar_por_id(p.id)
                existente.ementa_resumida = p.ementa_resumida
                existente.tags = p.tags
                existente.status = p.status
                existente.normalizar_campo_status()
                session.add(existente)
                session.commit()
                print(f"[UPDATE] {p.nome_canonico} (id={p.id})")
                pulados += 1

    print(f"\nSeed concluído — inseridos: {inseridos}, atualizados: {pulados}")


if __name__ == "__main__":
    run()
