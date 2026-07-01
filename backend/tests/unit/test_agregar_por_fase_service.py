from datetime import date
from unittest.mock import MagicMock

from application.services.agregar_por_fase_service import AgregarPorFaseService
from domain.entities.evento_tramitacao import EventoTramitacao
from domain.entities.fase_analitica import FaseAnalitica
from domain.entities.tipo_evento import TipoEvento

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fase(
    id: int,
    codigo: str = "ANALISE_COMISSOES",
    nome: str = "Análise em comissões",
    ordem: int = 2,
) -> FaseAnalitica:
    f = FaseAnalitica(codigo=codigo, nome=nome, ordem_logica=ordem)
    f.id = id
    return f


def _repo(*fases) -> MagicMock:
    repo = MagicMock()
    repo.buscar_todas.return_value = list(fases)
    return repo


def _evento(
    seq: int,
    data: str,
    fase_id=None,
    relevante: bool = False,
) -> EventoTramitacao:
    return EventoTramitacao(
        proposicao_id="1",
        data_evento=data,
        sequencia=seq,
        sigla_orgao="CCJ",
        descricao_original="Teste",
        tipo_evento=TipoEvento.NAO_CLASSIFICADO.value,
        deliberativo=False,
        mudou_fase=False,
        mudou_orgao=False,
        fase_analitica_id=fase_id,
        relevante=relevante,
    )


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------


def test_lista_vazia_retorna_lista_vazia():
    service = AgregarPorFaseService(_repo())
    assert service.executar([]) == []


def test_sequencia_simples_duas_fases():
    fase1 = _fase(1, "PROTOCOLO_INICIAL", "Protocolo inicial", 1)
    fase2 = _fase(2, "ANALISE_COMISSOES", "Análise em comissões", 2)
    service = AgregarPorFaseService(_repo(fase1, fase2))

    periodos = service.executar(
        [
            _evento(1, "2024-01-01", fase_id=1),
            _evento(2, "2024-02-01", fase_id=2),
        ]
    )

    assert len(periodos) == 2
    assert periodos[0].fase_codigo == "PROTOCOLO_INICIAL"
    assert periodos[0].data_entrada == date(2024, 1, 1)
    assert periodos[0].data_saida == date(2024, 2, 1)
    assert periodos[0].dias_corridos == 31
    assert periodos[1].fase_codigo == "ANALISE_COMISSOES"
    assert periodos[1].data_saida is None


def test_fase_ativa_sem_data_saida():
    service = AgregarPorFaseService(_repo(_fase(1)))
    periodos = service.executar([_evento(1, "2024-01-01", fase_id=1)])

    assert len(periodos) == 1
    assert periodos[0].data_saida is None
    assert periodos[0].dias_corridos == (date.today() - date(2024, 1, 1)).days


def test_eventos_sem_fase_analitica_ignorados():
    # Eventos com fase_analitica_id=None sem período anterior são descartados.
    service = AgregarPorFaseService(_repo())
    eventos = [
        _evento(1, "2024-01-01", fase_id=None),
        _evento(2, "2024-02-01", fase_id=None),
    ]
    assert service.executar(eventos) == []


def test_acumula_apenas_eventos_relevantes():
    service = AgregarPorFaseService(_repo(_fase(1)))
    eventos = [
        _evento(1, "2024-01-01", fase_id=1, relevante=True),
        _evento(2, "2024-01-15", fase_id=1, relevante=False),
        _evento(3, "2024-02-01", fase_id=1, relevante=True),
    ]
    periodos = service.executar(eventos)

    assert len(periodos) == 1
    assert len(periodos[0].eventos_relevantes) == 2
    assert periodos[0].eventos_relevantes[0].sequencia == 1
    assert periodos[0].eventos_relevantes[1].sequencia == 3


def test_suavizacao_fase_encerrada_mesmo_dia():
    fase1 = _fase(1, "ATIVO", "Ativo", 1)
    fase8 = _fase(8, "ENCERRADA", "Encerrada", 8)
    service = AgregarPorFaseService(_repo(fase1, fase8))

    # Se temos uma fase 8 seguida de uma fase 1 no mesmo dia,
    # a fase 8 deve ser suavizada (não deve mudar para 8).
    eventos = [
        _evento(1, "2024-01-01T10:00:00", fase_id=8),
        _evento(2, "2024-01-01T11:00:00", fase_id=1),
    ]
    periodos = service.executar(eventos)

    # Deve ter apenas um período (fase 1)
    assert len(periodos) == 1
    assert periodos[0].fase_codigo == "ATIVO"
