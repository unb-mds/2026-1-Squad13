from unittest.mock import MagicMock, patch


def test_detalhe_proposicao_com_muitas_emendas_mock(http_client):
    """
    Teste de integração (pipeline completo) que valida a contagem de emendas
    em uma proposição de alto volume, mockando a API da Câmara com paginação.
    """
    id_prop = "2256735"  # PL 2630/2020

    # Mock responses
    mock_prop = {
        "dados": {
            "id": 2256735,
            "siglaTipo": "PL",
            "numero": 2630,
            "ano": 2020,
            "ementa": "Ementa Fake News",
            "dataApresentacao": "2020-01-01",
            "statusProposicao": {"dataHora": "2020-01-01T10:00:00"},
        }
    }

    mock_autores = {"dados": [{"nome": "Autor Teste"}]}

    # Simula 2 páginas de relacionadas
    mock_rel1 = {
        "dados": [{"siglaTipo": "EMP"}] * 50,  # 50 emendas
        "links": [{"rel": "next", "href": "http://api/relacionadas?pagina=2"}],
    }
    mock_rel2 = {
        "dados": [{"siglaTipo": "SBT"}] * 30,  # + 30 substitutivos
        "links": [],
    }

    # Patch no requests dentro do CamaraAdapter
    with patch("requests.Session.get") as mock_get:
        r_prop = MagicMock()
        r_prop.status_code = 200
        r_prop.json.return_value = mock_prop
        r_prop.raise_for_status.return_value = None

        r_autores = MagicMock()
        r_autores.status_code = 200
        r_autores.json.return_value = mock_autores
        r_autores.raise_for_status.return_value = None

        r_rel1 = MagicMock()
        r_rel1.status_code = 200
        r_rel1.json.return_value = mock_rel1
        r_rel1.raise_for_status.return_value = None

        r_rel2 = MagicMock()
        r_rel2.status_code = 200
        r_rel2.json.return_value = mock_rel2
        r_rel2.raise_for_status.return_value = None

        mock_get.side_effect = [r_prop, r_autores, r_rel1, r_rel2]

        # Act
        response = http_client.get(f"/proposicoes/{id_prop}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == id_prop
        assert data["numeroEmendas"] == 80
        assert data["tipo"] == "PL"
