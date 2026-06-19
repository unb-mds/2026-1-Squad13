import pytest
from sqlmodel import Session, SQLModel, create_engine, select

from domain.entities.proposicao import Proposicao
from infrastructure.database.models.proposicao_model import ProposicaoModel
from infrastructure.repositories.sql_proposicao_repository import (
    SQLProposicaoRepository,
)


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


def test_upsert_em_lote_idempotencia(session):
    repo = SQLProposicaoRepository(session)

    prop1 = Proposicao(
        id="1",
        tipo="PL",
        numero="100",
        ano=2024,
        autor="Autor A",
        ementa="Ementa A",
        data_apresentacao="2024-01-01",
        orgao_origem="Câmara",
        status="Ativo",
        orgao_atual="Câmara",
        link_oficial="link",
        data_ultima_movimentacao="2024-01-01",
    )

    # 1. Primeiro insert
    repo.upsert_em_lote_por_numero_canonico([prop1])

    saved = repo.buscar_por_codigo("PL", "100", 2024)
    assert saved is not None
    assert saved.autor == "Autor A"

    # 2. Update via upsert (mesma chave canônica, autor diferente)
    prop1_mod = prop1.model_copy(update={"autor": "Autor B", "ementa": "Ementa B"})
    repo.upsert_em_lote_por_numero_canonico([prop1_mod])

    session.expire_all()
    updated = repo.buscar_por_codigo("PL", "100", 2024)
    assert updated.autor == "Autor B"
    assert updated.ementa == "Ementa B"
    assert updated.id == saved.id  # ID deve ser mantido


def test_upsert_em_lote_multiplos(session):
    repo = SQLProposicaoRepository(session)

    props = [
        Proposicao(
            id="1",
            tipo="PL",
            numero="101",
            ano=2024,
            autor="A1",
            ementa="E1",
            data_apresentacao="2024-01-01",
            orgao_origem="C",
            status="S",
            orgao_atual="O",
            link_oficial="L",
            data_ultima_movimentacao="D",
        ),
        Proposicao(
            id="2",
            tipo="PEC",
            numero="1",
            ano=2024,
            autor="A2",
            ementa="E2",
            data_apresentacao="2024-01-01",
            orgao_origem="S",
            status="S",
            orgao_atual="O",
            link_oficial="L",
            data_ultima_movimentacao="D",
        ),
    ]

    repo.upsert_em_lote_por_numero_canonico(props)

    assert len(session.exec(select(ProposicaoModel)).all()) == 2
    assert repo.buscar_por_codigo("PL", "101", 2024) is not None
    assert repo.buscar_por_codigo("PEC", "1", 2024) is not None


def test_upsert_em_lote_case_insensitivity(session):
    repo = SQLProposicaoRepository(session)

    prop = Proposicao(
        id="1",
        tipo="pl",
        numero="200",
        ano=2024,
        autor="A",
        ementa="E",
        data_apresentacao="2024-01-01",
        orgao_origem="C",
        status="S",
        orgao_atual="O",
        link_oficial="L",
        data_ultima_movimentacao="D",
    )
    repo.upsert_em_lote_por_numero_canonico([prop])

    # Busca com CAPS diferente deve funcionar tanto no repo quanto no upsert interno
    prop_caps = prop.model_copy(update={"tipo": "PL", "autor": "Novo Autor"})
    repo.upsert_em_lote_por_numero_canonico([prop_caps])

    session.expire_all()
    saved = repo.buscar_por_codigo("pL", "200", 2024)
    assert saved.autor == "Novo Autor"
    assert len(session.exec(select(ProposicaoModel)).all()) == 1


def test_upsert_em_lote_diferentes_casas_preserva_origem(session):
    repo = SQLProposicaoRepository(session)

    # 1. Insere proposição iniciada na Câmara pós-2019
    prop_camara = Proposicao(
        id="camara:50",
        tipo="PL",
        numero="50",
        ano=2020,
        autor="Deputado Iniciador",
        ementa="Ementa da Câmara",
        data_apresentacao="2020-05-10",
        orgao_origem="Câmara dos Deputados",
        status="Em Tramitação",
        orgao_atual="Câmara dos Deputados",
        link_oficial="link-camara",
        data_ultima_movimentacao="2020-05-10",
    )
    repo.upsert_em_lote_por_numero_canonico([prop_camara])

    # 2. Insere proposição do Senado com mesma chave canônica (PL 50/2020)
    # Simula a coleta do Senado que é a casa revisora
    prop_senado = Proposicao(
        id="senado:888",
        tipo="PL",
        numero="50",
        ano=2020,
        autor="Senador Relator",
        ementa="Ementa do Senado que revisa a matéria",
        data_apresentacao="2020-08-15",
        orgao_origem="Senado Federal",
        status="Aprovada",
        orgao_atual="Senado Federal",
        link_oficial="link-senado",
        data_ultima_movimentacao="2020-08-15",
    )
    repo.upsert_em_lote_por_numero_canonico([prop_senado])

    session.expire_all()
    saved = repo.buscar_por_codigo("PL", "50", 2020)

    assert saved is not None
    # ID e metadados de origem da casa iniciadora devem ser preservados
    assert saved.id == "camara:50"
    assert saved.orgao_origem == "Câmara dos Deputados"
    assert saved.autor == "Deputado Iniciador"
    assert saved.data_apresentacao == "2020-05-10"

    # Metadados mutáveis de andamento atual devem ser atualizados
    assert saved.orgao_atual == "Senado Federal"
    assert saved.status == "Aprovada"
    assert saved.data_ultima_movimentacao == "2020-08-15"
    assert len(session.exec(select(ProposicaoModel)).all()) == 1


def test_upsert_em_lote_pre_2019_nao_colide(session):
    repo = SQLProposicaoRepository(session)

    # Inserção de duas matérias com mesma sigla/número/ano anteriores a 2019
    # que nasceram em casas diferentes (Devem ser salvas como registros distintos)
    prop1 = Proposicao(
        id="camara:100",
        tipo="PL",
        numero="100",
        ano=2015,
        autor="Deputado Antigo",
        ementa="Ementa da Câmara de 2015",
        data_apresentacao="2015-01-01",
        orgao_origem="Câmara dos Deputados",
        status="Arquivada",
        orgao_atual="Câmara dos Deputados",
        link_oficial="link-camara",
        data_ultima_movimentacao="2015-01-01",
    )
    prop2 = Proposicao(
        id="senado:200",
        tipo="PL",
        numero="100",
        ano=2015,
        autor="Senador Antigo",
        ementa="Ementa do Senado de 2015",
        data_apresentacao="2015-02-02",
        orgao_origem="Senado Federal",
        status="Arquivada",
        orgao_atual="Senado Federal",
        link_oficial="link-senado",
        data_ultima_movimentacao="2015-02-02",
    )

    repo.upsert_em_lote_por_numero_canonico([prop1, prop2])

    session.expire_all()
    props_no_banco = session.exec(select(ProposicaoModel)).all()

    # Devem coexistir duas linhas físicas no banco de dados
    assert len(props_no_banco) == 2

    # Busca por código direta em ano anterior a 2019 pode colidir se a assinatura do método busca sem órgão de origem.
    # Mas no banco as duas devem coexistir. Vamos validar por ID.
    p1 = repo.buscar_por_id("camara:100")
    p2 = repo.buscar_por_id("senado:200")

    assert p1 is not None
    assert p2 is not None
    assert p1.autor == "Deputado Antigo"
    assert p2.autor == "Senador Antigo"


def test_upsert_em_lote_mesmo_id_orgao_diferente(session):
    repo = SQLProposicaoRepository(session)

    # 1. Primeiro insert com orgao_origem = "Câmara dos Deputados" e ID "camara:169655"
    prop1 = Proposicao(
        id="camara:169655",
        tipo="PEC",
        numero="468",
        ano=1997,
        autor="Autor A",
        ementa="Ementa A",
        data_apresentacao="1997-05-06",
        orgao_origem="Câmara dos Deputados",
        status="Ativo",
        orgao_atual="Mesa",
        link_oficial="link",
        data_ultima_movimentacao="1997-05-06",
    )
    repo.upsert_em_lote_por_numero_canonico([prop1])

    # 2. Segundo insert via upsert com o mesmo ID "camara:169655", mas orgao_origem = "Mesa"
    # Como o orgao_origem é diferente e o ano < 2019, a chave composta seria diferente,
    # mas o ID é idêntico. O repositório deve atualizar o registro sem erro de UniqueViolation.
    prop1_mod = prop1.model_copy(update={"orgao_origem": "Mesa", "autor": "Autor B"})
    repo.upsert_em_lote_por_numero_canonico([prop1_mod])

    session.expire_all()
    saved = repo.buscar_por_id("camara:169655")
    assert saved is not None
    assert saved.orgao_origem == "Mesa"
    assert saved.autor == "Autor B"
    assert len(session.exec(select(ProposicaoModel)).all()) == 1
