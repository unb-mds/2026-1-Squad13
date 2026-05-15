from infrastructure.database import init_db, engine
from sqlmodel import Session, select
from domain.entities.user import User
from infrastructure.adapters.security_adapter import get_password_hash

# Importando modelos para registro no metadata
from domain.entities.proposicao import Proposicao  # noqa: F401


def seed_demo_user():
    print("Verificando usuário de demonstração...")
    with Session(engine) as session:
        statement = select(User).where(User.email == "demo@lextrack.gov.br")
        demo_user = session.exec(statement).first()

        if not demo_user:
            print("Criando usuário de demonstração (demo@lextrack.gov.br)...")
            user = User(
                nome="Demo User",
                email="demo@lextrack.gov.br",
                hashed_password=get_password_hash("demo123"),
                perfil="analista",
            )
            session.add(user)
            session.commit()
            print("Usuário de demonstração criado!")
        else:
            print("Usuário de demonstração já existe.")


def run():
    print("Criando tabelas no banco de dados...")
    init_db()
    seed_demo_user()
    print("Tabelas e dados iniciais configurados com sucesso!")


if __name__ == "__main__":
    run()
