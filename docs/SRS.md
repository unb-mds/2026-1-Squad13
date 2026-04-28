# Especificação de Requisitos de Software (SRS)

## 1. Introdução

Este documento apresenta a Especificação de Requisitos de Software (SRS) do sistema web de Monitoramento de Tempo de Tramitação de Leis. Seu objetivo é registrar, de forma clara e enxuta, o escopo inicial do produto, os principais requisitos funcionais e não funcionais, as dependências externas e os critérios de aceitação que orientam o desenvolvimento no contexto acadêmico.

O sistema busca ampliar a transparência e facilitar o acesso às informações sobre o processo legislativo brasileiro, permitindo consulta, acompanhamento e análise de proposições em uma interface centralizada.

## 2. Visão Geral do Sistema

O sistema será uma aplicação web voltada ao monitoramento da tramitação de proposições legislativas, com foco em análise temporal, visualização de métricas e identificação de padrões de atraso.

Os principais usuários esperados são cidadãos interessados em acompanhar o processo legislativo, estudantes e pesquisadores, jornalistas e organizações da sociedade civil.

O sistema utilizará dados públicos obtidos por meio de APIs de órgãos legislativos, especialmente Câmara dos Deputados e Senado Federal.

## 3. Escopo Validado

O escopo inicial do sistema considera proposições legislativas dos tipos **PL** e **PEC**, por serem categorias relevantes para análise de tramitação, comparação de tempos e identificação de gargalos institucionais. Esse recorte poderá ser revisto posteriormente conforme validação do grupo e viabilidade técnica observada ao longo do desenvolvimento.

Neste estágio inicial, o produto terá como foco:

- consulta e filtragem de proposições;
- visualização de tramitação e tempo decorrido;
- apresentação de métricas analíticas;
- exploração inicial de funcionalidades baseadas em IA.

## 4. Requisitos Funcionais

| Requisito                | Descrição                                                                                                                                                     | Prioridade | Critérios de Aceitação                                                                                                                       |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Busca de proposições     | O sistema permite buscar proposições por palavra-chave, número, ano ou autor.                                                                                 | Alta       | A busca retorna resultados compatíveis com o termo informado; o usuário consegue pesquisar por pelo menos um dos campos definidos.           |
| Filtragem de proposições | O sistema permite filtrar proposições por tipo, órgão legislativo, período, status de tramitação e outros filtros relevantes disponíveis nas fontes de dados. | Alta       | Os filtros alteram os resultados exibidos; o usuário consegue aplicar e remover filtros; a interface deixa claro quais filtros estão ativos. |
| Combinação de filtros    | O sistema permite combinar múltiplos filtros na mesma consulta.                                                                                               | Média      | O sistema aplica simultaneamente os filtros selecionados; os resultados respeitam a interseção dos critérios escolhidos.                     |
| Visualização de lista    | O sistema exibe uma lista de proposições com base nos critérios de busca e filtragem.                                                                         | Alta       | A lista apresenta resultados coerentes com a consulta; cada item contém informações resumidas suficientes para identificação inicial.        |
| Visualização detalhada   | O sistema permite visualizar os detalhes de uma proposição específica.                                                                                        | Alta       | A tela de detalhes apresenta título, ementa, número, ano, autor, status atual e links oficiais quando disponíveis.                           |
| Histórico de tramitação  | O sistema apresenta o histórico de tramitação da proposição.                                                                                                  | Alta       | O usuário consegue visualizar as etapas registradas da tramitação em ordem compreensível.                                                    |
| Tempo de tramitação      | O sistema apresenta o tempo total de tramitação e, quando possível, o tempo por fase.                                                                         | Alta       | O tempo total aparece para a proposição consultada; quando existirem dados suficientes, o sistema mostra recortes por etapa.                 |
| Métricas analíticas      | O sistema calcula e exibe métricas como tempo médio por tipo de proposição, por comissão e fases mais longas.                                                 | Alta       | O dashboard apresenta ao menos as métricas definidas no escopo; os valores mudam de acordo com os filtros aplicados.                         |
| Gargalos institucionais  | O sistema destaca possíveis gargalos institucionais com base na tramitação observada.                                                                         | Média      | O usuário consegue identificar etapas, órgãos ou recortes com maior demora relativa.                                                         |
| Previsão com IA          | O sistema oferece uma estimativa de tempo de aprovação com base em dados históricos.                                                                          | Média      | O sistema gera uma previsão para proposições com dados suficientes; a funcionalidade deixa claro que se trata de estimativa.                 |
| Padrões de atraso        | O sistema identifica padrões de atraso e diferenças entre temas ou tipos de proposição.                                                                       | Média      | O sistema apresenta indicadores ou visualizações que permitam comparar proposições e perceber padrões de lentidão.                           |

## 5. Requisitos Não Funcionais

| Requisito                       | Descrição                                                                                                    | Prioridade | Critérios de Aceitação                                                                                     |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------ | ---------- | ---------------------------------------------------------------------------------------------------------- |
| Responsividade                  | O sistema deve funcionar adequadamente em desktop e dispositivos móveis.                                     | Alta       | As principais telas permanecem utilizáveis em diferentes tamanhos de tela, sem perda crítica de navegação. |
| Clareza da interface            | O sistema deve apresentar navegação clara e interface compreensível para usuários não especializados.        | Alta       | Um usuário consegue localizar busca, filtros, lista e detalhes sem instrução prévia extensa.               |
| Atualização por fontes oficiais | O sistema deve utilizar dados públicos provenientes de fontes oficiais.                                      | Alta       | Os dados exibidos são obtidos de APIs legislativas oficiais definidas pelo projeto.                        |
| Flexibilidade de evolução       | O sistema deve ser estruturado para permitir expansão futura para novos tipos de proposição e novos filtros. | Média      | A documentação e a organização funcional não impedem inclusão posterior de novos tipos e filtros.          |
| Rastreabilidade                 | A evolução do projeto deve ser registrada por meio do repositório GitHub e do histórico de commits.          | Alta       | Alterações de documentação e implementação ficam registradas em commits e pull requests revisáveis.        |

## 6. Integrações e Dependências

O sistema dependerá de APIs públicas fornecidas por órgãos legislativos, especialmente Câmara dos Deputados e Senado Federal, para obtenção e atualização dos dados de proposições.

A disponibilidade, completude e consistência das informações exibidas dependerão da qualidade dos dados retornados por essas fontes externas.

## 7. Observações Finais

Este documento representa uma versão inicial e leve da especificação de requisitos do sistema. Ele poderá ser revisado ao longo do desenvolvimento, conforme evolução do entendimento do domínio, validação do grupo e refinamento do escopo do produto.
