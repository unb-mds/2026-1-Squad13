import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

FAILURE_THRESHOLD = 5
FAILURE_WINDOW = 60
RECOVERY_TIMEOUT = 120


class CircuitBreakerOpenError(Exception):
    """
    Levantada quando o circuito está aberto.
    Não é subclasse de ConnectionError — permite que o código de negócio
    distinga 'API sabidamente down' de falha de rede pontual.
    """


class CircuitBreaker:
    """
    Circuit breaker stateful com backend Redis.
    Estados: closed → open → half_open → closed.

    Se redis=None opera em modo passthrough: before_call/on_success/on_failure
    são no-ops e nenhuma chamada é bloqueada.
    """

    def __init__(
        self,
        service: str,
        redis=None,
        failure_threshold: int = FAILURE_THRESHOLD,
        failure_window: int = FAILURE_WINDOW,
        recovery_timeout: int = RECOVERY_TIMEOUT,
    ) -> None:
        self.service = service
        self.redis = redis
        self.failure_threshold = failure_threshold
        self.failure_window = failure_window
        self.recovery_timeout = recovery_timeout

        self._key_state = f"circuit:{service}:state"
        self._key_failures = f"circuit:{service}:failures"
        self._key_opened_at = f"circuit:{service}:opened_at"
        self._key_probe_lock = f"circuit:{service}:probe_lock"

    # ------------------------------------------------------------------
    # interface pública
    # ------------------------------------------------------------------

    def before_call(self) -> None:
        """
        Verifica se a chamada HTTP deve prosseguir.
        Levanta CircuitBreakerOpenError se o circuito estiver aberto
        e o recovery_timeout ainda não tiver expirado.
        """
        if self.redis is None:
            return

        try:
            state = self._get_state()

            if state == "closed":
                return

            if state == "open":
                opened_at = self._get_opened_at()
                if opened_at and (time.time() - opened_at) >= self.recovery_timeout:
                    self._set_state("half_open")
                    logger.info(
                        f"[circuit:{self.service}] open → half_open após {self.recovery_timeout}s"
                    )
                    self._acquire_probe()
                    return
                raise CircuitBreakerOpenError(
                    f"Circuito aberto para '{self.service}' — chamada bloqueada."
                )

            if state == "half_open":
                # permite apenas uma sonda por vez
                acquired = self.redis.set(
                    self._key_probe_lock, "1", nx=True, ex=30
                )
                if not acquired:
                    raise CircuitBreakerOpenError(
                        f"Circuito em half_open para '{self.service}' — sonda em andamento."
                    )

        except CircuitBreakerOpenError:
            raise
        except Exception as exc:
            logger.warning(
                f"[circuit:{self.service}] Redis indisponível em before_call — "
                f"falhar fechado. Detalhe: {exc}"
            )

    def on_success(self) -> None:
        """
        Registra sucesso. Em half_open fecha o circuito; em closed reseta falhas.
        """
        if self.redis is None:
            return

        try:
            state = self._get_state()
            if state == "half_open":
                self._reset()
                logger.info(
                    f"[circuit:{self.service}] half_open → closed após sonda bem-sucedida."
                )
            elif state == "closed":
                self.redis.delete(self._key_failures)
        except Exception as exc:
            logger.warning(
                f"[circuit:{self.service}] Redis indisponível em on_success: {exc}"
            )

    def on_failure(self) -> None:
        """
        Registra falha. Se threshold atingido abre o circuito.
        Em half_open reabre imediatamente.
        """
        if self.redis is None:
            return

        try:
            state = self._get_state()

            if state == "half_open":
                self._open()
                logger.warning(
                    f"[circuit:{self.service}] half_open → open: sonda falhou."
                )
                return

            count = self.redis.incr(self._key_failures)
            if count == 1:
                self.redis.expire(self._key_failures, self.failure_window)

            if count >= self.failure_threshold:
                self._open()
                logger.warning(
                    f"[circuit:{self.service}] closed → open após {count} falhas."
                )
        except Exception as exc:
            logger.warning(
                f"[circuit:{self.service}] Redis indisponível em on_failure: {exc}"
            )

    # ------------------------------------------------------------------
    # helpers privados
    # ------------------------------------------------------------------

    def _get_state(self) -> str:
        raw = self.redis.get(self._key_state)
        if raw is None:
            return "closed"
        return raw.decode() if isinstance(raw, bytes) else str(raw)

    def _set_state(self, state: str) -> None:
        self.redis.set(self._key_state, state)

    def _get_opened_at(self) -> Optional[float]:
        raw = self.redis.get(self._key_opened_at)
        if raw is None:
            return None
        return float(raw)

    def _open(self) -> None:
        self.redis.set(self._key_state, "open")
        self.redis.set(self._key_opened_at, str(time.time()))
        self.redis.delete(self._key_probe_lock)

    def _reset(self) -> None:
        self.redis.delete(self._key_state)
        self.redis.delete(self._key_failures)
        self.redis.delete(self._key_opened_at)
        self.redis.delete(self._key_probe_lock)

    def _acquire_probe(self) -> None:
        self.redis.set(self._key_probe_lock, "1", ex=30)
