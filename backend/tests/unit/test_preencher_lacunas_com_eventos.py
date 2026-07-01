from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from application.services.preencher_lacunas_service import PreencherLacunasService
from domain.entities.proposicao import Proposicao
from infrastructure.adapters.senado_adapter import SenadoAdapter
from tests.unit.test_preencher_lacunas_service import MockCacheProvider


@pytest.fixture
def repo_mock():
    repo = MagicMock()
    repo.contar.return_value = 50
    return repo


@pytest.fixture
def camara_mock():
    adapter = AsyncMock()
    adapter.obter_total.return_value = 100
    adapter.listar_recentes.return_value = [1, 2]

    p = Proposicao(
        id="camara:1",
        tipo="PL",
        numero="123",
        ano=2026,
        autor="Autor Teste",
        uf_autor="DF",
        orgao_origem="Câmara dos Deputados",
        status="Sem status",
        ementa="Ementa Teste",
        data_apresentacao="2026-06-12",
        data_ultima_movimentacao="2026-06-12",
        orgao_atual="Câmara",
        link_oficial="http://link",
        regime_tramitacao="ORDINARIO",
        tags=[],
        numero_assinaturas=1,
        numero_emendas=0,
        autor_e_poder_executivo=False,
        tema_economico=False,
    )
    adapter.buscar_por_id.return_value = p
    return adapter


@pytest.fixture
def senado_mock():
    adapter = AsyncMock()
    adapter.obter_total.return_value = 80
    adapter.listar_recentes.return_value = [3]

    p = Proposicao(
        id="senado:3",
        tipo="PL",
        numero="456",
        ano=2026,
        autor="Autor Senado",
        uf_autor="N/A",
        orgao_origem="Senado Federal",
        status="Sem status",
        ementa="Ementa Senado",
        data_apresentacao="2026-06-12",
        data_ultima_movimentacao="2026-06-12",
        orgao_atual="Senado",
        link_oficial="http://link",
        regime_tramitacao="ORDINARIO",
        tags=[],
        numero_assinaturas=1,
        numero_emendas=0,
        autor_e_poder_executivo=False,
        tema_economico=False,
    )
    adapter.buscar_por_id.return_value = p
    return adapter


@pytest.fixture
def cache_mock():
    return MockCacheProvider()


@pytest.fixture
def mov_service_mock():
    return AsyncMock()


@pytest.fixture
def service(repo_mock, camara_mock, senado_mock, cache_mock, mov_service_mock):
    # Mocka os comportamentos de random para previsibilidade
    with (
        patch(
            "application.services.preencher_lacunas_service.random.shuffle",
            side_effect=lambda x: x.sort(key=lambda item: item["ano"], reverse=True),
        ),
        patch(
            "application.services.preencher_lacunas_service.random.choices",
            side_effect=lambda population, weights, k: [population[0]],
        ),
        patch(
            "application.services.preencher_lacunas_service.random.choice",
            side_effect=lambda seq: seq[0],
        ),
    ):
        yield PreencherLacunasService(
            proposicao_repo=repo_mock,
            camara_adapter=camara_mock,
            senado_adapter=senado_mock,
            cache=cache_mock,
            movimentacoes_service=mov_service_mock,
        )


@pytest.mark.asyncio
async def test_pos_processar_sem_servico_injetado(
    repo_mock, camara_mock, senado_mock, cache_mock
):
    """Garante que o fluxo roda normalmente sem disparar nada se mov_service não for injetado."""
    service_sem_mov = PreencherLacunasService(
        proposicao_repo=repo_mock,
        camara_adapter=camara_mock,
        senado_adapter=senado_mock,
        cache=cache_mock,
        movimentacoes_service=None,
    )
    proposicoes = [camara_mock.buscar_por_id.return_value]
    # Não deve lançar erro
    await service_sem_mov._pos_processar_proposicoes(proposicoes)


@pytest.mark.asyncio
async def test_pos_processar_com_flag_desativada(
    service, cache_mock, mov_service_mock, camara_mock
):
    """Garante que a coleta de eventos não é executada se a feature flag estiver inativa."""
    cache_mock.set("seeding:enable_eventos_gapfiller", "false")
    proposicoes = [camara_mock.buscar_por_id.return_value]

    await service._pos_processar_proposicoes(proposicoes)
    mov_service_mock.executar.assert_not_called()


@pytest.mark.asyncio
async def test_pos_processar_fluxo_feliz(
    service, cache_mock, mov_service_mock, camara_mock
):
    """Garante a coleta bem-sucedida com a feature flag habilitada."""
    cache_mock.set("seeding:enable_eventos_gapfiller", "true")
    cache_mock.set("seeding:eventos_batch_size", "5")
    cache_mock.set("seeding:eventos_concorrencia", "2")

    p1 = camara_mock.buscar_por_id.return_value
    p2 = Proposicao(
        id="senado:4",
        tipo="PL",
        numero="789",
        ano=2026,
        autor="Autor",
        uf_autor="DF",
        orgao_origem="Senado Federal",
        status="Sem status",
        ementa="Ementa",
        data_apresentacao="2026-06-12",
        data_ultima_movimentacao="2026-06-12",
        orgao_atual="Senado",
        link_oficial="http://link",
        regime_tramitacao="ORDINARIO",
        tags=[],
    )

    await service._pos_processar_proposicoes([p1, p2])

    assert mov_service_mock.executar.call_count == 2
    mov_service_mock.executar.assert_any_call("camara:1")
    mov_service_mock.executar.assert_any_call("senado:4")


@pytest.mark.asyncio
async def test_pos_processar_falha_parcial_isolada(
    service, cache_mock, mov_service_mock, camara_mock
):
    """Garante que uma falha de coleta em uma proposição não interrompe a coleta das demais do sublote."""
    cache_mock.set("seeding:enable_eventos_gapfiller", "true")

    p1 = camara_mock.buscar_por_id.return_value
    p2 = Proposicao(
        id="senado:4",
        tipo="PL",
        numero="789",
        ano=2026,
        autor="Autor",
        uf_autor="DF",
        orgao_origem="Senado Federal",
        status="Sem status",
        ementa="Ementa",
        data_apresentacao="2026-06-12",
        data_ultima_movimentacao="2026-06-12",
        orgao_atual="Senado",
        link_oficial="http://link",
        regime_tramitacao="ORDINARIO",
        tags=[],
    )

    # Simula falha para p1 e sucesso para p2
    mov_service_mock.executar.side_effect = lambda pid: (
        raise_error() if pid == "camara:1" else None
    )

    def raise_error():
        raise Exception("Erro de conexão na Câmara")

    # A execução não deve quebrar
    await service._pos_processar_proposicoes([p1, p2])

    assert mov_service_mock.executar.call_count == 2
    mov_service_mock.executar.assert_any_call("camara:1")
    mov_service_mock.executar.assert_any_call("senado:4")


@pytest.mark.asyncio
async def test_pos_processar_ignora_ids_invalidos(
    service, cache_mock, mov_service_mock
):
    """Garante que apenas proposições com identificadores válidos seguem para a coleta."""
    cache_mock.set("seeding:enable_eventos_gapfiller", "true")

    p_invalido_1 = Proposicao(
        id="invalido:123",  # Prefixo desconhecido
        tipo="PL",
        numero="1",
        ano=2026,
        autor="Autor",
        status="Sem status",
        ementa="Ementa",
        data_apresentacao="2026-06-12",
        data_ultima_movimentacao="2026-06-12",
        orgao_atual="Câmara",
    )
    p_invalido_2 = Proposicao(
        id="camara:abc",  # Sufixo não-numérico
        tipo="PL",
        numero="1",
        ano=2026,
        autor="Autor",
        status="Sem status",
        ementa="Ementa",
        data_apresentacao="2026-06-12",
        data_ultima_movimentacao="2026-06-12",
        orgao_atual="Câmara",
    )
    p_valido = Proposicao(
        id="camara:100",
        tipo="PL",
        numero="100",
        ano=2026,
        autor="Autor",
        status="Sem status",
        ementa="Ementa",
        data_apresentacao="2026-06-12",
        data_ultima_movimentacao="2026-06-12",
        orgao_atual="Câmara",
    )

    await service._pos_processar_proposicoes([p_invalido_1, p_invalido_2, p_valido])

    mov_service_mock.executar.assert_called_once_with("camara:100")


@pytest.mark.asyncio
async def test_senado_adapter_traducao_pl_para_pls_historico():
    """Valida que o SenadoAdapter traduz dinamicamente a sigla PL para PLS quando o ano é anterior a 2019."""
    adapter = SenadoAdapter()

    mock_client = AsyncMock()
    # Mock da resposta para obter_total
    mock_client.get.return_value = MagicMock(
        status_code=200, json=lambda: [{"codigoMateria": 1}]
    )

    # Caso 1: ano 2018 (anterior a 2019) -> deve traduzir para PLS
    await adapter.obter_total("PL", 2018, client=mock_client)
    _, kwargs = mock_client.get.call_args
    assert kwargs["params"]["sigla"] == "PLS"

    # Caso 2: ano 2020 (a partir de 2019) -> deve manter PL
    await adapter.obter_total("PL", 2020, client=mock_client)
    _, kwargs = mock_client.get.call_args
    assert kwargs["params"]["sigla"] == "PL"

    # Caso 3: PEC no ano 2018 -> deve manter PEC (não traduz)
    await adapter.obter_total("PEC", 2018, client=mock_client)
    _, kwargs = mock_client.get.call_args
    assert kwargs["params"]["sigla"] == "PEC"


@pytest.mark.asyncio
async def test_preencher_lacunas_detectar_lacunas_senado_pls(
    service, repo_mock, cache_mock, senado_mock
):
    """Garante que a contagem local em _detectar_lacunas mapeia o tipo para PLS no Senado antes de 2019."""
    # Simula ano atual 2026
    with patch("application.services.preencher_lacunas_service.datetime") as mock_date:
        mock_date.now.return_value = datetime(2026, 6, 12, tzinfo=UTC)

        # Simula contagem local
        # O repo contar deve ser chamado com tipo="PLS" para o Senado pré-2019
        await service._detectar_lacunas()

        # Verifica as chamadas ao repo.contar
        chamadas = repo_mock.contar.call_args_list

        # Encontra a chamada do Senado Federal para o ano de 2015 (pré-2019)
        chamada_senado_2015 = None
        for c in chamadas:
            kwargs = c[1]
            if (
                kwargs.get("orgao_origem") == "Senado Federal"
                and kwargs.get("ano") == 2015
            ):
                chamada_senado_2015 = kwargs
                break

        assert chamada_senado_2015 is not None
        assert chamada_senado_2015["tipo"] == "PLS"
