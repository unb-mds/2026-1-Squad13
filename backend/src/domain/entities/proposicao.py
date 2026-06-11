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
    status_original: str | None = None
    orgao_atual: str | None = None
    data_apresentacao: str | None = None
    data_ultima_movimentacao: str | None = None
    tempo_total_dias: int | None = 0
    tem_atraso: bool | None = False
    tem_previsao_ia: bool | None = False
    link_oficial: str | None = None
    data_encerramento: str | None = None
    previsao_aprovacao_dias: int | None = None
    indice_atraso_relativo: float | None = None
    indice_atraso_fase_atual: float | None = None
    indice_espera_improdutiva: float | None = None
    status_atraso: str | None = None
    dias_decorridos_total: int | None = None
    dias_esperados_total: int | None = None
    baseline_grupo_id: str | None = None
    data_calculo_metricas: datetime | None = None
    regime_tramitacao: str | None = None
    tags: list[str] = []
    numero_assinaturas: int | None = 0
    numero_emendas: int | None = 0
    autor_e_poder_executivo: bool | None = False
    tema_economico: bool | None = False

    def normalizar_campo_status(self):
        """Normaliza o campo status para um dos 6 valores canônicos do domínio."""
        # Mantém retrocompatibilidade se status_original não estiver preenchido, mas status estiver
        if not self.status_original and self.status:
            self.status_original = self.status

        if not self.status_original or self.status_original.lower() == "sem status":
            self.status = "Em Tramitação"
            if not self.status_original:
                self.status_original = "Sem status"
            return

        raw = self.status_original.upper()

        # 1. Sancionada / Concluída
        if "NORMA JURÍDICA" in raw or "SANCIONAD" in raw:
            self.status = "Sancionada"
            return

        # 2. Vetada
        if "VETAD" in raw:
            self.status = "Vetada"
            return

        # 3. Arquivada / Rejeitada / Apensada
        if (
            "REJEITAD" in raw
            or "ARQUIVAD" in raw
            or "PREJUDICAD" in raw
            or "RETIRAD" in raw
            or "APENSAD" in raw
        ):
            self.status = "Arquivada"
            return

        # 4. Aprovada
        if "APROVAD" in raw:
            self.status = "Aprovada"
            return

        # 5. Em Pauta
        if "PAUTA" in raw:
            self.status = "Em Pauta"
            return

        # 6. Em Tramitação (fallback para todos os outros andamentos ativos)
        self.status = "Em Tramitação"

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

    @property
    def cobertura_dados(self) -> int:
        """Calcula a cobertura de dados da proposição."""
        campos_validar = [
            self.tipo,
            self.numero,
            self.ano,
            self.ementa,
            self.autor,
            self.orgao_origem,
            self.status,
            self.orgao_atual,
            self.data_apresentacao,
            self.data_ultima_movimentacao,
            self.link_oficial,
            self.regime_tramitacao,
            self.numero_emendas,
        ]
        preenchidos = sum(
            1 for c in campos_validar if c is not None and str(c).strip() != ""
        )
        proporcao = preenchidos / len(campos_validar)
        cobertura = 70 + int(proporcao * 25)
        if self.tags:
            cobertura += 5
        return min(cobertura, 100)

    @property
    def confiabilidade(self) -> str:
        """Calcula o nível de confiabilidade baseado na cobertura de dados."""
        cob = self.cobertura_dados
        if cob >= 90:
            return "alta"
        elif cob >= 70:
            return "media"
        else:
            return "baixa"
