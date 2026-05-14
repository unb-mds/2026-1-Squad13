import pytest
from unittest.mock import MagicMock
from application.services.buscar_proposicoes_service import BuscarProposicoesService

@pytest.fixture
def mock_repositorio(lista_proposicoes):
    """
    Repositório falso. Retorna lista_proposicoes por padrão.
    Cada teste pode sobrescrever o return_value se precisar.
    """
    repo = MagicMock()
    repo.filtrar.return_value = lista_proposicoes
    repo.contar.return_value = len(lista_proposicoes)
    return repo

@pytest.fixture
def service(mock_repositorio):
    """Service já montado com o repositório mockado."""
    return BuscarProposicoesService(repository=mock_repositorio)
