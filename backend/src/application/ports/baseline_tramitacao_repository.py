from typing import Protocol

from domain.entities.baseline_tramitacao import BaselineTramitacao


class BaselineTramitacaoRepositoryPort(Protocol):
    """
    Interface (Port) para o repositório de Baseline de Tramitação.
    Garante o desacoplamento do domínio/aplicação com a camada de infraestrutura.
    """

    def buscar_baseline(
        self,
        escopo: str,
        tipo: str | None = None,
        regime_tramitacao: str | None = None,
        fase_codigo: str | None = None,
    ) -> BaselineTramitacao | None:
        """
        Busca um baseline de tramitação específico ou correspondente aos fallbacks.
        """
        ...

    def salvar(self, baseline: BaselineTramitacao) -> BaselineTramitacao:
        """
        Persiste ou atualiza um baseline de tramitação.
        """
        ...

    def remover_calculos_dinamicos(self) -> None:
        """
        Remove todos os registros de baseline com origem DYNAMIC_CALCULATION.
        Útil para limpar antes do recálculo diário.
        """
        ...
