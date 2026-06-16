# AGENTS.md - Diretrizes do Frontend

Este guia orienta agentes de IA atuando na pasta `frontend/` do LexTrack.

## 1. Organização Feature-Based
O frontend é componentizado por features e layout de telas:
* **Features:** A lógica de negócio visual e os componentes locais devem residir em [frontend/src/features/](file:///home/caio/2026-1-Squad13/frontend/src/features/).
* **Pages:** O roteamento de telas e layouts globais residem em [frontend/src/pages/](file:///home/caio/2026-1-Squad13/frontend/src/pages/).
* **Sem Lógica no Core:** Não colocar regras de negócio complexas ou chamadas diretas de infraestrutura em componentes comuns de apresentação.

## 2. Comandos e Scripts de Teste/Lint
Evite rodar comandos avulsos. Utilize a suíte de scripts da raiz:
* **Validação Completa (CI Local):** Rodar `./scripts/ci/frontend.sh` a partir da raiz do repositório.
  * *O que faz:* Instala dependências (via `npm ci` ou `npm install`), roda `tsc --noEmit`, `npm run lint`, `npm run test` e `npm run build`.
* **Executar no diretório `frontend/`:**
  * Servidor de desenvolvimento: `npm run dev`
  * Executar testes em modo watch: `npm run test`
  * Testes com cobertura: `npm run test:coverage`
  * Executar linting: `npm run lint`

## 3. Definition of Done (DoD Local)
1. Executar `./scripts/ci/frontend.sh` e obter sucesso (zero erros).
2. Prover tratamento de erros visual, telas de carregamento (`loading`) e estados vazios (`empty states`) com atributos ARIA.
3. Garantir responsividade e respeito aos design tokens do Tailwind CSS.
