import pytest
from infrastructure.adapters.senado_adapter import SenadoAdapter
from domain.entities.proposicao import Proposicao


@pytest.mark.integration
def test_senado_adapter_buscar_por_id_valido(monkeypatch, senado_api_materia_json):
    """Verifica se o adaptador consegue buscar e converter uma matéria real do Senado."""
    from unittest.mock import Mock

    adapter = SenadoAdapter()
    # ID usado no exemplo original
    id_valido = 8147067

    def mock_get(url, *args, **kwargs):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = Mock()
        mock_resp.json.return_value = senado_api_materia_json
        return mock_resp

    monkeypatch.setattr(adapter.session, 'get', mock_get)

    proposicao = adapter.buscar_por_id(id_valido)

    assert proposicao is not None
    assert isinstance(proposicao, Proposicao)
    assert proposicao.id == f"senado:{id_valido}"
    assert proposicao.ementa is not None
    assert "Senado Federal" in proposicao.orgao_atual
    assert "senado.leg.br" in proposicao.link_oficial


@pytest.mark.integration
def test_senado_adapter_buscar_por_id_invalido():
    """Verifica comportamento do adaptador com ID inexistente no Senado."""
    adapter = SenadoAdapter()
    id_invalido = 999999999

    proposicao = adapter.buscar_por_id(id_invalido)

    assert proposicao is None
