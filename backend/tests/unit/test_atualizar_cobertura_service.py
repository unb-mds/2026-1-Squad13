from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from application.services.atualizar_cobertura_service import AtualizarCoberturaService
from domain.entities.cobertura_snapshot import CoberturaSnapshot


@pytest.fixture
def mock_repos():
    cobertura_repo = MagicMock()
    proposicao_repo = MagicMock()
    camara_adapter = MagicMock()
    senado_adapter = MagicMock()

    return {
        "cobertura_repo": cobertura_repo,
        "proposicao_repo": proposicao_repo,
        "camara_adapter": camara_adapter,
        "senado_adapter": senado_adapter,
    }


@pytest.fixture
def service(mock_repos):
    return AtualizarCoberturaService(
        cobertura_repo=mock_repos["cobertura_repo"],
        proposicao_repo=mock_repos["proposicao_repo"],
        camara_adapter=mock_repos["camara_adapter"],
        senado_adapter=mock_repos["senado_adapter"],
    )


@pytest.mark.asyncio
async def test_atualizar_snapshot_camara(service, mock_repos):
    # Arrange
    mock_repos["camara_adapter"].obter_total = AsyncMock(return_value=120)
    mock_repos["cobertura_repo"].salvar = MagicMock(side_effect=lambda x: x)

    # Act
    snapshot = await service.atualizar_snapshot(2026, "PL", "camara")

    # Assert
    assert snapshot.ano == 2026
    assert snapshot.tipo_proposicao == "PL"
    assert snapshot.total_api_oficial == 120
    mock_repos["camara_adapter"].obter_total.assert_called_once_with("PL", 2026)
    mock_repos["cobertura_repo"].salvar.assert_called_once()


@pytest.mark.asyncio
async def test_atualizar_snapshot_senado(service, mock_repos):
    # Arrange
    mock_repos["senado_adapter"].obter_total = AsyncMock(return_value=80)
    mock_repos["cobertura_repo"].salvar = MagicMock(side_effect=lambda x: x)

    # Act
    snapshot = await service.atualizar_snapshot(2026, "PEC", "senado")

    # Assert
    assert snapshot.ano == 2026
    assert snapshot.tipo_proposicao == "PEC"
    assert snapshot.total_api_oficial == 80
    mock_repos["senado_adapter"].obter_total.assert_called_once_with("PEC", 2026)
    mock_repos["cobertura_repo"].salvar.assert_called_once()


def test_obter_metricas_cobertura(service, mock_repos):
    # Arrange
    dt = datetime.now(UTC)
    snap = CoberturaSnapshot(
        id=1, ano=2026, tipo_proposicao="PL", total_api_oficial=100, data_atualizacao=dt
    )
    mock_repos["cobertura_repo"].buscar_por_ano_e_tipo.return_value = snap
    mock_repos["proposicao_repo"].contar.return_value = 85

    # Act
    metrics = service.obter_metricas_cobertura(2026, "PL")

    # Assert
    assert metrics["ano"] == 2026
    assert metrics["tipo_proposicao"] == "PL"
    assert metrics["total_local"] == 85
    assert metrics["total_api_oficial"] == 100
    assert metrics["percentual_cobertura"] == 85.0
    assert metrics["data_atualizacao"] == dt
