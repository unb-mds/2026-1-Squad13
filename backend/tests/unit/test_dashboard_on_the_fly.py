import pytest
from datetime import date
from unittest.mock import Mock
from application.services.dashboard_service import DashboardService
from domain.entities.evento_tramitacao import EventoTramitacao
from domain.entities.tipo_evento import TipoEvento

def mock_evento(tipo_evento, data_iso):
    return EventoTramitacao(
        proposicao_id="123",
        data_evento=data_iso,
        sequencia=1,
        sigla_orgao="TEST",
        descricao_original="Teste",
        tipo_evento=tipo_evento,
        deliberativo=False,
        mudou_fase=False,
        mudou_orgao=False,
    )

@pytest.fixture
def service():
    return DashboardService(repository=Mock(), evento_repo=Mock())

def test_calcular_tempo_sem_terminal(service):
    eventos = [
        mock_evento(TipoEvento.APRESENTACAO.value, "2024-01-01T10:00:00"),
        mock_evento(TipoEvento.DESPACHO.value, "2024-01-10T10:00:00"),
    ]
    
    tempo = service._calcular_tempo_total(eventos, 0)
    
    # Diferença de 2024-01-01 até hoje
    inicio = date(2024, 1, 1)
    hoje = date.today()
    esperado = (hoje - inicio).days
    
    assert tempo == esperado

def test_calcular_tempo_com_terminal(service):
    eventos = [
        mock_evento(TipoEvento.APRESENTACAO.value, "2024-01-01T10:00:00"),
        mock_evento(TipoEvento.DESPACHO.value, "2024-01-10T10:00:00"),
        mock_evento(TipoEvento.APROVACAO.value, "2024-02-01T10:00:00"),
    ]
    
    tempo = service._calcular_tempo_total(eventos, 0)
    
    # 2024-01-01 até 2024-02-01 = 31 dias
    assert tempo == 31

def test_calcular_tempo_sem_eventos(service):
    assert service._calcular_tempo_total([], 42) == 42

def test_extrair_status_atual(service):
    eventos = [
        mock_evento(TipoEvento.APRESENTACAO.value, "2024-01-01T10:00:00"),
        mock_evento(TipoEvento.RECEBIMENTO_ORGAO.value, "2024-01-10T10:00:00"),
        mock_evento(TipoEvento.NAO_CLASSIFICADO.value, "2024-01-15T10:00:00"),
    ]
    
    # Deve pegar o retroativo (RECEBIMENTO_ORGAO -> Em Tramitação)
    status = service._extrair_status_atual(eventos, "Fallback")
    assert status == "Em Tramitação"

def test_extrair_status_atual_sem_eventos(service):
    assert service._extrair_status_atual([], "Original") == "Original"
