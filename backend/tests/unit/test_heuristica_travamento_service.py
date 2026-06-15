from domain.entities.motivo_travamento import MotivoTravamentoEnum
from domain.services.heuristica_travamento_service import HeuristicaTravamentoService


def test_classificar_motivo_travamento_vinculada():
    texto = "Proposição apensada ao PL 1234/2026."
    res = HeuristicaTravamentoService.classificar_motivo_travamento(texto)
    assert res == MotivoTravamentoEnum.VINCULADA


def test_classificar_motivo_travamento_sobrestado():
    texto = "Prazo suspenso da tramitação devido a recesso parlamentar."
    res = HeuristicaTravamentoService.classificar_motivo_travamento(texto)
    assert res == MotivoTravamentoEnum.SOBRESTADO


def test_classificar_motivo_travamento_quorum():
    texto = "Sessão prejudicada por falta de quórum deliberativo."
    res = HeuristicaTravamentoService.classificar_motivo_travamento(texto)
    assert res == MotivoTravamentoEnum.QUORUM


def test_classificar_motivo_travamento_parecer_divergente():
    texto = "Apresentado voto em separado pelo deputado relator."
    res = HeuristicaTravamentoService.classificar_motivo_travamento(texto)
    assert res == MotivoTravamentoEnum.PARECER_DIVERGENTE


def test_classificar_motivo_travamento_prioridade_presidente():
    texto = "Retido pela mesa diretora aguardando decisão da presidência."
    res = HeuristicaTravamentoService.classificar_motivo_travamento(texto)
    assert res == MotivoTravamentoEnum.PRIORIDADE_PRESIDENTE


def test_classificar_motivo_travamento_outro():
    texto = "Aguardando envio de resposta do ofício."
    res = HeuristicaTravamentoService.classificar_motivo_travamento(texto)
    assert res == MotivoTravamentoEnum.OUTRO


def test_classificar_motivo_travamento_vazio():
    res = HeuristicaTravamentoService.classificar_motivo_travamento("")
    assert res == MotivoTravamentoEnum.OUTRO
