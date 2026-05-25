from datetime import date, datetime

from domain.entities.evento_tramitacao import EventoTramitacao
from domain.entities.tipo_evento import TipoEvento


class CalcularMetricasService:
    """
    Serviço de domínio puro para cálculo de métricas de atraso legislativo.
    Livre de dependências de banco de dados ou infraestrutura.
    """

    TERMINAIS = {
        TipoEvento.APROVACAO.value,
        TipoEvento.REJEICAO.value,
        TipoEvento.ARQUIVAMENTO.value,
        TipoEvento.PREJUDICIALIDADE.value,
        TipoEvento.SANCAO_OU_VETO.value,
        TipoEvento.PROMULGACAO.value,
    }

    @staticmethod
    def obter_decorrido_e_encerramento(
        data_apresentacao_str: str | None,
        eventos: list[EventoTramitacao],
    ) -> tuple[int, str | None]:
        """
        Determina os dias decorridos desde a apresentação e a data de encerramento, se aplicável.
        """
        if not data_apresentacao_str:
            return 0, None

        try:
            fmt = "%Y-%m-%d"
            data_apresentacao = datetime.strptime(
                data_apresentacao_str[:10], fmt
            ).date()
        except ValueError:
            return 0, None

        # Procura por um evento terminal para marcar o encerramento
        ultimo_evento_terminal = None
        for e in reversed(eventos):
            if e.tipo_evento in CalcularMetricasService.TERMINAIS:
                ultimo_evento_terminal = e
                break

        hoje = date.today()
        if ultimo_evento_terminal:
            try:
                data_fim = datetime.strptime(
                    ultimo_evento_terminal.data_evento[:10], fmt
                ).date()
                data_encerramento = data_fim.isoformat()
            except ValueError:
                data_fim = hoje
                data_encerramento = None
        else:
            data_fim = hoje
            data_encerramento = None

        delta = data_fim - data_apresentacao
        return max(0, delta.days), data_encerramento

    @staticmethod
    def calcular_iar(tempo_decorrido: int, mediana_esperada: int) -> float | None:
        """Calcula o Índice de Atraso Relativo (IAR)."""
        if mediana_esperada <= 0:
            return None
        return round(tempo_decorrido / mediana_esperada, 4)

    @staticmethod
    def classificar_status_atraso(iar: float | None) -> str:
        """Classifica o status de atraso conforme as faixas de IAR."""
        if iar is None:
            return "INSUFICIENTE_BASELINE"
        if iar < 1.0:
            return "NO_PRAZO"
        if iar < 1.5:
            return "ATENCAO"
        if iar < 2.5:
            return "ATRASADA"
        return "CRITICA"

    @staticmethod
    def calcular_iei(eventos: list[EventoTramitacao], tempo_decorrido: int) -> float:
        """Calcula o Índice de Espera Improdutiva (IEI)."""
        if tempo_decorrido <= 0:
            return 0.0

        tempo_improdutivo = 0
        for e in eventos:
            if not e.deliberativo and not e.mudou_fase and not e.mudou_orgao:
                tempo_improdutivo += e.dias_na_etapa or 0

        iei = tempo_improdutivo / tempo_decorrido
        return round(max(0.0, min(1.0, iei)), 4)

    @staticmethod
    def obter_data_entrada_fase_atual(
        data_apresentacao_str: str | None,
        eventos: list[EventoTramitacao],
    ) -> tuple[int | None, str | None]:
        """
        Retorna o fase_analitica_id atual e a data de entrada na fase atual (início da ocorrência ativa).
        """
        # Filtra apenas eventos que possuem fase definida
        eventos_com_fase = [e for e in eventos if e.fase_analitica_id is not None]

        if not eventos_com_fase:
            return None, data_apresentacao_str

        ultimo_evento = eventos_com_fase[-1]
        fase_atual_id = ultimo_evento.fase_analitica_id

        # Rastreia de trás para frente para encontrar o primeiro evento contínuo nesta fase
        data_entrada = ultimo_evento.data_evento
        for e in reversed(eventos_com_fase):
            if e.fase_analitica_id == fase_atual_id:
                data_entrada = e.data_evento
            else:
                break

        return fase_atual_id, data_entrada

    @staticmethod
    def calcular_iaf(
        data_entrada_fase_str: str | None,
        mediana_esperada_fase: int,
        data_encerramento: str | None,
    ) -> float | None:
        """Calcula o Índice de Atraso da Fase Atual (IAF)."""
        if data_encerramento is not None:
            # Proposição encerrada não possui fase atual ativa
            return None

        if not data_entrada_fase_str or mediana_esperada_fase <= 0:
            return None

        try:
            fmt = "%Y-%m-%d"
            data_entrada = datetime.strptime(data_entrada_fase_str[:10], fmt).date()
        except ValueError:
            return None

        hoje = date.today()
        dias_na_fase = (hoje - data_entrada).days
        return round(max(0, dias_na_fase) / mediana_esperada_fase, 4)
