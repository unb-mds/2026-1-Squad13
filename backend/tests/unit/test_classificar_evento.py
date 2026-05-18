"""
Testes para classificar_tipo_evento() — função de domínio.

Matriz:
  - 19 tipos canônicos com descrições claras
  - Descrições ambíguas com múltiplos termos (prioridade correta)
  - Bordas: vazia, espaços, None, acentos, case-insensitive
"""

import pytest

from domain.classificar_evento import classificar_tipo_evento
from domain.entities.tipo_evento import TipoEvento


# ============================================================================
# Casos normais — 1 descrição clara para cada tipo canônico
# ============================================================================


class TestClassificarCasosNormais:
    """Uma descrição inequívoca para cada um dos 19 tipos."""

    def test_apresentacao(self):
        assert (
            classificar_tipo_evento("Apresentação do projeto de lei")
            == TipoEvento.APRESENTACAO
        )

    def test_despacho(self):
        assert (
            classificar_tipo_evento("Despacho inicial às comissões")
            == TipoEvento.DESPACHO
        )

    def test_recebimento_orgao(self):
        assert (
            classificar_tipo_evento("Recebimento pela CCJ")
            == TipoEvento.RECEBIMENTO_ORGAO
        )

    def test_designacao_relator(self):
        assert (
            classificar_tipo_evento("Designação de relator na comissão")
            == TipoEvento.DESIGNACAO_RELATOR
        )

    def test_parecer(self):
        assert (
            classificar_tipo_evento("Parecer favorável do relator")
            == TipoEvento.PARECER
        )

    def test_inclusao_pauta(self):
        assert (
            classificar_tipo_evento("Inclusão na pauta da sessão")
            == TipoEvento.INCLUSAO_PAUTA
        )

    def test_retirada_pauta(self):
        assert (
            classificar_tipo_evento("Retirada de pauta a pedido do autor")
            == TipoEvento.RETIRADA_PAUTA
        )

    def test_votacao_comissao(self):
        assert (
            classificar_tipo_evento("Votação na comissão de mérito")
            == TipoEvento.VOTACAO_COMISSAO
        )

    def test_votacao_plenario(self):
        assert (
            classificar_tipo_evento("Votação em plenário concluída")
            == TipoEvento.VOTACAO_PLENARIO
        )

    def test_aprovacao(self):
        assert (
            classificar_tipo_evento("Aprovada na comissão especial")
            == TipoEvento.APROVACAO
        )

    def test_rejeicao(self):
        assert classificar_tipo_evento("Rejeitada pelo plenário") == TipoEvento.REJEICAO

    def test_remessa_outra_casa(self):
        assert (
            classificar_tipo_evento("Remessa à outra Casa legislativa")
            == TipoEvento.REMESSA_OUTRA_CASA
        )

    def test_recebimento_outra_casa(self):
        assert (
            classificar_tipo_evento("Recebimento pela outra Casa")
            == TipoEvento.RECEBIMENTO_OUTRA_CASA
        )

    def test_retorno_iniciadora(self):
        assert (
            classificar_tipo_evento("Retorno à casa iniciadora para revisão")
            == TipoEvento.RETORNO_INICIADORA
        )

    def test_arquivamento(self):
        assert (
            classificar_tipo_evento("Arquivamento definitivo")
            == TipoEvento.ARQUIVAMENTO
        )

    def test_prejudicialidade(self):
        assert (
            classificar_tipo_evento("Declarada prejudicada pela Mesa")
            == TipoEvento.PREJUDICIALIDADE
        )

    def test_envio_executivo(self):
        assert (
            classificar_tipo_evento("Enviado ao Poder Executivo para sanção")
            == TipoEvento.ENVIO_EXECUTIVO
        )

    def test_sancao_ou_veto(self):
        assert (
            classificar_tipo_evento("Sancionada pelo Presidente")
            == TipoEvento.SANCAO_OU_VETO
        )

    def test_promulgacao(self):
        assert (
            classificar_tipo_evento("Promulgação da emenda constitucional")
            == TipoEvento.PROMULGACAO
        )


# ============================================================================
# Casos ambíguos — descrições com múltiplos termos competidores
# ============================================================================


class TestClassificarCasosAmbiguos:
    """Verifica que a prioridade dos patterns resolve ambiguidades."""

    def test_aprovada_e_remetida_prioriza_aprovacao(self):
        """'Aprovada' vem antes de 'remetid' na prioridade."""
        resultado = classificar_tipo_evento("Aprovada e remetida ao Senado Federal")
        assert resultado == TipoEvento.APROVACAO

    def test_parecer_aprovado_prioriza_parecer(self):
        """'Parecer' vem antes de 'aprovad' na prioridade."""
        resultado = classificar_tipo_evento("Parecer do relator aprovado pela Comissão")
        assert resultado == TipoEvento.PARECER

    def test_sancionada_e_promulgada_prioriza_promulgacao(self):
        """'Promulgação' é mais específico e vem primeiro."""
        resultado = classificar_tipo_evento("Promulgação após sanção presidencial")
        assert resultado == TipoEvento.PROMULGACAO

    def test_veto_parcial_classifica_como_sancao_ou_veto(self):
        resultado = classificar_tipo_evento("Veto parcial do Executivo")
        assert resultado == TipoEvento.SANCAO_OU_VETO

    def test_arquivada_e_prejudicada_prioriza_prejudicialidade(self):
        """'Prejudicad' vem antes de 'arquiv' na prioridade."""
        resultado = classificar_tipo_evento("Declarada prejudicada e arquivada")
        assert resultado == TipoEvento.PREJUDICIALIDADE

    def test_distribuicao_as_comissoes_classifica_como_despacho(self):
        """'Distribuição' casa com DESPACHO."""
        resultado = classificar_tipo_evento("Distribuição às comissões permanentes")
        assert resultado == TipoEvento.DESPACHO

    def test_voto_relator_classifica_como_parecer(self):
        resultado = classificar_tipo_evento("Voto do relator pela aprovação")
        assert resultado == TipoEvento.PARECER

    def test_leitura_classifica_como_apresentacao(self):
        resultado = classificar_tipo_evento("Leitura em plenário")
        assert resultado == TipoEvento.APRESENTACAO

    def test_pronta_para_pauta_classifica_como_inclusao(self):
        resultado = classificar_tipo_evento("Pronta para pauta na comissão")
        assert resultado == TipoEvento.INCLUSAO_PAUTA

    def test_enviado_ao_senado_classifica_como_remessa(self):
        resultado = classificar_tipo_evento("Enviado ao Senado Federal para revisão")
        assert resultado == TipoEvento.REMESSA_OUTRA_CASA

    def test_remetida_a_camara_classifica_como_remessa(self):
        resultado = classificar_tipo_evento("Remetida à Câmara dos Deputados")
        assert resultado == TipoEvento.REMESSA_OUTRA_CASA

    def test_encaminhada_a_comissao_classifica_como_recebimento(self):
        resultado = classificar_tipo_evento(
            "Encaminhada à Comissão de Constituição e Justiça"
        )
        assert resultado == TipoEvento.RECEBIMENTO_ORGAO

    def test_remetida_ao_presidente_classifica_como_envio_executivo(self):
        resultado = classificar_tipo_evento("Remetida ao Presidente da República")
        assert resultado == TipoEvento.ENVIO_EXECUTIVO


# ============================================================================
# Casos de borda
# ============================================================================


class TestClassificarCasosBorda:
    """Casos extremos: vazios, None, acentos, casing."""

    def test_string_vazia_retorna_nao_classificado(self):
        assert classificar_tipo_evento("") == TipoEvento.NAO_CLASSIFICADO

    def test_somente_espacos_retorna_nao_classificado(self):
        assert classificar_tipo_evento("   ") == TipoEvento.NAO_CLASSIFICADO

    def test_none_levanta_type_error(self):
        with pytest.raises(TypeError, match="descricao deve ser str"):
            classificar_tipo_evento(None)  # type: ignore[arg-type]

    def test_numero_levanta_type_error(self):
        with pytest.raises(TypeError, match="descricao deve ser str"):
            classificar_tipo_evento(42)  # type: ignore[arg-type]

    def test_texto_desconhecido_retorna_nao_classificado(self):
        assert (
            classificar_tipo_evento("Lorem ipsum dolor sit amet")
            == TipoEvento.NAO_CLASSIFICADO
        )

    def test_case_insensitive_maiusculas(self):
        assert (
            classificar_tipo_evento("ARQUIVAMENTO DEFINITIVO")
            == TipoEvento.ARQUIVAMENTO
        )

    def test_case_insensitive_minusculas(self):
        assert (
            classificar_tipo_evento("arquivamento definitivo")
            == TipoEvento.ARQUIVAMENTO
        )

    def test_case_insensitive_misto(self):
        assert (
            classificar_tipo_evento("Arquivamento Definitivo")
            == TipoEvento.ARQUIVAMENTO
        )

    def test_acentos_preservados(self):
        """Verifica que acentos não impedem classificação."""
        assert (
            classificar_tipo_evento("Votação em plenário")
            == TipoEvento.VOTACAO_PLENARIO
        )

    def test_acento_na_sancao(self):
        assert (
            classificar_tipo_evento("Sanção presidencial") == TipoEvento.SANCAO_OU_VETO
        )

    def test_descricao_muito_longa(self):
        """Descrição longa com keyword no meio deve funcionar."""
        texto = "a" * 500 + " arquivamento " + "b" * 500
        assert classificar_tipo_evento(texto) == TipoEvento.ARQUIVAMENTO

    def test_descricao_com_quebra_de_linha(self):
        resultado = classificar_tipo_evento("Apresentação\ndo projeto de lei")
        assert resultado == TipoEvento.APRESENTACAO
