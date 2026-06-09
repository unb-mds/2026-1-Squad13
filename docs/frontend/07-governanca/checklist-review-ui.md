# Governança de UI - Checklist de Revisão de Pull Requests (UI/UX)

Este checklist serve como critério de aceitação técnica e visual para qualquer Pull Request (PR) que adicione, modifique ou remova elementos visuais no frontend do LexTrack.

---

## 1. Coerência com o Design System (Estilos e Tokens)
- [ ] **Aderência aos Tokens:** O código utiliza apenas classes padrão do Tailwind configuradas no design system. Não existem cores arbitrárias em hexadecimal (ex: `#ff0055`) declaradas inline.
- [ ] **Limitação de Largura (Shell):** O container do componente respeita a largura máxima do grid principal (`max-w-[1400px]`) e não quebra o alinhamento da barra lateral ou cabeçalho.
- [ ] **Tipografia Semântica:** Uso das fontes corretas (`Syne` para displays/títulos, `DM Sans` para corpo, `JetBrains Mono` para dados numéricos/código).

---

## 2. Experiência de Carregamento e Robustez (Resiliência)
- [ ] **Carregamento Paralelo:** Múltiplas requisições assíncronas de rede ocorrem em paralelo via `Promise.allSettled`, evitando waterfalls de latência.
- [ ] **Controle de Estado de Carregamento:** O componente implementa Skeletons (estruturas complexas) ou Spinners (ações de botão) durante o fetch de dados.
- [ ] **Tratamento de Estado Vazio (Empty State):** Exibe o componente `<EmptyState />` adequado com mensagem clara ao usuário caso a busca por filtros resulte em 0 itens.
- [ ] **Fallback de Erros:** O componente prevê falhas de rede na API e realiza um fallback suave para dados de contingência (mocks) ou exibe card de erro com botão de recarga.

---

## 3. Acessibilidade e Testabilidade (QA)
- [ ] **Identificadores Únicos (IDs):** Todos os novos elementos interativos (botões, inputs de filtros, abas clicáveis) possuem um atributo `id` único e descritivo para suportar testes de integração automatizados.
- [ ] **HTML5 Semântico:** Uso apropriado de tags semânticas (`<section>`, `<article>`, `<header>`, `<nav>`) ao invés do uso indiscriminado de `<div>`.
- [ ] **Leitores de Tela:** Elementos puramente visuais ou ícones decorativos possuem `aria-hidden="true"`, e spinners de loading têm `role="status"` com `aria-label` descritivo.

---

## 4. Higiene do Repositório (Higiene de Código)
- [ ] **Sem Código Morto:** Arquivos de componentes obsoletos, protótipos ou páginas sob redirecionamento desabilitado foram fisicamente deletados da branch.
- [ ] **Imports Limpos:** Imports relativos ou paths com alias (`@/shared/...`) estão ordenados e limpos de referências circulares.
- [ ] **Build e Lint Verdes:** O comando `npm run build` e `npm run lint` na pasta `frontend/` executam com 100% de sucesso localmente antes de enviar para o repositório remoto.
