"""
Testes de infraestrutura para SQLEventoTramitacaoRepository.

Usa SQLite in-memory para isolamento — padrão já adotado pelo projeto.
Valida insert, batch insert, consulta ordenada, último evento,
deleção seletiva, contagem por tipo e persistência de campos JSON/bool.
"""

import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from domain.entities.evento_tramitacao import EventoTramitacao
from domain.entities.proposicao import Proposicao
from domain.entities.tipo_evento import TipoEvento
from infrastructure.repositories.sql_evento_tramitacao_repository import (
    SQLEventoTramitacaoRepository,
)


@pytest.fixture(name="session")
def session_fixture():
    """Cria banco SQLite in-memory com todas as tabelas."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # Proposição base para FK
        p = Proposicao(
            id="123",
            tipo="PL",
            numero="1",
            ano=2024,
            autor="Test",
            status="Test",
            ementa="Test",
            data_apresentacao="2024-01-01",
            data_ultima_movimentacao="2024-01-01",
            orgao_atual="Test",
            tags=[],
        )
        session.add(p)
        # Segunda proposição para testes de isolamento
        p2 = Proposicao(
            id="456",
            tipo="PEC",
            numero="2",
            ano=2024,
            autor="Test2",
            status="Test",
            ementa="Test2",
            data_apresentacao="2024-01-01",
            data_ultima_movimentacao="2024-01-01",
            orgao_atual="Test",
            tags=[],
        )
        session.add(p2)
        session.commit()
        yield session


def _criar_evento(
    proposicao_id: str = "123",
    data_evento: str = "2024-01-01T10:00",
    sequencia: int = 1,
    sigla_orgao: str = "CCJ",
    descricao: str = "Recebimento",
    tipo_evento: str = TipoEvento.NAO_CLASSIFICADO.value,
    deliberativo: bool = False,
    mudou_fase: bool = False,
    mudou_orgao: bool = False,
) -> EventoTramitacao:
    """Factory de EventoTramitacao para testes."""
    return EventoTramitacao(
        proposicao_id=proposicao_id,
        data_evento=data_evento,
        sequencia=sequencia,
        sigla_orgao=sigla_orgao,
        descricao_original=descricao,
        tipo_evento=tipo_evento,
        deliberativo=deliberativo,
        mudou_fase=mudou_fase,
        mudou_orgao=mudou_orgao,
    )


# --- Testes de inserção ---


def test_salvar_evento_persiste_corretamente(session: Session):
    repo = SQLEventoTramitacaoRepository(session)
    evento = _criar_evento(tipo_evento=TipoEvento.APRESENTACAO.value)

    salvo = repo.salvar(evento)

    assert salvo.evento_id is not None
    assert salvo.proposicao_id == "123"
    assert salvo.tipo_evento == TipoEvento.APRESENTACAO.value
    assert salvo.descricao_original == "Recebimento"


def test_salvar_lote_multiplos_eventos(session: Session):
    repo = SQLEventoTramitacaoRepository(session)
    e1 = _criar_evento(sequencia=1, data_evento="2024-01-01T10:00")
    e2 = _criar_evento(sequencia=2, data_evento="2024-01-01T11:00")
    e3 = _criar_evento(sequencia=3, data_evento="2024-01-02T09:00")

    repo.salvar_lote([e1, e2, e3])

    resultados = repo.buscar_por_proposicao("123")
    assert len(resultados) == 3


# --- Testes de consulta ---


def test_buscar_por_proposicao_ordena_por_data_e_sequencia(session: Session):
    repo = SQLEventoTramitacaoRepository(session)
    # Inserir fora de ordem
    repo.salvar_lote([
        _criar_evento(sequencia=3, data_evento="2024-01-02T09:00"),
        _criar_evento(sequencia=1, data_evento="2024-01-01T10:00"),
        _criar_evento(sequencia=2, data_evento="2024-01-01T11:00"),
    ])

    resultados = repo.buscar_por_proposicao("123")

    assert len(resultados) == 3
    # Ordem: data_evento ASC, sequencia ASC
    assert resultados[0].sequencia == 1
    assert resultados[1].sequencia == 2
    assert resultados[2].sequencia == 3


def test_buscar_por_proposicao_retorna_vazio_se_inexistente(session: Session):
    repo = SQLEventoTramitacaoRepository(session)

    resultados = repo.buscar_por_proposicao("999999")

    assert resultados == []


def test_buscar_ultimo_evento_retorna_mais_recente(session: Session):
    repo = SQLEventoTramitacaoRepository(session)
    repo.salvar_lote([
        _criar_evento(sequencia=1, data_evento="2024-01-01T10:00"),
        _criar_evento(sequencia=2, data_evento="2024-01-02T10:00"),
        _criar_evento(sequencia=3, data_evento="2024-01-03T10:00"),
    ])

    ultimo = repo.buscar_ultimo_evento("123")

    assert ultimo is not None
    assert ultimo.sequencia == 3
    assert ultimo.data_evento == "2024-01-03T10:00"


def test_buscar_ultimo_evento_retorna_none_se_vazio(session: Session):
    repo = SQLEventoTramitacaoRepository(session)

    resultado = repo.buscar_ultimo_evento("999999")

    assert resultado is None


# --- Testes de deleção ---


def test_deletar_por_proposicao_remove_apenas_especifica(session: Session):
    repo = SQLEventoTramitacaoRepository(session)
    # Eventos para prop 123
    repo.salvar_lote([
        _criar_evento(proposicao_id="123", sequencia=1),
        _criar_evento(proposicao_id="123", sequencia=2),
    ])
    # Eventos para prop 456
    repo.salvar_lote([
        _criar_evento(proposicao_id="456", sequencia=1),
    ])

    repo.deletar_por_proposicao("123")

    assert len(repo.buscar_por_proposicao("123")) == 0
    assert len(repo.buscar_por_proposicao("456")) == 1


# --- Testes de contagem ---


def test_contar_por_tipo_agrupa_corretamente(session: Session):
    repo = SQLEventoTramitacaoRepository(session)
    repo.salvar_lote([
        _criar_evento(sequencia=1, tipo_evento=TipoEvento.APRESENTACAO.value),
        _criar_evento(sequencia=2, tipo_evento=TipoEvento.DESPACHO.value),
        _criar_evento(sequencia=3, tipo_evento=TipoEvento.DESPACHO.value),
        _criar_evento(sequencia=4, tipo_evento=TipoEvento.NAO_CLASSIFICADO.value),
    ])

    contagem = repo.contar_por_tipo("123")

    assert contagem[TipoEvento.APRESENTACAO.value] == 1
    assert contagem[TipoEvento.DESPACHO.value] == 2
    assert contagem[TipoEvento.NAO_CLASSIFICADO.value] == 1


# --- Testes de campos especiais ---


def test_payload_bruto_json_persiste_e_recupera(session: Session):
    repo = SQLEventoTramitacaoRepository(session)
    payload = {"id": 123, "descricao": "Teste", "nested": {"key": "value"}}
    evento = _criar_evento()
    evento.payload_bruto = payload

    repo.salvar(evento)

    recuperado = repo.buscar_por_proposicao("123")[0]
    assert recuperado.payload_bruto == payload
    assert recuperado.payload_bruto["nested"]["key"] == "value"


def test_flags_booleanos_persistem(session: Session):
    repo = SQLEventoTramitacaoRepository(session)
    evento = _criar_evento(
        tipo_evento=TipoEvento.VOTACAO_PLENARIO.value,
        deliberativo=True,
        mudou_fase=True,
        mudou_orgao=True,
    )
    evento.remessa_ou_retorno = "REMESSA"

    repo.salvar(evento)

    recuperado = repo.buscar_por_proposicao("123")[0]
    assert recuperado.deliberativo is True
    assert recuperado.mudou_fase is True
    assert recuperado.mudou_orgao is True
    assert recuperado.remessa_ou_retorno == "REMESSA"


def test_evento_terminal_via_property(session: Session):
    """Valida a property eh_evento_terminal definida pelo domínio (A)."""
    repo = SQLEventoTramitacaoRepository(session)

    evento_normal = _criar_evento(
        sequencia=1, tipo_evento=TipoEvento.DESPACHO.value
    )
    evento_terminal = _criar_evento(
        sequencia=2, tipo_evento=TipoEvento.ARQUIVAMENTO.value
    )
    repo.salvar_lote([evento_normal, evento_terminal])

    eventos = repo.buscar_por_proposicao("123")
    assert eventos[0].eh_evento_terminal is False
    assert eventos[1].eh_evento_terminal is True
