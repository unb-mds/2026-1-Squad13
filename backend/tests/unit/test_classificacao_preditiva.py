import pytest

from domain.classificacao_preditiva import (
    classificar_tema_economico,
    identificar_autor_executivo,
)


class TestClassificacaoPreditiva:
    """
    Testes de unidade minuciosos para a lógica de classificação de domínio.
    Garante que as regras de negócio preditivas sejam precisas e resilientes.
    """

    @pytest.mark.parametrize(
        "ementa, esperado",
        [
            # Casos positivos: Palavras-chave exatas e variações
            ("Dispõe sobre a instituição de novo tributo federal", True),
            ("Altera a alíquota do imposto de renda", True),
            ("Reforma o sistema tributário nacional", True),
            ("Define diretrizes para o orçamento da união", True),
            ("Estabelece normas de responsabilidade fiscal", True),
            ("Cria incentivos para a economia criativa", True),
            ("Trata da receita pública e despesas", True),
            ("Institui a taxa de iluminação pública", True),
            ("Altera o PPA, LDO e a LOA", True),
            # Casos positivos: Acentuação e Case Insensitive
            ("EMENTA: REFORMA ECONOMICA", True),
            ("ementa: reforma econômica", True),
            ("Sobre o orcamento e financas", True),  # Sem acento (comum em APIs)
            ("TRIBUTARIO E FINANCEIRO", True),
            # Casos positivos: Siglas de impostos
            ("Altera o ICMS e o IPI", True),
            ("Regulamenta o ISS e o IPTU", True),
            ("Sobre a COFINS e o PIS/PASEP", True),
            ("Incidência de IRF e IPVA", True),
            # Casos negativos: Ementas que não devem ser classificadas como economia
            ("Dispõe sobre a proteção do meio ambiente", False),
            ("Institui o dia nacional do café", False),
            ("Altera o código de trânsito brasileiro", False),
            ("Regulamenta a profissão de engenheiro", False),
            ("Cria o parque nacional da Chapada", False),
            ("Trata de direitos humanos e cidadania", False),
            ("Saúde pública e saneamento básico", False),
            # Casos de borda
            ("", False),
            (None, False),
            ("Economia", True),  # Palavra única
            ("Fiscal.", True),  # Com pontuação
            ("Incentivo fiscal-econômico", True),  # Com hífen
            (
                "Não econômico",
                True,
            ),  # Cuidado: contém a keyword. No MVP aceitamos falsos positivos simples.
        ],
    )
    def test_classificar_tema_economico(self, ementa, esperado):
        """Valida a detecção de temas econômicos por keywords."""
        assert classificar_tema_economico(ementa) == esperado

    @pytest.mark.parametrize(
        "autor, esperado",
        [
            # Casos positivos
            ("Poder Executivo", True),
            ("PRESIDENTE DA REPÚBLICA", True),
            ("Ministério da Fazenda (Poder Executivo)", True),
            ("Poder Executivo - Presidência", True),
            ("Poder executivo", True),  # Case insensitive
            ("presidente", True),  # Case insensitive parcial
            # Casos negativos
            ("Deputado Federal João Silva", False),
            ("Senador Rodrigo Pacheco", False),
            ("Comissão de Constituição e Justiça", False),
            ("Tribunal de Contas da União", False),
            ("Poder Legislativo", False),
            ("Sociedade Civil", False),
            ("Não informado", False),
            # Casos de borda
            ("", False),
            (None, False),
            (
                "Executivo",
                False,
            ),  # Muito genérico, não deve passar sem "Poder" ou "Presidente"
        ],
    )
    def test_identificar_autor_executivo(self, autor, esperado):
        """Valida a identificação de autores do Poder Executivo."""
        assert identificar_autor_executivo(autor) == esperado

    def test_classificar_tema_economico_robustez_acentuacao(self):
        """Garante que a lógica ignore diferenças sutis de encoding/acentuação se possível."""
        # A implementação atual usa .lower() e strings fixas com/sem acento
        assert classificar_tema_economico("Finanças") is True
        assert classificar_tema_economico("Financas") is True
        assert classificar_tema_economico("ORÇAMENTO") is True
        assert classificar_tema_economico("ORCAMENTO") is True
