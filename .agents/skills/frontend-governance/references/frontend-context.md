# Baseline do Frontend - LexTrack

Este documento define a fonte de verdade operacional para o desenvolvimento do frontend.

## 1. Fonte de Verdade
- **Primária:** Código-fonte em `/frontend` e documentação técnica em `docs/frontend/`.
- **Secundária:** ADRs (Architectural Decision Records) em `docs/adr/`.
- **Referência Visual:** Figma (quando disponível), mas deve ser validado contra os Design Tokens implementados.

## 2. Princípios de Design
- **Foco Analítico:** A interface deve priorizar a clareza dos dados legislativos.
- **Simplicidade:** Evitar decorações desnecessárias; preferir Vanilla CSS e Tailwind.
- **Responsividade:** O Dashboard deve ser funcional em resoluções desktop e tablet.

## 3. Arquitetura
- **Feature-Based:** Componentes e lógicas organizados por domínios de negócio (ex: `features/proposicoes`, `features/dashboard`).
- **Layers:** Separação clara entre componentes de apresentação e hooks de lógica/dados.

## 4. Design Tokens
- Localizados em `frontend/tailwind.config.js`.
- Cores semânticas: `ink` (neutros), `volt` (destaque), `rose` (alerta), `amber` (atenção).
