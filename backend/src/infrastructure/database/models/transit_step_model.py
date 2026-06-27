from datetime import datetime

from sqlmodel import Field, SQLModel


class TransitStepModel(SQLModel, table=True):
    """
    Modelo de persistência para os Passos de Trânsito entre as Casas (transit_step).
    Mapeia e consolida o trânsito da FSM para fins analíticos no banco de dados.
    """

    __tablename__ = "transit_step"

    id: int | None = Field(default=None, primary_key=True)
    proposicao_id: str = Field(
        foreign_key="proposicao.id", ondelete="CASCADE", index=True
    )
    casa: str = Field(index=True)  # "Câmara" ou "Senado"
    tipo_passo: str = Field(index=True)  # "origem", "revisora", "retorno"
    data_entrada: datetime = Field(index=True)
    data_saida: datetime | None = Field(default=None, index=True)
    duracao_dias: int = Field(default=0)
