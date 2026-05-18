"""
Testes para determinar_fase_analitica() — função de domínio.

Matriz:
  - Mapeamento direto (cada TipoEvento → FaseCodigo esperada)
  - NAO_CLASSIFICADO preserva fase_atual
  - APROVACAO preserva fase_atual
  - fase_atual=None → fallback PROTOCOLO_INICIAL
  - Regressão de fase (RETORNO_INICIADORA)
"""

import pytest

from domain.classificar_evento import determinar_fase_analitica
from domain.entities.fase_codigo import FaseCodigo
from domain.entities.tipo_evento import TipoEvento


class TestDeterminarFaseMapeamentoDireto:
    @pytest.mark.parametrize(
        ("tipo", "fase_esperada"),
        [
            (TipoEvento.APRESENTACAO, FaseCodigo.PROTOCOLO_INICIAL),
            (TipoEvento.DESPACHO, FaseCodigo.PROTOCOLO_INICIAL),
            (TipoEvento.RECEBIMENTO_ORGAO, FaseCodigo.ANALISE_COMISSOES),
            (TipoEvento.DESIGNACAO_RELATOR, FaseCodigo.ANALISE_COMISSOES),
            (TipoEvento.PARECER, FaseCodigo.ANALISE_COMISSOES),
            (TipoEvento.VOTACAO_COMISSAO, FaseCodigo.ANALISE_COMISSOES),
            (TipoEvento.INCLUSAO_PAUTA, FaseCodigo.AGUARDANDO_PAUTA),
            (TipoEvento.RETIRADA_PAUTA, FaseCodigo.AGUARDANDO_PAUTA),
            (TipoEvento.VOTACAO_PLENARIO, FaseCodigo.DELIBERACAO_PLENARIO),
            (TipoEvento.REMESSA_OUTRA_CASA, FaseCodigo.TRAMITE_ENTRE_CASAS),
            (TipoEvento.RECEBIMENTO_OUTRA_CASA, FaseCodigo.REVISAO_OUTRA_CASA),
            (TipoEvento.RETORNO_INICIADORA, FaseCodigo.ANALISE_COMISSOES),
            (TipoEvento.ENVIO_EXECUTIVO, FaseCodigo.ETAPA_EXECUTIVO),
            (TipoEvento.SANCAO_OU_VETO, FaseCodigo.ENCERRADA),
            (TipoEvento.PROMULGACAO, FaseCodigo.ENCERRADA),
            (TipoEvento.ARQUIVAMENTO, FaseCodigo.ENCERRADA),
            (TipoEvento.PREJUDICIALIDADE, FaseCodigo.ENCERRADA),
            (TipoEvento.REJEICAO, FaseCodigo.ENCERRADA),
        ],
        ids=lambda v: v.value if hasattr(v, "value") else str(v),
    )
    def test_mapeamento(self, tipo, fase_esperada):
        resultado = determinar_fase_analitica(tipo, FaseCodigo.PROTOCOLO_INICIAL)
        assert resultado == fase_esperada


class TestDeterminarFaseNaoClassificado:
    def test_preserva_analise_comissoes(self):
        r = determinar_fase_analitica(
            TipoEvento.NAO_CLASSIFICADO, FaseCodigo.ANALISE_COMISSOES
        )
        assert r == FaseCodigo.ANALISE_COMISSOES

    def test_preserva_deliberacao_plenario(self):
        r = determinar_fase_analitica(
            TipoEvento.NAO_CLASSIFICADO, FaseCodigo.DELIBERACAO_PLENARIO
        )
        assert r == FaseCodigo.DELIBERACAO_PLENARIO

    def test_preserva_encerrada(self):
        r = determinar_fase_analitica(TipoEvento.NAO_CLASSIFICADO, FaseCodigo.ENCERRADA)
        assert r == FaseCodigo.ENCERRADA

    def test_fase_none_usa_fallback(self):
        r = determinar_fase_analitica(TipoEvento.NAO_CLASSIFICADO, None)
        assert r == FaseCodigo.PROTOCOLO_INICIAL


class TestDeterminarFaseAprovacao:
    def test_mantem_analise_comissoes(self):
        r = determinar_fase_analitica(
            TipoEvento.APROVACAO, FaseCodigo.ANALISE_COMISSOES
        )
        assert r == FaseCodigo.ANALISE_COMISSOES

    def test_mantem_deliberacao_plenario(self):
        r = determinar_fase_analitica(
            TipoEvento.APROVACAO, FaseCodigo.DELIBERACAO_PLENARIO
        )
        assert r == FaseCodigo.DELIBERACAO_PLENARIO

    def test_mantem_revisao_outra_casa(self):
        r = determinar_fase_analitica(
            TipoEvento.APROVACAO, FaseCodigo.REVISAO_OUTRA_CASA
        )
        assert r == FaseCodigo.REVISAO_OUTRA_CASA

    def test_fase_none_usa_fallback(self):
        r = determinar_fase_analitica(TipoEvento.APROVACAO, None)
        assert r == FaseCodigo.PROTOCOLO_INICIAL


class TestDeterminarFaseNone:
    def test_apresentacao_com_fase_none(self):
        assert (
            determinar_fase_analitica(TipoEvento.APRESENTACAO, None)
            == FaseCodigo.PROTOCOLO_INICIAL
        )

    def test_despacho_com_fase_none(self):
        assert (
            determinar_fase_analitica(TipoEvento.DESPACHO, None)
            == FaseCodigo.PROTOCOLO_INICIAL
        )

    def test_recebimento_orgao_com_fase_none(self):
        assert (
            determinar_fase_analitica(TipoEvento.RECEBIMENTO_ORGAO, None)
            == FaseCodigo.ANALISE_COMISSOES
        )


class TestDeterminarFaseRegressao:
    def test_retorno_de_revisao_para_analise(self):
        r = determinar_fase_analitica(
            TipoEvento.RETORNO_INICIADORA, FaseCodigo.REVISAO_OUTRA_CASA
        )
        assert r == FaseCodigo.ANALISE_COMISSOES

    def test_retorno_de_tramite_para_analise(self):
        r = determinar_fase_analitica(
            TipoEvento.RETORNO_INICIADORA, FaseCodigo.TRAMITE_ENTRE_CASAS
        )
        assert r == FaseCodigo.ANALISE_COMISSOES


class TestDeterminarFaseSequenciaRealista:
    def test_ciclo_completo_pl(self):
        eventos = [
            (TipoEvento.APRESENTACAO, FaseCodigo.PROTOCOLO_INICIAL),
            (TipoEvento.DESPACHO, FaseCodigo.PROTOCOLO_INICIAL),
            (TipoEvento.RECEBIMENTO_ORGAO, FaseCodigo.ANALISE_COMISSOES),
            (TipoEvento.DESIGNACAO_RELATOR, FaseCodigo.ANALISE_COMISSOES),
            (TipoEvento.PARECER, FaseCodigo.ANALISE_COMISSOES),
            (TipoEvento.VOTACAO_COMISSAO, FaseCodigo.ANALISE_COMISSOES),
            (TipoEvento.APROVACAO, FaseCodigo.ANALISE_COMISSOES),
            (TipoEvento.INCLUSAO_PAUTA, FaseCodigo.AGUARDANDO_PAUTA),
            (TipoEvento.VOTACAO_PLENARIO, FaseCodigo.DELIBERACAO_PLENARIO),
            (TipoEvento.APROVACAO, FaseCodigo.DELIBERACAO_PLENARIO),
            (TipoEvento.REMESSA_OUTRA_CASA, FaseCodigo.TRAMITE_ENTRE_CASAS),
            (TipoEvento.RECEBIMENTO_OUTRA_CASA, FaseCodigo.REVISAO_OUTRA_CASA),
            (TipoEvento.APROVACAO, FaseCodigo.REVISAO_OUTRA_CASA),
            (TipoEvento.ENVIO_EXECUTIVO, FaseCodigo.ETAPA_EXECUTIVO),
            (TipoEvento.SANCAO_OU_VETO, FaseCodigo.ENCERRADA),
        ]
        fase_atual = None
        for tipo, fase_esperada in eventos:
            fase_atual = determinar_fase_analitica(tipo, fase_atual)
            assert fase_atual == fase_esperada, (
                f"Após {tipo.value}: esperado {fase_esperada.value}, obtido {fase_atual.value}"
            )
