from typing import Protocol

from domain.entities.orgao_legislativo import CasaLegislativa, OrgaoLegislativo


class OrgaoLegislativoRepositoryPort(Protocol):
    """
    Interface (Port) para o repositório de Órgãos Legislativos.
    """

    def buscar_ou_criar(
        self,
        sigla: str,
        casa: CasaLegislativa,
        nome: str | None = None,
        id_origem: str | None = None,
    ) -> OrgaoLegislativo:
        """Upsert por (sigla, casa) de um órgão legislativo."""
        ...

    def buscar_por_sigla(self, sigla: str) -> list[OrgaoLegislativo]:
        """Lista todos os órgãos com a sigla fornecida."""
        ...

    def seed_orgaos(self) -> None:
        """Executa o seed idempotente de órgãos."""
        ...
