from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError

from application.services.coletar_em_lote_service import ColetarEmLoteService
from domain.entities.proposicao import Proposicao


@pytest.fixture
def mock_proposicao():
    return Proposicao(
        id="camara:123",
        tipo="PL",
        numero="123",
        ano=2024,
        autor="Autor",
        orgao_origem="Câmara dos Deputados",
        status="Status",
        ementa="Ementa",
        data_apresentacao="2024-01-01",
        data_ultima_movimentacao="2024-01-01",
    )


@pytest.mark.asyncio
async def test_coletar_loga_excecao_detalhada_em_falha(mock_proposicao):
    """Bug B: Verifica se falhas na busca detalhada são logadas com erro."""
    mock_repo = MagicMock()
    mock_evento_repo = MagicMock()
    mock_fase_repo = MagicMock()
    mock_orgao_repo = MagicMock()
    mock_apensamento_repo = MagicMock()
    mock_log_repo = MagicMock()
    mock_camara = AsyncMock()
    mock_senado = AsyncMock()

    # Simula gap para disparar a coleta
    mock_repo.contar.return_value = 0
    mock_camara.obter_total.return_value = 1
    mock_camara.listar_recentes.return_value = [123]

    # Simula falha catastrófica ao buscar detalhes
    mock_camara.buscar_por_id.side_effect = Exception("Falha Crítica na API")

    service = ColetarEmLoteService(
        repository=mock_repo,
        evento_repo=mock_evento_repo,
        fase_repo=mock_fase_repo,
        orgao_repo=mock_orgao_repo,
        apensamento_repo=mock_apensamento_repo,
        log_repo=mock_log_repo,
        camara_adapter=mock_camara,
        senado_adapter=mock_senado,
    )

    with patch("application.services.coletar_em_lote_service.logger") as mock_logger:
        await service.executar_coleta_diaria()

        # Deve ter logado o erro com a mensagem da exceção
        mock_logger.error.assert_any_call(
            "❌ Falha na busca detalhada da proposição 123 na CAMARA: Falha Crítica na API"
        )


@pytest.mark.asyncio
async def test_coletar_continua_apos_falha_individual(mock_proposicao):
    """Bug B: Verifica se uma falha de banco em uma proposição não impede as outras (rollback)."""
    mock_repo = MagicMock()
    # Expõe uma sessão mockada para testar o rollback
    mock_session = MagicMock()
    mock_repo.session = mock_session

    mock_evento_repo = MagicMock()
    mock_fase_repo = MagicMock()
    mock_orgao_repo = MagicMock()
    mock_apensamento_repo = MagicMock()
    mock_log_repo = MagicMock()
    mock_camara = AsyncMock()
    mock_senado = AsyncMock()

    service = ColetarEmLoteService(
        repository=mock_repo,
        evento_repo=mock_evento_repo,
        fase_repo=mock_fase_repo,
        orgao_repo=mock_orgao_repo,
        apensamento_repo=mock_apensamento_repo,
        log_repo=mock_log_repo,
        camara_adapter=mock_camara,
        senado_adapter=mock_senado,
    )

    prop1 = mock_proposicao.model_copy(update={"id": "camara:1"})
    prop2 = mock_proposicao.model_copy(update={"id": "camara:2"})

    # Mock do listar_movimentacoes_service.executar
    # A primeira falha com IntegrityError (FK violation), a segunda tem sucesso
    mock_listar_service = AsyncMock()
    mock_listar_service.executar.side_effect = [
        IntegrityError("FK violation", params=None, orig=None),
        [],  # Sucesso para a segunda
    ]
    service.listar_movimentacoes_service = mock_listar_service

    # Act
    await service._processar_proposicoes([prop1, prop2], client=AsyncMock())

    # Assert
    # Deve ter tentado executar para AMBAS
    assert mock_listar_service.executar.call_count == 2
    # Deve ter chamado rollback após a falha da primeira
    mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_coletar_valida_prefixo_de_id(mock_proposicao):
    """Bug B: Verifica se proposições sem prefixo (ex: '123') são ignoradas para evitar FK violation."""
    mock_repo = MagicMock()
    mock_evento_repo = MagicMock()
    mock_fase_repo = MagicMock()
    mock_orgao_repo = MagicMock()
    mock_apensamento_repo = MagicMock()
    mock_log_repo = MagicMock()
    mock_camara = AsyncMock()
    mock_senado = AsyncMock()

    service = ColetarEmLoteService(
        repository=mock_repo,
        evento_repo=mock_evento_repo,
        fase_repo=mock_fase_repo,
        orgao_repo=mock_orgao_repo,
        apensamento_repo=mock_apensamento_repo,
        log_repo=mock_log_repo,
        camara_adapter=mock_camara,
        senado_adapter=mock_senado,
    )

    # ID sem prefixo
    prop_invalida = mock_proposicao.model_copy(update={"id": "123"})

    mock_listar_service = AsyncMock()
    service.listar_movimentacoes_service = mock_listar_service

    # Act
    await service._processar_proposicoes([prop_invalida], client=AsyncMock())

    # Assert
    # Não deve ter chamado o listar_movimentacoes_service.executar
    mock_listar_service.executar.assert_not_called()

    # Deve ter logado um warning
    with patch("application.services.coletar_em_lote_service.logger") as mock_logger:
        await service._processar_uma_proposicao(prop_invalida, client=AsyncMock())
        mock_logger.warning.assert_any_call(
            "⚠️ Proposição com ID inválido (sem prefixo): 123. Ignorando eventos para evitar FK violation."
        )
