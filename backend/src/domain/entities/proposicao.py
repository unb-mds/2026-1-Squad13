from datetime import date, datetime
from typing import List, Optional

from sqlmodel import SQLModel


class Proposicao(SQLModel):
    """
    Entidade de Domínio Pura.
    Representa uma Proposição Legislativa (PL, PEC, etc).
    Não possui dependências diretas de persistência (table=True).
    """

    id: Optional[str] = None
    tipo: Optional[str] = None
    numero: Optional[str] = None
    ano: Optional[int] = None
    ementa: Optional[str] = None
    ementa_resumida: Optional[str] = None
    autor: Optional[str] = None
    uf_autor: Optional[str] = None
    orgao_origem: Optional[str] = None
    status: Optional[str] = None
    orgao_atual: Optional[str] = None
    data_apresentacao: Optional[str] = None
    data_ultima_movimentacao: Optional[str] = None
    tempo_total_dias: Optional[int] = 0
    tem_atraso: Optional[bool] = False
    tem_previsao_ia: Optional[bool] = False
    link_oficial: Optional[str] = None
    data_encerramento: Optional[str] = None
    previsao_aprovacao_dias: Optional[int] = None
    tags: List[str] = []
    numero_emendas: Optional[int] = 0

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
        if "APENSAD" in raw:
            self.status = "Arquivada (Apensada)"
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
