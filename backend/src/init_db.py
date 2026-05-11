from infrastructure.database import init_db
from domain.entities.proposicao import Proposicao # Importante importar as entidades para o SQLModel vê-las

def run():
    print("Criando tabelas no banco de dados...")
    init_db()
    print("Tabelas criadas com sucesso!")

if __name__ == "__main__":
    run()
