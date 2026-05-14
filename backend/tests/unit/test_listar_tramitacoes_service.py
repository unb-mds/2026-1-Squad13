import pytest
from unittest.mock import Mock
from application.services.listar_tramitacoes_service import ListarTramitacoesService
from domain.entities.tramitacao import Tramitacao

@pytest.fixture
def mocks():
    return {
        "tram_repo": Mock(),
        "prop_repo": Mock(),
        "camara_adapter": Mock(),
        "senado_adapter": Mock()
    }

@pytest.fixture
def service(mocks):
    return ListarTramitacoesService(
        mocks["tram_repo"],
        mocks["prop_repo"],
        mocks["camara_adapter"],
        mocks["senado_adapter"]
    )

def test_listar_tramitacoes_fallback_camara_sucesso(service, mocks):
    # Proposição não está no banco
    mocks["tram_repo"].buscar_por_proposicao.return_value = []
    mocks["prop_repo"].buscar_por_id.return_value = None
    
    # ID numérico dispara tentativa nos adapters
    id_prop = "123"
    tram = Tramitacao(proposicao_id=id_prop, data_hora="2024-01-01", sequencia=1, sigla_orgao="X", descricao_tramitacao="Y")
    
    mocks["camara_adapter"].buscar_tramitacoes.return_value = [tram]
    
    resultados = service.executar(id_prop)
    
    assert resultados == [tram]
    mocks["camara_adapter"].buscar_tramitacoes.assert_called_once_with(123)
    mocks["tram_repo"].salvar_lote.assert_called_once()

def test_listar_tramitacoes_fallback_senado_sucesso(service, mocks):
    # Proposição não está no banco, nem na Câmara
    mocks["tram_repo"].buscar_por_proposicao.return_value = []
    mocks["prop_repo"].buscar_por_id.return_value = None
    mocks["camara_adapter"].buscar_tramitacoes.return_value = []
    
    id_prop = "456"
    tram = Tramitacao(proposicao_id=id_prop, data_hora="2024-01-01", sequencia=1, sigla_orgao="X", descricao_tramitacao="Y")
    mocks["senado_adapter"].buscar_tramitacoes.return_value = [tram]
    
    resultados = service.executar(id_prop)
    
    assert resultados == [tram]
    mocks["senado_adapter"].buscar_tramitacoes.assert_called_once_with(456)

def test_listar_tramitacoes_id_nao_numerico_sem_prop_no_banco(service, mocks):
    mocks["tram_repo"].buscar_por_proposicao.return_value = []
    mocks["prop_repo"].buscar_por_id.return_value = None
    
    id_prop = "nao-sou-numero"
    resultados = service.executar(id_prop)
    
    assert resultados == []
    mocks["camara_adapter"].buscar_tramitacoes.assert_not_called()
    mocks["senado_adapter"].buscar_tramitacoes.assert_not_called()
