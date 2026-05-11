import pytest
from domain.entities.proposicao import Proposicao

def test_deve_lancar_erro_ao_buscar_sem_filtros(service):
    # Act & Assert
    with pytest.raises(ValueError) as excinfo:
        service.executar(filtros={})
    
    assert "Preencha pelo menos um filtro" in str(excinfo.value)

def test_deve_filtrar_por_tipo_com_sucesso(service, mock_repositorio, lista_proposicoes):
    # Arrange
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

def test_deve_filtrar_por_ano_com_sucesso(service, mock_repositorio, lista_proposicoes):
    # Arrange
    proposicoes_2023 = [p for p in lista_proposicoes if p.ano == 2023]
    mock_repositorio.filtrar.return_value = proposicoes_2023
    
    # Act
    resultado = service.executar(filtros={"ano": 2023})
    
    # Assert
    assert resultado["total"] == 1
    assert resultado["items"][0].ano == 2023
    mock_repositorio.filtrar.assert_called_once_with(
        tipo=None, numero=None, ano=2023, autor=None, status_tramitacao=None
    )

def test_deve_retornar_lista_vazia_quando_nao_houver_resultados(service, mock_repositorio):
    # Arrange
    mock_repositorio.filtrar.return_value = []
    
    # Act
    resultado = service.executar(filtros={"tipo": "PL", "ano": 1900})
    
    # Assert
    assert resultado["total"] == 0
    assert resultado["items"] == []
