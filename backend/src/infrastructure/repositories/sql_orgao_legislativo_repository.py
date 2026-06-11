"""
Repositório para a tabela orgaolegislativo.

Estratégia de persistência: upsert automático por (sigla, casa).
Os adapters criam/atualizam órgãos conforme encontram novas siglas.

Seed mínimo: 3 órgãos implícitos (PLEN, MESA, SECCJ).
"""

from typing import List, Optional

from sqlmodel import Session, select

from domain.entities.orgao_legislativo import (
    ORGAOS_SEED,
    CasaLegislativa,
    OrgaoLegislativo,
)
from infrastructure.database.models.orgao_legislativo_model import OrgaoLegislativoModel


class SQLOrgaoLegislativoRepository:
    """Repositório SQL para órgãos legislativos."""

    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: OrgaoLegislativoModel) -> OrgaoLegislativo:
        return OrgaoLegislativo.model_validate(model.model_dump())

    def _to_model(self, entity: OrgaoLegislativo) -> OrgaoLegislativoModel:
        return OrgaoLegislativoModel.model_validate(entity.model_dump())

    def buscar_ou_criar(
        self,
        sigla: str,
        casa: CasaLegislativa,
        nome: Optional[str] = None,
        id_origem: Optional[str] = None,
    ) -> OrgaoLegislativo:
        """
        Upsert por (sigla, casa).
        """
        statement = select(OrgaoLegislativoModel).where(
            OrgaoLegislativoModel.sigla == sigla,
            OrgaoLegislativoModel.casa == casa,
        )
        model = self.session.exec(statement).first()
        if model is not None:
            return self._to_entity(model)

        model = OrgaoLegislativoModel(
            sigla=sigla,
            nome=nome,
            casa=casa,
            id_origem=id_origem,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def buscar_por_sigla(self, sigla: str) -> List[OrgaoLegislativo]:
        """Lista todos os órgãos com a sigla fornecida (pode haver um por Casa)."""
        statement = select(OrgaoLegislativoModel).where(
            OrgaoLegislativoModel.sigla == sigla
        )
        models = self.session.exec(statement).all()
        return [self._to_entity(m) for m in models]

    def seed_orgaos(self) -> None:
        """
        Upsert idempotente dos órgãos mínimos de ORGAOS_SEED.
        """
        for orgao_data in ORGAOS_SEED:
            self.buscar_ou_criar(
                sigla=orgao_data["sigla"],
                casa=orgao_data["casa"],
                nome=orgao_data.get("nome"),
            )
