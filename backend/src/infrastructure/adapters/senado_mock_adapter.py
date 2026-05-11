from domain.entities.proposicao import Proposicao
from infrastructure.adapters.base_adapter import ProposicaoAdapter


class SenadoMockAdapter(ProposicaoAdapter):
    """Adapter mock da API do Senado Federal.

    Normaliza dados no formato do Senado (matérias) para a entidade de domínio Proposicao.
    O Senado chama proposições de "matérias" — a normalização ocorre aqui, mantendo
    o restante do sistema desconhecente dessa diferença.
    Substitua por SenadoAdapter quando a integração real for implementada.
    """

    def buscar(self) -> list[Proposicao]:
        return [
            Proposicao(
                id="sen-1",
                tipo="PLP",
                numero="68",
                ano=2024,
                ementa="Regulamenta a reforma tributária aprovada pela Emenda Constitucional nº 132, de 2023, instituindo o Imposto sobre Bens e Serviços (IBS) e a Contribuição sobre Bens e Serviços (CBS).",
                ementa_resumida="Regulamentação da reforma tributária — IBS e CBS",
                autor="Poder Executivo",
                orgao_origem="Senado Federal",
                status="Em tramitação",
                orgao_atual="CAE",
                data_apresentacao="2024-04-25",
                data_ultima_movimentacao="2024-12-10",
                tempo_total_dias=229,
                tem_atraso=False,
                tem_previsao_ia=True,
                previsao_aprovacao_dias=90,
                tags=["tributário", "reforma tributária", "IBS", "CBS"],
            ),
            Proposicao(
                id="sen-2",
                tipo="PL",
                numero="2630",
                ano=2020,
                ementa="Institui a Lei Brasileira de Liberdade, Responsabilidade e Transparência na Internet, estabelecendo regras para moderação de conteúdo em redes sociais.",
                ementa_resumida="Lei das fake news — regulação de redes sociais",
                autor="Alessandro Vieira",
                orgao_origem="Senado Federal",
                status="Aguardando votação",
                orgao_atual="Plenário",
                data_apresentacao="2020-06-30",
                data_ultima_movimentacao="2024-10-01",
                tempo_total_dias=1555,
                tem_atraso=True,
                tem_previsao_ia=False,
                tags=["internet", "fake news", "redes sociais", "liberdade de expressão"],
            ),
            Proposicao(
                id="sen-3",
                tipo="PEC",
                numero="3",
                ano=2024,
                ementa="Altera o artigo 142 da Constituição Federal para delimitar expressamente as atribuições das Forças Armadas no que se refere à garantia da ordem constitucional.",
                ementa_resumida="Redefinição do papel constitucional das Forças Armadas",
                autor="Rodrigo Pacheco",
                orgao_origem="Senado Federal",
                status="Em análise",
                orgao_atual="CCJ",
                data_apresentacao="2024-01-15",
                data_ultima_movimentacao="2024-11-05",
                tempo_total_dias=295,
                tem_atraso=False,
                tem_previsao_ia=False,
                tags=["constituição", "forças armadas", "democracia"],
            ),
            Proposicao(
                id="sen-4",
                tipo="PL",
                numero="1087",
                ano=2023,
                ementa="Dispõe sobre a proteção de dados pessoais de crianças e adolescentes no ambiente digital, complementando a Lei Geral de Proteção de Dados Pessoais.",
                ementa_resumida="Proteção de dados de crianças no ambiente digital",
                autor="Soraya Thronicke",
                orgao_origem="Senado Federal",
                status="Aprovada",
                orgao_atual="Câmara dos Deputados",
                data_apresentacao="2023-07-12",
                data_ultima_movimentacao="2024-08-20",
                tempo_total_dias=405,
                tem_atraso=False,
                tem_previsao_ia=True,
                previsao_aprovacao_dias=60,
                tags=["LGPD", "crianças", "dados pessoais", "digital"],
            ),
        ]
