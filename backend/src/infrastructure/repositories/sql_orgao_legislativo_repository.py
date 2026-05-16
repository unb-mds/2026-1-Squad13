"""
Repositório para a tabela orgaolegislativo.

Estratégia de persistência: upsert automático por (sigla, casa).
Os adapters criam/atualizam órgãos conforme encontram novas siglas.

Seed mínimo: 3 órgãos implícitos (PLEN, MESA, SECCJ).
"""

from typing import List, Optional

from sqlmodel import Session, select

from domain.entities.orgao_legislativo import (
    CasaLegislativa,
    ORGAOS_SEED,
    OrgaoLegislativo,
)


class SQLOrgaoLegislativoRepository:
    """Repositório SQL para órgãos legislativos."""

    def __init__(self, session: Session):
        self.session = session

    def buscar_ou_criar(
        self,
        sigla: str,
        casa: CasaLegislativa,
        nome: Optional[str] = None,
        id_origem: Optional[str] = None,
    ) -> OrgaoLegislativo:
        """
        Upsert por (sigla, casa).

        Se o órgão já existe, retorna o existente.
        Se não existe, cria com os dados fornecidos.
        """
        statement = select(OrgaoLegislativo).where(
            OrgaoLegislativo.sigla == sigla,
            OrgaoLegislativo.casa == casa,
        )
        existente = self.session.exec(statement).first()
        if existente is not None:
            return existente

        orgao = OrgaoLegislativo(
            sigla=sigla,
            nome=nome,
            casa=casa,
            id_origem=id_origem,
        )
        self.session.add(orgao)
        self.session.commit()
        self.session.refresh(orgao)
        return orgao

    def buscar_por_sigla(self, sigla: str) -> List[OrgaoLegislativo]:
        """Lista todos os órgãos com a sigla fornecida (pode haver um por Casa)."""
        statement = select(OrgaoLegislativo).where(OrgaoLegislativo.sigla == sigla)
        return list(self.session.exec(statement).all())

    def seed_orgaos(self) -> None:
        """
        Upsert idempotente dos órgãos mínimos de ORGAOS_SEED.

        Permite rodar o seed múltiplas vezes sem duplicar dados.
        """
        for orgao_data in ORGAOS_SEED:
            self.buscar_ou_criar(
                sigla=orgao_data["sigla"],
                casa=orgao_data["casa"],
                nome=orgao_data.get("nome"),
            )
