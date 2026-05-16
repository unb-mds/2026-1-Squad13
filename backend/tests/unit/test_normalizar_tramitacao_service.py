import pytest
from unittest.mock import Mock, MagicMock
from application.services.normalizar_tramitacao_service import NormalizarTramitacaoService
from domain.entities.tipo_evento import TipoEvento
from domain.entities.orgao_legislativo import CasaLegislativa

@pytest.fixture
def mocks():
    return {
        "fase_repo": MagicMock(),
        "orgao_repo": MagicMock(),
    }

def _fase_mock(codigo, id):
    f = Mock()
    f.codigo = codigo
    f.id = id
    return f

@pytest.fixture
def service(mocks):
    # Setup the fase_repo to return known phases
    mocks["fase_repo"].buscar_todas.return_value = [
        _fase_mock("PROTOCOLO_INICIAL", 1),
        _fase_mock("ANALISE_COMISSOES", 2),
        _fase_mock("DELIBERACAO_PLENARIO", 3),
        _fase_mock("ENCERRADA", 4),
    ]
    return NormalizarTramitacaoService(
        fase_repo=mocks["fase_repo"],
        orgao_repo=mocks["orgao_repo"],
        casa_padrao=CasaLegislativa.CAMARA,
    )

def test_normalizar_mantem_cronologia_e_fase(service, mocks):
    dados_brutos = [
        {
            "data_hora": "2024-01-01T10:00:00",
            "sequencia": 1,
            "sigla_orgao": "MESA",
            "descricao": "Apresentação do Projeto de Lei",
            "payload_bruto": {"raw": 1}
        },
        {
            "data_hora": "2024-01-02T10:00:00",
            "sequencia": 2,
            "sigla_orgao": "CCJ",
            "descricao": "Recebimento na Comissão",
            "payload_bruto": {"raw": 2}
        },
        {
            "data_hora": "2024-01-03T10:00:00",
            "sequencia": 3,
            "sigla_orgao": "CCJ",
            "descricao": "Parecer do relator aprovado",
            "payload_bruto": {"raw": 3}
        }
    ]

    eventos = service.normalizar("PL-123", dados_brutos)

    assert len(eventos) == 3
    
    # Evento 1: Apresentação
    assert eventos[0].tipo_evento == TipoEvento.APRESENTACAO.value
    assert eventos[0].fase_analitica_id == 1  # APRESENTACAO
    assert eventos[0].mudou_fase is False     # primeira fase
    assert eventos[0].mudou_orgao is False

    # Evento 2: Recebimento Órgão
    assert eventos[1].tipo_evento == TipoEvento.RECEBIMENTO_ORGAO.value
    assert eventos[1].fase_analitica_id == 2  # ANALISE_COMISSOES
    assert eventos[1].mudou_fase is True      # Mudou de 1 para 2
    assert eventos[1].mudou_orgao is True     # Mudou de MESA para CCJ

    # Evento 3: Parecer / Aprovação
    assert eventos[2].tipo_evento == TipoEvento.PARECER.value
    assert eventos[2].fase_analitica_id == 2  # Continua em ANALISE_COMISSOES
    assert eventos[2].mudou_fase is False
    assert eventos[2].mudou_orgao is False

    # Verifica se fez upsert de órgãos (MESA, CCJ) - como tem cache, são apenas 2 chamadas
    assert mocks["orgao_repo"].buscar_ou_criar.call_count == 2
    mocks["orgao_repo"].buscar_ou_criar.assert_any_call(sigla="MESA", casa=CasaLegislativa.CAMARA)
    mocks["orgao_repo"].buscar_ou_criar.assert_any_call(sigla="CCJ", casa=CasaLegislativa.CAMARA)

def test_normalizar_nao_classificado_preserva_fase(service, mocks):
    dados_brutos = [
        {
            "data_hora": "2024-01-01",
            "sequencia": 1,
            "sigla_orgao": "PLEN",
            "descricao": "Apresentação"
        },
        {
            "data_hora": "2024-01-02",
            "sequencia": 2,
            "sigla_orgao": "PLEN",
            "descricao": "Texto esquisito sem match"
        }
    ]

    eventos = service.normalizar("PL-123", dados_brutos)

    # Evento 1 está na fase APRESENTACAO (id=1)
    assert eventos[0].tipo_evento == TipoEvento.APRESENTACAO.value
    assert eventos[0].fase_analitica_id == 1

    # Evento 2 deve ser NAO_CLASSIFICADO e herdar a fase id=1 do evento anterior
    assert eventos[1].tipo_evento == TipoEvento.NAO_CLASSIFICADO.value
    assert eventos[1].fase_analitica_id == 1
    assert eventos[1].mudou_fase is False
