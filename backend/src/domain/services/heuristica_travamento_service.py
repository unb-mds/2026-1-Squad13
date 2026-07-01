from domain.entities.motivo_travamento import MotivoTravamentoEnum


class HeuristicaTravamentoService:
    """
    Serviço de domínio puro para detectar o motivo de travamento jurídico
    de uma proposição baseando-se no mapeamento lexical do andamento.
    """

    @staticmethod
    def classificar_motivo_travamento(texto: str) -> MotivoTravamentoEnum:
        if not texto:
            return MotivoTravamentoEnum.OUTRO

        raw = texto.lower()

        # 1. VINCULADA (apensados, tramitação em conjunto)
        if any(
            w in raw
            for w in [
                "apensad",
                "tramitacão em conjunto",
                "tramitacao em conjunto",
                "apensamento",
            ]
        ):
            return MotivoTravamentoEnum.VINCULADA

        # 2. SOBRESTADO
        if any(
            w in raw
            for w in [
                "sobrestad",
                "sobrestamento",
                "prazo suspenso",
                "suspensao do prazo",
                "suspensão do prazo",
            ]
        ):
            return MotivoTravamentoEnum.SOBRESTADO

        # 3. QUORUM
        if any(
            w in raw
            for w in [
                "quorum",
                "quórum",
                "falta de quor",
                "sem deliberacao por falta",
            ]
        ):
            return MotivoTravamentoEnum.QUORUM

        # 4. PARECER_DIVERGENTE
        if any(
            w in raw
            for w in [
                "voto em separado",
                "parecer divergente",
                "voto contrario",
                "voto contrário",
            ]
        ):
            return MotivoTravamentoEnum.PARECER_DIVERGENTE

        # 5. PRIORIDADE_PRESIDENTE
        if any(
            w in raw
            for w in [
                "prioridade do presidente",
                "retido pela mesa",
                "mesa diretora",
                "decisao da presidencia",
                "decisão da presidência",
            ]
        ):
            return MotivoTravamentoEnum.PRIORIDADE_PRESIDENTE

        return MotivoTravamentoEnum.OUTRO
