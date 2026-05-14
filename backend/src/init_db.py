from domain.entities.proposicao import Proposicao  # noqa: F401
from infrastructure.database import init_db

def run():
    print("Criando tabelas no banco de dados...")
    init_db()
    print("Tabelas criadas com sucesso!")

if __name__ == "__main__":
    run()
