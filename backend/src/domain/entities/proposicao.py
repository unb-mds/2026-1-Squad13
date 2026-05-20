from datetime import date, datetime

from sqlmodel import SQLModel

from domain.constants import LIMITE_DIAS_ATRASO


class Proposicao(SQLModel):
    """
    Entidade de Domínio Pura.
    Representa uma Proposição Legislativa (PL, PEC, etc).
    Não possui dependências diretas de persistência (table=True).
    """

    id: str | None = None
    tipo: str | None = None
    numero: str | None = None
    ano: int | None = None
    ementa: str | None = None
    ementa_resumida: str | None = None
    autor: str | None = None
    uf_autor: str | None = None
    orgao_origem: str | None = None
    status: str | None = None
    orgao_atual: str | None = None
    data_apresentacao: str | None = None
    data_ultima_movimentacao: str | None = None
    tempo_total_dias: int | None = 0
    tem_atraso: bool | None = False
    tem_previsao_ia: bool | None = False
    link_oficial: str | None = None
    data_encerramento: str | None = None
    previsao_aprovacao_dias: int | None = None
    tags: list[str] = []

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
            self.tem_atraso = self.tempo_total_dias > LIMITE_DIAS_ATRASO
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
        """Retorna True se o tempo total de tramitação for superior a LIMITE_DIAS_ATRASO dias."""
        return (self.tempo_total_dias or 0) > LIMITE_DIAS_ATRASO
