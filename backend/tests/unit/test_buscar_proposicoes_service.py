import pytest
from domain.entities.proposicao import Proposicao

def test_deve_lancar_erro_ao_buscar_sem_filtros(service):
    # Act & Assert
    with pytest.raises(ValueError) as excinfo:
        service.executar(filtros={})
    
    assert "Preencha pelo menos um filtro" in str(excinfo.value)

def test_deve_filtrar_por_tipo_com_sucesso(service, mock_repositorio, lista_proposicoes):
    # Arrange
    # Filtramos a lista para simular o comportamento do repositório
    proposicoes_pl = [p for p in lista_proposicoes if p.tipo == "PL"]
    mock_repositorio.filtrar.return_value = proposicoes_pl
    
    # Act
    resultado = service.executar(filtros={"tipo": "PL"})
    
    # Assert
    assert resultado["total"] == 2
    assert all(p.tipo == "PL" for p in resultado["items"])
    mock_repositorio.filtrar.assert_called_once_with(
        tipo="PL", numero=None, ano=None, autor=None, status_tramitacao=None
    )
