import time
import pytest
from unittest.mock import MagicMock
from infrastructure.adapters.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    FAILURE_THRESHOLD,
    FAILURE_WINDOW,
    RECOVERY_TIMEOUT,
)


def _make_redis():
    """Retorna um mock de redis.Redis com comportamento realista para os testes."""
    store = {}

    def redis_get(key):
        entry = store.get(key)
        if entry is None:
            return None
        return entry["value"]

    def redis_set(key, value, nx=False, ex=None, **kwargs):
        if nx and key in store:
            return None
        store[key] = {"value": value if isinstance(value, bytes) else str(value).encode()}
        return True

    def redis_incr(key):
        entry = store.get(key)
        current = int(entry["value"]) if entry else 0
        new_val = current + 1
        store[key] = {"value": str(new_val).encode()}
        return new_val

    def redis_expire(key, seconds):
        pass  # TTL não simulado — não afeta a lógica dos testes

    def redis_delete(*keys):
        for k in keys:
            store.pop(k, None)

    r = MagicMock()
    r.get.side_effect = redis_get
    r.set.side_effect = redis_set
    r.incr.side_effect = redis_incr
    r.expire.side_effect = redis_expire
    r.delete.side_effect = redis_delete
    r._store = store
    return r


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cb(redis=None, threshold=FAILURE_THRESHOLD, window=FAILURE_WINDOW, timeout=RECOVERY_TIMEOUT):
    return CircuitBreaker("test", redis, failure_threshold=threshold, failure_window=window, recovery_timeout=timeout)


def _open_circuit(cb):
    """Registra falhas suficientes para abrir o circuito."""
    for _ in range(cb.failure_threshold):
        cb.on_failure()


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------

def test_circuit_opens_after_threshold_failures():
    redis = _make_redis()
    cb = _cb(redis, threshold=3)

    cb.on_failure()
    cb.on_failure()
    cb.before_call()  # ainda fechado — não levanta

    cb.on_failure()  # atinge threshold → abre
    with pytest.raises(CircuitBreakerOpenError):
        cb.before_call()


def test_circuit_blocks_calls_when_open():
    redis = _make_redis()
    cb = _cb(redis)
    _open_circuit(cb)

    with pytest.raises(CircuitBreakerOpenError):
        cb.before_call()

    # segunda chamada também bloqueada
    with pytest.raises(CircuitBreakerOpenError):
        cb.before_call()


def test_circuit_transitions_to_half_open_after_recovery_timeout():
    redis = _make_redis()
    cb = _cb(redis, timeout=1)
    _open_circuit(cb)

    with pytest.raises(CircuitBreakerOpenError):
        cb.before_call()

    # simula passagem do recovery_timeout
    past = str(time.time() - 2)
    redis._store[cb._key_opened_at] = {"value": past.encode()}

    # não deve levantar — entra em half_open e permite sonda
    cb.before_call()

    state = redis.get(cb._key_state)
    assert state == b"half_open"


def test_circuit_closes_on_successful_probe():
    redis = _make_redis()
    cb = _cb(redis, timeout=1)
    _open_circuit(cb)

    # força half_open
    past = str(time.time() - 2)
    redis._store[cb._key_opened_at] = {"value": past.encode()}
    cb.before_call()

    cb.on_success()

    # circuito fechado: chave state removida (default = closed)
    assert redis.get(cb._key_state) is None
    # contadores limpos
    assert redis.get(cb._key_failures) is None


def test_circuit_reopens_on_failed_probe():
    redis = _make_redis()
    cb = _cb(redis, timeout=1)
    _open_circuit(cb)

    # força half_open
    past = str(time.time() - 2)
    redis._store[cb._key_opened_at] = {"value": past.encode()}
    cb.before_call()

    cb.on_failure()

    state = redis.get(cb._key_state)
    assert state == b"open"

    with pytest.raises(CircuitBreakerOpenError):
        cb.before_call()


def test_on_failure_increments_and_opens_at_threshold():
    redis = _make_redis()
    cb = _cb(redis, threshold=2)

    cb.on_failure()
    # ainda fechado
    cb.before_call()

    cb.on_failure()
    # threshold atingido → open
    with pytest.raises(CircuitBreakerOpenError):
        cb.before_call()


def test_passthrough_when_redis_none():
    cb = _cb(redis=None)

    # nenhuma operação deve levantar exceção
    cb.before_call()
    cb.on_success()
    cb.on_failure()
    cb.on_failure()
    cb.before_call()  # ainda acessível — modo passthrough
