Documento de Requisitos de Software

1. Introdução

Este documento apresenta uma especificação de requisitos de software (SRS) simplificada para um sistema web de Monitoramento de Tempo de Tramitação de Leis. O objetivo principal é fornecer uma visão geral do propósito, escopo, usuários e funcionalidades essenciais do software, servindo como base para as próximas etapas de desenvolvimento no contexto da disciplina de "Métodos de Desenvolvimento de Software".

O sistema visa aumentar a transparência e o acesso da população às informações sobre o processo legislativo, permitindo o acompanhamento da tramitação de projetos de lei e a visualização de dados relevantes de forma clara e acessível.

2. Descrição Geral

O sistema de Monitoramento de Tempo de Tramitação de Leis será uma aplicação web que permitirá aos cidadãos acompanhar o andamento de projetos de lei no Brasil. Ele buscará resolver o problema da dificuldade de acesso e compreensão das informações legislativas, que muitas vezes são complexas e dispersas em diferentes portais governamentais.

Objetivos do Software:

•Transparência: Tornar o processo legislativo mais transparente para a população.

•Acessibilidade: Facilitar o acesso e a compreensão das informações sobre a tramitação de leis.

•Engajamento Cívico: Incentivar o acompanhamento e a participação cidadã no processo legislativo.

•Informação Centralizada: Oferecer um ponto único para consulta de dados sobre projetos de lei.

O sistema se integrará com APIs de órgãos legislativos (como o Senado Federal e a Câmara dos Deputados) para obter dados atualizados sobre a tramitação de projetos de lei, sem a necessidade de entrada manual de dados.

3. Clientes

Os clientes e partes interessadas deste software são primariamente a população em geral que deseja acompanhar o processo legislativo. Isso inclui:

•Cidadãos Engajados: Indivíduos interessados em política e no impacto das leis em suas vidas.

•Estudantes e Pesquisadores: Pessoas que necessitam de dados sobre a tramitação de leis para estudos acadêmicos ou pesquisas.

•Jornalistas e Mídia: Profissionais que buscam informações rápidas e precisas para reportagens e análises.

•Organizações da Sociedade Civil: Grupos que monitoram a atividade legislativa para advocacia e fiscalização.

O foco principal é em usuários que não possuem conhecimento técnico aprofundado sobre o funcionamento do congresso, buscando uma interface intuitiva e de fácil compreensão.

4. Funcionalidades

Esta seção detalha as funcionalidades que o sistema oferecerá, com uma perspectiva focada na experiência do usuário (frontend), sem especificar a tecnologia de implementação.

4.1. Visão Geral do Frontend

A interface do usuário será projetada para ser limpa, intuitiva e responsiva, garantindo uma boa experiência em diferentes dispositivos (desktops, tablets e smartphones). O design priorizará a clareza das informações e a facilidade de navegação.

4.2. Funcionalidades Principais

As funcionalidades essenciais do sistema incluem:

4.2.1. Busca e Filtragem de Leis

•Barra de Busca: Um campo de texto proeminente que permite aos usuários pesquisar projetos de lei por palavras-chave, número do projeto, ou nome do autor.

•Filtros por Data: Opções para filtrar projetos de lei por data de apresentação, data de última atualização ou período de tramitação.

•Filtros por Status: Capacidade de filtrar por status atual da tramitação (ex: "Em Análise", "Aprovado", "Arquivado").

•Filtros por Tipo de Lei: Opções para filtrar por tipo de proposição (ex: "Projeto de Lei", "PEC - Proposta de Emenda à Constituição", "Medida Provisória").

•Filtros por Órgão: Filtragem por órgão legislativo (Senado Federal, Câmara dos Deputados).

4.2.2. Visualização Detalhada de Projetos de Lei

•Lista de Resultados: Uma lista paginada de projetos de lei que correspondem aos critérios de busca e filtragem, exibindo informações resumidas como título, número, autor e status atual.

•Página de Detalhes do Projeto: Ao selecionar um projeto da lista, o usuário será direcionado a uma página dedicada com informações completas, incluindo:

•Título e Ementa: Descrição concisa e completa do projeto.

•Número e Ano: Identificação única do projeto.

•Autor(es): Nome(s) do(s) parlamentar(es) ou órgão(s) responsável(is).

•Histórico de Tramitação: Uma linha do tempo ou lista cronológica dos passos que o projeto já percorreu (ex: "Apresentado", "Enviado à Comissão X", "Aprovado na Câmara", "Enviado ao Senado").

•Status Atual: Indicação clara da fase em que o projeto se encontra.

•Links para Documentos Oficiais: Acesso direto aos textos integrais do projeto e documentos relacionados nos portais do Senado/Câmara.

•Tempo de Tramitação: Exibição do tempo total de tramitação até o momento ou em fases específicas.



4.2.3. Informações Adicionais (Frontend)

•
Painel de Estatísticas (Opcional): Uma seção que pode apresentar gráficos simples ou números sobre o tempo médio de tramitação, número de projetos em andamento, etc.

•
Responsividade: A interface se adaptará a diferentes tamanhos de tela para garantir usabilidade em dispositivos móveis e desktops.

•
Navegação Intuitiva: Menus e elementos de navegação claros para facilitar a exploração do site.

4.3. Integração com APIs

O sistema consumirá dados de APIs públicas fornecidas por órgãos legislativos, como a API de Dados Abertos do Senado Federal e a API de Dados Abertos da Câmara dos Deputados. Essa integração será responsável por manter as informações sobre os projetos de lei atualizadas no sistema. A complexidade da integração e o tratamento dos dados brutos serão abstraídos do usuário final, que verá apenas as informações processadas e organizadas.
