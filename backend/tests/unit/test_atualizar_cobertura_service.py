"""
Testes unitários para AtualizarCoberturaService.

Cobrem o bug crítico onde `obter_metricas_cobertura` somava proposições de
Câmara + Senado e comparava com o total de apenas uma fonte, gerando percentuais
de cobertura ficticiamente > 100%.

Exemplo real do bug:
    PEC/2026 no banco: 4 (Câmara) + 9 (Senado) = 13 total
    API Senado reporta: 9
    Cobertura calculada sem filtro de fonte: 13/9 = 144% ← INCORRETO
    Cobertura correta (por fonte):
        Câmara: 4/9 = 44%
        Senado: 9/9 = 100%
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from application.services.atualizar_cobertura_service import AtualizarCoberturaService
from domain.entities.cobertura_snapshot import CoberturaSnapshot


def _snapshot(ano: int, tipo: str, fonte: str, total: int) -> CoberturaSnapshot:
    return CoberturaSnapshot(
        id=1,
        ano=ano,
        tipo_proposicao=tipo,
        fonte=fonte,
        total_api_oficial=total,
        data_atualizacao=datetime.now(UTC),
    )


# ─── Fixtures base ──────────────────────────────────────────────────────────────


@pytest.fixture
def mock_repos():
    cobertura_repo = MagicMock()
    proposicao_repo = MagicMock()
    camara_adapter = MagicMock()
    senado_adapter = MagicMock()

    cobertura_repo.buscar_por_ano_tipo_e_fonte.return_value = None
    cobertura_repo.buscar_por_ano_e_tipo.return_value = None

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


# ─── atualizar_snapshot ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_atualizar_snapshot_camara(service, mock_repos):
    """Snapshot salvo com fonte='camara' e total correto da API."""
    mock_repos["camara_adapter"].obter_total = AsyncMock(return_value=120)
    mock_repos["cobertura_repo"].salvar = MagicMock(side_effect=lambda x: x)

    snapshot = await service.atualizar_snapshot(2026, "PL", "camara")

    assert snapshot.ano == 2026
    assert snapshot.tipo_proposicao == "PL"
    assert snapshot.fonte == "camara"
    assert snapshot.total_api_oficial == 120
    mock_repos["camara_adapter"].obter_total.assert_called_once_with("PL", 2026)
    mock_repos["cobertura_repo"].salvar.assert_called_once()


@pytest.mark.asyncio
async def test_atualizar_snapshot_senado(service, mock_repos):
    """Snapshot salvo com fonte='senado' e total correto da API."""
    mock_repos["senado_adapter"].obter_total = AsyncMock(return_value=80)
    mock_repos["cobertura_repo"].salvar = MagicMock(side_effect=lambda x: x)

    snapshot = await service.atualizar_snapshot(2026, "PEC", "senado")

    assert snapshot.ano == 2026
    assert snapshot.tipo_proposicao == "PEC"
    assert snapshot.fonte == "senado"
    assert snapshot.total_api_oficial == 80
    mock_repos["senado_adapter"].obter_total.assert_called_once_with("PEC", 2026)
    mock_repos["cobertura_repo"].salvar.assert_called_once()


@pytest.mark.asyncio
async def test_atualizar_snapshot_fallback_api_zero(service, mock_repos):
    """Se API retorna 0 (instável), mantém o total do snapshot anterior."""
    snap_antigo = _snapshot(2026, "PEC", "senado", 9)
    mock_repos["senado_adapter"].obter_total = AsyncMock(return_value=0)
    mock_repos["cobertura_repo"].buscar_por_ano_tipo_e_fonte.return_value = snap_antigo
    mock_repos["cobertura_repo"].salvar = MagicMock(side_effect=lambda x: x)

    resultado = await service.atualizar_snapshot(2026, "PEC", "senado")

    assert resultado.total_api_oficial == 9, "Deve preservar o valor anterior"
    assert resultado.fonte == "senado"


# ─── obter_metricas_cobertura — regressão do bug de cobertura cruzada ──────────


def test_obter_metricas_cobertura_sem_fonte_retrocompativel(service, mock_repos):
    """Chamada sem fonte usa buscar_por_ano_e_tipo (retrocompatibilidade)."""
    dt = datetime.now(UTC)
    snap = _snapshot(2026, "PL", "", 100)
    snap.data_atualizacao = dt
    mock_repos["cobertura_repo"].buscar_por_ano_e_tipo.return_value = snap
    mock_repos["proposicao_repo"].contar.return_value = 85

    metrics = service.obter_metricas_cobertura(2026, "PL")

    assert metrics["ano"] == 2026
    assert metrics["tipo_proposicao"] == "PL"
    assert metrics["total_local"] == 85
    assert metrics["total_api_oficial"] == 100
    assert metrics["percentual_cobertura"] == 85.0
    assert metrics["data_atualizacao"] == dt


def test_cobertura_camara_nao_soma_senado(service, mock_repos):
    """
    REGRESSÃO — bug original: PEC/2026 tinha 4 Câmara + 9 Senado = 13 no banco.
    A API do Senado reportava 9 → cobertura fictícia de 144%.

    Com a correção, ao consultar 'camara', o contar() filtra por orgao_origem
    = 'Câmara dos Deputados', retornando 4 → 4/9 = 44% ≤ 100%.
    """
    snap = _snapshot(2026, "PEC", "camara", 9)
    mock_repos["cobertura_repo"].buscar_por_ano_tipo_e_fonte.return_value = snap

    # Simula: 4 Câmara, 9 Senado, 13 sem filtro (o bug)
    def contar_com_filtro(**kwargs):
        orgao = kwargs.get("orgao_origem")
        if orgao == "Câmara dos Deputados":
            return 4
        if orgao == "Senado Federal":
            return 9
        return 13  # <- o que o bug retornava

    mock_repos["proposicao_repo"].contar.side_effect = contar_com_filtro

    metricas = service.obter_metricas_cobertura(2026, "PEC", "camara")

    assert metricas["total_local"] == 4, "Deve contar só Câmara"
    assert metricas["percentual_cobertura"] <= 100.0, (
        "Cobertura nunca pode exceder 100%"
    )
    assert metricas["fonte"] == "camara"


def test_cobertura_senado_nao_soma_camara(service, mock_repos):
    """Fonte='senado' deve contar apenas proposições do Senado."""
    snap = _snapshot(2026, "PEC", "senado", 9)
    mock_repos["cobertura_repo"].buscar_por_ano_tipo_e_fonte.return_value = snap

    def contar_com_filtro(**kwargs):
        orgao = kwargs.get("orgao_origem")
        if orgao == "Senado Federal":
            return 9
        if orgao == "Câmara dos Deputados":
            return 4
        return 13

    mock_repos["proposicao_repo"].contar.side_effect = contar_com_filtro

    metricas = service.obter_metricas_cobertura(2026, "PEC", "senado")

    assert metricas["total_local"] == 9
    assert metricas["percentual_cobertura"] == 100.0
    assert metricas["fonte"] == "senado"


# ─── obter_todas_metricas_cobertura ────────────────────────────────────────────


def test_todas_metricas_filtram_por_fonte_corretamente(service, mock_repos):
    """
    Cada snapshot deve usar seu orgao_origem correspondente para contar,
    não a soma de todos.
    """
    snapshots = [
        _snapshot(2026, "PEC", "camara", 9),
        _snapshot(2026, "PEC", "senado", 9),
    ]
    mock_repos["cobertura_repo"].buscar_todos.return_value = snapshots

    def contar_com_filtro(**kwargs):
        orgao = kwargs.get("orgao_origem")
        if orgao == "Câmara dos Deputados":
            return 4
        if orgao == "Senado Federal":
            return 9
        return 13  # bug

    mock_repos["proposicao_repo"].contar.side_effect = contar_com_filtro

    resultados = service.obter_todas_metricas_cobertura()

    assert len(resultados) == 2
    camara_r = next(r for r in resultados if r["fonte"] == "camara")
    senado_r = next(r for r in resultados if r["fonte"] == "senado")

    assert camara_r["total_local"] == 4, "Câmara: só conta suas proposições"
    assert senado_r["total_local"] == 9, "Senado: só conta suas proposições"
    assert camara_r["percentual_cobertura"] <= 100.0
    assert senado_r["percentual_cobertura"] <= 100.0


# ─── Normalização de nomes de origem ──────────────────────────────────────────


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "origem,esperado",
    [
        ("camara", "camara"),
        ("Câmara dos Deputados", "camara"),
        ("senado", "senado"),
        ("Senado Federal", "senado"),
    ],
)
async def test_normalizacao_fonte_em_atualizar_snapshot(origem, esperado, mock_repos):
    """Diferentes formas de passar a origem são normalizadas corretamente."""
    adapter_key = "camara_adapter" if "camara" in esperado else "senado_adapter"
    mock_repos[adapter_key].obter_total = AsyncMock(return_value=10)
    mock_repos["cobertura_repo"].salvar = MagicMock(side_effect=lambda x: x)

    service = AtualizarCoberturaService(
        cobertura_repo=mock_repos["cobertura_repo"],
        proposicao_repo=mock_repos["proposicao_repo"],
        camara_adapter=mock_repos["camara_adapter"],
        senado_adapter=mock_repos["senado_adapter"],
    )

    snapshot = await service.atualizar_snapshot(2026, "PL", origem)

    assert snapshot.fonte == esperado
