from sqlmodel import SQLModel, Field
from typing import Optional


class Tramitacao(SQLModel, table=True):
    """
    Representa uma movimentação ou tramitação de uma proposição.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    proposicao_id: str = Field(foreign_key="proposicao.id", index=True)
    data_hora: str
    sequencia: int
    sigla_orgao: str
    descricao_orgao: Optional[str] = None
    descricao_tramitacao: str
    despacho: Optional[str] = None
    status: Optional[str] = None

    @property
    def data_formatada(self) -> str:
        """Retorna apenas a data em formato YYYY-MM-DD."""
        return self.data_hora[:10]

    def normalizar(self):
        """Normaliza as descrições e status para o formato 'Sentence case'."""

        def _fmt(texto: Optional[str]) -> Optional[str]:
            if not texto:
                return texto
            # Se estiver tudo em maiúsculo, converte para capitalizado
            if texto.isupper():
                return texto.capitalize()
            return texto

        self.descricao_tramitacao = _fmt(self.descricao_tramitacao) or ""
        self.status = _fmt(self.status)
        self.descricao_orgao = _fmt(self.descricao_orgao)
