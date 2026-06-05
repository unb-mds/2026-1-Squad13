from datetime import date, datetime

from application.ports.fase_analitica_repository import FaseAnaliticaRepositoryPort
from domain.entities.evento_tramitacao import EventoTramitacao
from domain.value_objects.periodo_fase import PeriodoFase


class AgregarPorFaseService:
    """
    Serviço de aplicação para agrupar eventos de tramitação em períodos por fase.
    """

    def __init__(self, fase_repository: FaseAnaliticaRepositoryPort):
        self._fase_repo = fase_repository
        # Cache de fases para evitar múltiplas consultas
        todas = self._fase_repo.buscar_todas()
        self._fases_map = {f.id: f for f in todas}

    def executar(
        self,
        eventos: list[EventoTramitacao],
        proposicao_encerrada: bool = False,
        data_encerramento: date | None = None,
    ) -> list[PeriodoFase]:
        """
        Transforma lista de eventos em lista de períodos por fase.
        """
        if not eventos:
            return []

        # Garante ordenação cronológica e por progressão lógica de fase
        def get_ordem(ev: EventoTramitacao) -> int:
            fase = self._fases_map.get(ev.fase_analitica_id)
            return fase.ordem_logica if fase else 0

        eventos_ordenados = sorted(
            eventos,
            key=lambda e: (e.data_evento, get_ordem(e), e.sequencia or 0),
        )

        # Suavização: Se um evento é 'Encerrada' (ID 8) mas há eventos não-8
        # depois no mesmo dia, ele não deveria mudar a fase para 8.
        # (Provavelmente uma rejeição de emenda ou arquivamento acessório)
        fases_suavizadas = []
        for i in range(len(eventos_ordenados)):
            ev = eventos_ordenados[i]
            fase_id = ev.fase_analitica_id

            if fase_id == 8:  # ENCERRADA
                data_atual = ev.data_evento[:10]
                tem_posterior_ativa_mesmo_dia = False
                for j in range(i + 1, len(eventos_ordenados)):
                    ev_futuro = eventos_ordenados[j]
                    if ev_futuro.data_evento[:10] != data_atual:
                        break
                    if ev_futuro.fase_analitica_id not in {None, 8}:
                        tem_posterior_ativa_mesmo_dia = True
                        break

                if tem_posterior_ativa_mesmo_dia:
                    # Usa a fase anterior (ou a próxima ativa se for o primeiro)
                    fase_id = fases_suavizadas[-1] if fases_suavizadas else 1

            fases_suavizadas.append(fase_id)

        periodos: list[PeriodoFase] = []
        fase_atual_id: int | None = None
        periodo_atual: PeriodoFase | None = None
        ocorrencias_fase: dict[int, int] = {}

        hoje = date.today()

        for idx, evento in enumerate(eventos_ordenados):
            fase_evento_id = fases_suavizadas[idx]

            # Se o evento não tem fase (ex: NAO_CLASSIFICADO), ele pertence à fase anterior
            if fase_evento_id is None:
                if periodo_atual:
                    if evento.relevante:
                        periodo_atual.eventos_relevantes.append(evento)
                    # Atualiza a saída do período para o evento mais recente (mesmo irrelevante)
                    periodo_atual.data_saida = datetime.fromisoformat(
                        evento.data_evento[:10]
                    ).date()
                continue

            # Se mudou a fase ou é o primeiro evento
            if fase_evento_id != fase_atual_id:
                # Fecha o período anterior se existir
                if periodo_atual:
                    # O SPEC diz que data_saida do período anterior é a data_entrada do novo
                    # Mas para cálculo de dias, vamos usar a data do evento atual
                    data_transicao = datetime.fromisoformat(
                        evento.data_evento[:10]
                    ).date()
                    periodo_atual.data_saida = data_transicao

                    # Recalcula dias corridos do período fechado
                    periodo_atual.dias_corridos = (
                        periodo_atual.data_saida - periodo_atual.data_entrada
                    ).days

                # Abre novo período
                fase_info = self._fases_map.get(fase_evento_id)
                if not fase_info:
                    continue

                ocorrencias_fase[fase_evento_id] = (
                    ocorrencias_fase.get(fase_evento_id, 0) + 1
                )

                data_entrada = datetime.fromisoformat(evento.data_evento[:10]).date()

                periodo_atual = PeriodoFase(
                    fase_codigo=fase_info.codigo,
                    fase_nome=fase_info.nome,
                    ordem_logica=fase_info.ordem_logica,
                    data_entrada=data_entrada,
                    data_saida=None,
                    dias_corridos=0,
                    eventos_relevantes=[],
                    ocorrencia=ocorrencias_fase[fase_evento_id],
                )

                if evento.relevante:
                    periodo_atual.eventos_relevantes.append(evento)

                periodos.append(periodo_atual)
                fase_atual_id = fase_evento_id
            else:
                # Continua na mesma fase
                if periodo_atual:
                    if evento.relevante:
                        periodo_atual.eventos_relevantes.append(evento)
                    periodo_atual.data_saida = datetime.fromisoformat(
                        evento.data_evento[:10]
                    ).date()

        # Finalização do último período
        if periodo_atual:
            if proposicao_encerrada and data_encerramento:
                periodo_atual.data_saida = data_encerramento
            elif proposicao_encerrada:
                # Se não tem data_encerramento informada, usa a do último evento
                pass
            else:
                periodo_atual.data_saida = None  # Mantém None para indicar ativa

            # Cálculo final de dias
            referencia_fim = periodo_atual.data_saida or hoje
            periodo_atual.dias_corridos = (
                referencia_fim - periodo_atual.data_entrada
            ).days

        return periodos
