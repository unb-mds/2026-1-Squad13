import pytest
from infrastructure.adapters.camara_adapter import CamaraAdapter
from domain.entities.proposicao import Proposicao

@pytest.mark.integration
def test_camara_adapter_buscar_por_id_valido():
    """Verifica se o adaptador consegue buscar e converter uma proposição real da Câmara."""
    adapter = CamaraAdapter()
    # ID 2368289 -> PL 2981/2023
    id_valido = 2368289 
    
    proposicao = adapter.buscar_por_id(id_valido)
    
    assert proposicao is not None
    assert isinstance(proposicao, Proposicao)
    assert proposicao.id == str(id_valido)
    assert proposicao.tipo == "PL"
    assert proposicao.numero == "2981"
    assert proposicao.ano == 2023
    assert proposicao.ementa is not None
    assert "Câmara dos Deputados" in proposicao.link_oficial or "camara.leg.br" in proposicao.link_oficial

@pytest.mark.integration
def test_camara_adapter_buscar_por_id_invalido():
    """Verifica comportamento do adaptador com ID inexistente."""
    adapter = CamaraAdapter()
    id_invalido = 999999999 # Provavelmente inexistente
    
    proposicao = adapter.buscar_por_id(id_invalido)
    
    assert proposicao is None
