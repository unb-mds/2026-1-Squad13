from sqlmodel import SQLModel, Field
from typing import Optional, List
from sqlalchemy import Column, JSON
from datetime import datetime, date


class Proposicao(SQLModel, table=True):
    """
    Entidade de Domínio e Modelo de Banco de Dados.
    Representa uma Proposição Legislativa (PL, PEC, etc).
    Combina a estrutura robusta da 'main' com a persistência da 'develop'.
    """

    id: Optional[str] = Field(default=None, primary_key=True)
    tipo: str
    numero: str
    ano: int
    ementa: str
    ementa_resumida: Optional[str] = None
    autor: str
    uf_autor: Optional[str] = None
    orgao_origem: Optional[str] = None
    status: str
    orgao_atual: str
    data_apresentacao: str
    data_ultima_movimentacao: str
    tempo_total_dias: Optional[int] = 0
    tem_atraso: Optional[bool] = False
    tem_previsao_ia: Optional[bool] = False
    link_oficial: Optional[str] = None
    data_encerramento: Optional[str] = None
    previsao_aprovacao_dias: Optional[int] = None

    # Armazenar lista como JSON no Postgres
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))

    def normalizar_campo_status(self):
        """Normaliza o campo status para algo mais conciso e legível."""
        if not self.status or self.status.lower() == "sem status":
            self.status = "Em Tramitação"
            return

        raw = self.status.upper()

        # Mapeamento de termos prioritários (conclusão)
        if "NORMA JURÍDICA" in raw:
            self.status = "Concluída (Lei)"
            return
        if "SANCIONAD" in raw:
            self.status = "Sancionada"
            return
        if "VETAD" in raw:
            self.status = "Vetada"
            return
        if (
            "REJEITAD" in raw
            or "ARQUIVAD" in raw
            or "PREJUDICAD" in raw
            or "RETIRAD" in raw
        ):
            self.status = "Arquivada"
            return
        if "APROVAD" in raw:
            self.status = "Aprovada"
            return

        # Status de tramitação ativa
        if "PAUTA" in raw:
            self.status = "Em Pauta"
            return
        if "RELATOR" in raw:
            self.status = "Em Relatoria"
            return
        if "AGUARDANDO" in raw:
            self.status = "Aguardando"
            return
        if (
            "RECEBIMENTO" in raw
            or "ENCAMINHAD" in raw
            or "DESPACHO" in raw
            or "DISTRIBUIÇÃO" in raw
        ):
            self.status = "Em Tramitação"
            return

        # Se for muito longo e não casou com nada, corta de forma inteligente
        if len(self.status) > 50:
            self.status = self.status[:47].strip() + "..."

    def atualizar_metricas(self):
        """Calcula métricas temporais baseadas nas datas da proposição."""
        if not self.data_apresentacao:
            return

        try:
            # Formatos podem variar entre APIs (T ou espaço)
            # Câmara: 2020-02-04T13:26
            # Senado: 2021-09-30
            fmt = "%Y-%m-%d"
            data_apresentacao = datetime.strptime(
                self.data_apresentacao[:10], fmt
            ).date()

            if self.data_encerramento:
                data_fim = datetime.strptime(self.data_encerramento[:10], fmt).date()
            else:
                data_fim = date.today()

            delta = data_fim - data_apresentacao
            self.tempo_total_dias = max(0, delta.days)
            self.tem_atraso = self.tempo_total_dias > 180
        except Exception:
            # Em caso de erro na data, mantém valores padrão
            pass

    @property
    def nome_canonico(self) -> str:
        """Exemplo: PL 123/2024"""
        return f"{self.tipo} {self.numero}/{self.ano}"

    @property
    def codigo_normalizado(self) -> str:
        """Exemplo: PL-123-2024"""
        return f"{self.tipo}-{self.numero}-{self.ano}"

    @property
    def atraso_critico(self) -> bool:
        """Retorna True se o tempo total de tramitação for superior a 180 dias."""
        return (self.tempo_total_dias or 0) > 180
