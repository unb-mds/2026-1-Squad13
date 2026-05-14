from infrastructure.adapters.camara_mock_adapter import CamaraMockAdapter
from infrastructure.adapters.senado_mock_adapter import SenadoMockAdapter
from infrastructure.database import init_db, get_session
from infrastructure.repositories.sql_proposicao_repository import SQLProposicaoRepository


def run() -> None:
    print("Inicializando tabelas...")
    init_db()

    proposicoes = CamaraMockAdapter().buscar() + SenadoMockAdapter().buscar()

    inseridos = 0
    pulados = 0

    with next(get_session()) as session:
        repo = SQLProposicaoRepository(session)
        for proposicao in proposicoes:
            if repo.buscar_por_id(proposicao.id) is None:
                repo.salvar(proposicao)
                print(f"[INSERT] {proposicao.nome_canonico} (id={proposicao.id})")
                inseridos += 1
            else:
                print(f"[SKIP]   {proposicao.nome_canonico} (id={proposicao.id})")
                pulados += 1

    print(f"\nSeed concluído — inseridos: {inseridos}, pulados: {pulados}")


if __name__ == "__main__":
    run()
