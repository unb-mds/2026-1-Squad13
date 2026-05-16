import pytest
from src.domain.services.estimativa_aprovacao_service import EstimativaAprovacaoService

@pytest.fixture
def service():
    return EstimativaAprovacaoService()

def test_deve_retornar_dados_insuficientes_quando_abaixo_do_threshold(service):
    # Cenário: 49 proposições (limite é 50)
    historico = [100] * 49
    
    resultado = service.calcular_estimativa(historico)
    
    assert resultado.dias is None
    assert resultado.status == "DADOS_INSUFICIENTES"
    assert resultado.amostra == 49

def test_deve_calcular_media_quando_atinge_threshold_exato(service):
    # Cenário: 50 proposições com 100 dias cada
    historico = [100] * 50
    
    resultado = service.calcular_estimativa(historico)
    
    assert resultado.dias == 100
    assert resultado.status == "CALCULADA"
    assert resultado.amostra == 50

def test_deve_calcular_media_corretamente_com_amostra_variada(service):
    # Cenário: 60 proposições, média 150
    historico = [100] * 30 + [200] * 30
    
    resultado = service.calcular_estimativa(historico)
    
    assert resultado.dias == 150
    assert resultado.amostra == 60
