import asyncio
import time
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from application.services.preencher_lacunas_service import (
    AsyncRateLimiter,
    PreencherLacunasService,
    parse_retry_after,
)
from domain.entities.proposicao import Proposicao
from domain.exceptions import ApiRateLimitError


class MockCacheProvider:
    """Implementação em memória do CacheProvider para testes robustos."""

    def __init__(self):
        self.store = {}
        self.should_fail_watch = 0  # Contador de WatchError simulados

    def get(self, key: str) -> Any | None:
        return self.store.get(key)

    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        self.store[key] = value

    def delete(self, key: str) -> None:
        if key in self.store:
            del self.store[key]

    def invalidate(self, prefix: str) -> None:
        keys_to_del = [k for k in self.store if k.startswith(prefix)]
        for k in keys_to_del:
            self.delete(k)

    def set_nx(self, key: str, value: Any, ttl_seconds: int) -> bool:
        if key in self.store:
            return False
        self.store[key] = value
        return True

    def eval_lua(self, script: str, keys: list[str], args: list[Any]) -> Any:
        # Simula script Lua de release-lock
        if "redis.call('get', KEYS[1]) == ARGV[1]" in script:
            key = keys[0]
            token = args[0]
            if self.store.get(key) == token:
                del self.store[key]
                return 1
            return 0
        return None

    def obter_e_atualizar_multichaves_seguro(
        self, keys: list[str], update_fn: Callable[[list[Any]], dict[str, Any] | None]
    ) -> bool:
        if self.should_fail_watch > 0:
            self.should_fail_watch -= 1
            # Simula a falha de WATCH concorrente
            return False

        valores_atuais = [self.store.get(k) for k in keys]
        novos_valores = update_fn(valores_atuais)
        if novos_valores is None:
            return False

        for k, v in novos_valores.items():
            if v == "":
                self.delete(k)
            else:
                self.set(k, v)
        return True


@pytest.fixture
def repo_mock():
    repo = MagicMock()
    repo.contar.return_value = 50
    return repo


@pytest.fixture
def camara_mock():
    adapter = AsyncMock()
    adapter.obter_total.return_value = 100
    adapter.listar_recentes.return_value = [1, 2, 3]

    p = Proposicao(
        id="1",
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
    adapter.listar_recentes.return_value = [4, 5]

    p = Proposicao(
        id="4",
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
def service(repo_mock, camara_mock, senado_mock, cache_mock):
    return PreencherLacunasService(repo_mock, camara_mock, senado_mock, cache_mock)


def test_parse_retry_after_formatos():
    """Valida parse de Retry-After de inteiros e datas RFC 7231."""
    # Caso 1: Inteiro
    assert parse_retry_after("120") == 120

    # Caso 2: Data RFC 7231
    future_date = datetime.now(UTC) + timedelta(seconds=45)
    date_str = future_date.strftime("%a, %d %b %Y %H:%M:%S GMT")
    parsed = parse_retry_after(date_str)
    # Compara tolerando pequena diferença de precisão (1-2s)
    assert 40 <= parsed <= 50

    # Caso 3: Inválido / Vazio
    assert parse_retry_after(None) == 0
    assert parse_retry_after("Data Invalida") == 0


@pytest.mark.asyncio
async def test_rate_limiter_temporal_com_lock_monotonic():
    """Garante que requisições paralelas concorrentes respeitem o atraso temporal com Lock e monotonic()."""
    limiter = AsyncRateLimiter(0.05)  # 50ms

    start_time = time.monotonic()

    # Dispara 3 requisições concorrentes
    await asyncio.gather(
        limiter.esperar(),
        limiter.esperar(),
        limiter.esperar(),
    )

    duration = time.monotonic() - start_time
    # 3 chamadas -> 2 intervalos de 50ms = mínimo 100ms
    assert duration >= 0.09


@pytest.mark.asyncio
async def test_pruning_anos_consolidados(service, repo_mock, camara_mock, senado_mock, cache_mock):
    """Ano consolidado não dispara COUNT(*) nem totalização externa."""
    ano_atual = datetime.now(UTC).year
    ano_anterior = ano_atual - 1

    cache_mock.set(f"seeding:consolidado:camara:{ano_anterior}:PL", "1")
    cache_mock.set(f"seeding:consolidado:camara:{ano_anterior}:PEC", "1")

    lacunas = await service._detectar_lacunas()
    print("\n--- DEBUG test_pruning_anos_consolidados ---")
    print("ANO ANTERIOR:", ano_anterior)
    print("CHAVES NO CACHE:", cache_mock.store)
    print("LACUNAS:", lacunas)
    print("-------------------------------------------\n")


    # Verifica se buscou ano atual da Câmara
    assert any(lac["fonte"] == "camara" and lac["ano"] == ano_atual for lac in lacunas)

    # Garante que o ano anterior (consolidado) não está listado como lacuna ativa
    assert not any(lac["fonte"] == "camara" and lac["ano"] == ano_anterior for lac in lacunas)



@pytest.mark.asyncio
async def test_concorrencia_adaptativa_lote_p95_sucesso(service, cache_mock):
    """P95 baixo aumenta o semáforo em +1."""
    cfg = {
        "concorrencia": 5,
        "rtts": [0.1, 0.15, 0.2],  # RTT P95 = 200ms
        "timeout_count": 0,
        "erros_criticos_lote": 0,
    }

    service._ajustar_concorrencia_lote("camara", cfg)
    assert cfg["concorrencia"] == 6


@pytest.mark.asyncio
async def test_concorrencia_adaptativa_lote_slow_reduz(service, cache_mock):
    """P95 alto reduz concorrência pela metade."""
    cfg = {
        "concorrencia": 10,
        "rtts": [1.5, 1.5, 1.5],  # RTT P95 = 1500ms
        "timeout_count": 0,
        "erros_criticos_lote": 0,
    }


    service._ajustar_concorrencia_lote("camara", cfg)
    assert cfg["concorrencia"] == 5


@pytest.mark.asyncio
async def test_breaker_abre_apenas_acima_20_porcento(service, cache_mock):
    """Breaker só abre se o percentual de falhas definitivas com 429 no lote exceder 20%."""
    # Lote de 10 requisições
    cfg = {
        "cb_estado": "CLOSED",
        "cb_falhas": 0,
        "cb_bloqueado_ate": None,
        "total_solicitados_lote": 10,
        "erros_criticos_429_lote": 1,  # 10%
    }

    # 10% de erros não deve abrir
    service._registrar_falha_cb_local("camara", is_429=True, config={"camara": cfg})
    assert cfg["cb_estado"] == "CLOSED"

    # 3 erros de 10 (30% > 20%) -> deve abrir disjuntor
    cfg["erros_criticos_429_lote"] = 3
    service._registrar_falha_cb_local("camara", is_429=True, config={"camara": cfg})
    assert cfg["cb_estado"] == "OPEN"
    assert cfg["cb_bloqueado_ate"] is not None


@pytest.mark.asyncio
async def test_429_com_retry_after(service, camara_mock):
    """Captura o erro 429, aplica o tempo de Retry-After e re-tenta com sucesso."""
    cfg = {
        "429_count": 0,
        "retry_after_max": 0,
    }

    # Simula erro 429 na primeira tentativa, e sucesso na segunda
    # Importante: Como o adapter lança ApiRateLimitError, simulamos esse comportamento no mock
    erro_rate = ApiRateLimitError("Rate limit", retry_after="5")
    p_sucesso = camara_mock.buscar_por_id.return_value

    # Moca a busca do adapter com side_effect para falhar uma vez e funcionar na segunda
    camara_mock.buscar_por_id.side_effect = [erro_rate, p_sucesso]

    # Substitui temporariamente o sleep para agilizar os testes
    with patch("asyncio.sleep") as mock_sleep:
        res = await service._executar_request_com_retry_after(
            camara_mock, 1, AsyncMock(), cfg
        )
        assert res == p_sucesso
        assert cfg["429_count"] == 1
        assert cfg["retry_after_max"] == 5
        mock_sleep.assert_called_once_with(5)


@pytest.mark.asyncio
async def test_lote_vazio_consolida_ano_historico(service, camara_mock, cache_mock):
    """API retornando vazio para ano < ano_atual remove cursor e consolida ano."""
    lacuna = {"fonte": "camara", "ano": 2025, "tipo": "PL"}
    camara_mock.listar_recentes.return_value = []  # Retorno vazio

    with patch("application.services.preencher_lacunas_service.datetime") as mock_date:
        mock_date.now.return_value = datetime(2026, 6, 12, tzinfo=UTC)

        # Injeta configuração local mockada
        config = {
            "camara": {
                "taxa": 100,
                "concorrencia": 10,
                "429_count": 0,
                "erros_criticos_lote": 0,
            }
        }

        cache_mock.set("seeding:cursor:camara:2025:PL", "500")

        qtd = await service._preencher_lacuna(lacuna, config)
        assert qtd == 0

        # Cursor histórico deve ser deletado
        assert cache_mock.get("seeding:cursor:camara:2025:PL") is None

        # Ano deve estar consolidado
        assert cache_mock.get("seeding:consolidado:camara:2025:PL") == "1"


@pytest.mark.asyncio
async def test_lote_vazio_reseta_cursor_ano_atual(service, camara_mock, cache_mock):
    """API retornando vazio para ano == ano_atual reseta cursor para 0 e ativa flag temporária."""
    lacuna = {"fonte": "camara", "ano": 2026, "tipo": "PL"}
    camara_mock.listar_recentes.return_value = []  # Retorno vazio

    with patch("application.services.preencher_lacunas_service.datetime") as mock_date:
        mock_date.now.return_value = datetime(2026, 6, 12, tzinfo=UTC)

        config = {
            "camara": {
                "taxa": 100,
                "concorrencia": 10,
                "429_count": 0,
                "erros_criticos_lote": 0,
            }
        }

        cache_mock.set("seeding:cursor:camara:2026:PL", "1200")

        qtd = await service._preencher_lacuna(lacuna, config)
        assert qtd == 0

        # Cursor do ano atual reseta para 0
        assert cache_mock.get("seeding:cursor:camara:2026:PL") == "0"

        # Deve ter flag temporária ativa de sincronizado
        assert cache_mock.get("seeding:sincronizado:ano_atual:camara:PL") == "1"


@pytest.mark.asyncio
async def test_cursor_reserva_lock(service, cache_mock):
    """Valida que a chave de reserva seeding:lock:processando:... impede workers paralelos de buscar o mesmo offset."""
    lacuna = {"fonte": "camara", "ano": 2026, "tipo": "PL"}

    # Simula lock já adquirido por outro worker
    cache_mock.set("seeding:lock:processando:camara:2026:PL:0", "outro-token")

    config = {
        "camara": {
            "taxa": 100,
            "concorrencia": 10,
        }
    }

    qtd = await service._preencher_lacuna(lacuna, config)
    # Deve retornar 0 imediatamente (pulou processamento)
    assert qtd == 0


@pytest.mark.asyncio
async def test_cursor_commit_monotonicidade(service, cache_mock):
    """Impede regressão indevida do cursor."""
    cache_mock.set("seeding:cursor:camara:2026:PL", "500")

    # Tenta atualizar para um valor menor (regressão)
    service._salvar_cursor_seguro("camara", 2026, "PL", 300)
    assert cache_mock.get("seeding:cursor:camara:2026:PL") == "500"

    # Atualiza para maior (avanço)
    service._salvar_cursor_seguro("camara", 2026, "PL", 700)
    assert cache_mock.get("seeding:cursor:camara:2026:PL") == "700"

    # Permite 0 (reset deliberado)
    service._salvar_cursor_seguro("camara", 2026, "PL", 0)
    assert cache_mock.get("seeding:cursor:camara:2026:PL") == "0"


@pytest.mark.asyncio
async def test_batch_size_calibration_backlog_baixo(service, camara_mock, cache_mock):
    """Backlog baixo (<= 100) limita o batch size (cap_lote = 20)."""
    lacuna = {"fonte": "camara", "ano": 2026, "tipo": "PL"}
    camara_mock.listar_recentes.return_value = [1, 2]

    config = {
        "camara": {
            "taxa": 100,
            "concorrencia": 10,
            "rtts": [],
            "429_count": 0,
            "erros_criticos_lote": 0,
            "erros_criticos_429_lote": 0,
            "5xx_count": 0,
            "timeout_count": 0,
            "retry_after_max": 0,
            "cb_estado": "CLOSED",
        }
    }

    with patch.object(service, "_executar_request_com_retry_after", new_callable=AsyncMock):
        await service._preencher_lacuna(lacuna, config, backlog_size=50)

        # Verifica se o batch_size usado no listar_recentes foi capped em 20
        assert camara_mock.listar_recentes.call_args[1]["quantidade"] == 20


@pytest.mark.asyncio
async def test_batch_size_calibration_backlog_medio(service, camara_mock, cache_mock):
    """Backlog médio (<= 1000) limita o batch size (cap_lote = 150)."""
    lacuna = {"fonte": "camara", "ano": 2026, "tipo": "PL"}
    camara_mock.listar_recentes.return_value = [1, 2]

    config = {
        "camara": {
            "taxa": 250,
            "concorrencia": 10,
            "rtts": [],
            "429_count": 0,
            "erros_criticos_lote": 0,
            "erros_criticos_429_lote": 0,
            "5xx_count": 0,
            "timeout_count": 0,
            "retry_after_max": 0,
            "cb_estado": "CLOSED",
        }
    }

    with patch.object(service, "_executar_request_com_retry_after", new_callable=AsyncMock):
        await service._preencher_lacuna(lacuna, config, backlog_size=500)

        # Verifica se o batch_size usado no listar_recentes foi capped em 150
        assert camara_mock.listar_recentes.call_args[1]["quantidade"] == 150


@pytest.mark.asyncio
async def test_batch_size_calibration_backlog_alto(service, camara_mock, cache_mock):
    """Backlog alto (> 1000) limita o batch size (cap_lote = 300)."""
    lacuna = {"fonte": "camara", "ano": 2026, "tipo": "PL"}
    camara_mock.listar_recentes.return_value = [1, 2]

    config = {
        "camara": {
            "taxa": 350,
            "concorrencia": 10,
            "rtts": [],
            "429_count": 0,
            "erros_criticos_lote": 0,
            "erros_criticos_429_lote": 0,
            "5xx_count": 0,
            "timeout_count": 0,
            "retry_after_max": 0,
            "cb_estado": "CLOSED",
        }
    }

    with patch.object(service, "_executar_request_com_retry_after", new_callable=AsyncMock):
        await service._preencher_lacuna(lacuna, config, backlog_size=1500)

        # Verifica se o batch_size usado no listar_recentes foi capped em 300
        assert camara_mock.listar_recentes.call_args[1]["quantidade"] == 300

