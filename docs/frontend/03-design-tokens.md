# 03 - Design Tokens

Este documento registra as variáveis estéticas (Design Tokens) que compõem o sistema visual do LexTrack, extraídas diretamente de [tailwind.config.js](../../frontend/tailwind.config.js) e [index.css](../../frontend/src/index.css).

## 1. Tipografia e Fontes
O sistema utiliza três famílias tipográficas específicas carregadas no cabeçalho do documento HTML:

| Token Semântico | Fonte Real | Utilização |
| :--- | :--- | :--- |
| `font-sans` | `'DM Sans', sans-serif` | Corpo de texto, tabelas, ementas e legendas de dados. |
| `font-display` | `'Syne', sans-serif` | Cabeçalhos de tela (`h1`), títulos de widgets e números grandes de KPIs. |
| `font-mono` | `'JetBrains Mono', monospace` | Códigos de proposições (números/anos), IDs e dados numéricos tabulares. |

---

## 2. Paletas de Cores (Tailwind Config)
O tema estende as cores do Tailwind CSS com duas paletas de base e cores semânticas para estados:

### A. Paleta Neutra Escura (`ink`)
Utilizada para fundos de containers, bordas e divisores do modo de layout escuro (Original):
* `ink-50`: `#f0f0f5`
* `ink-100`: `#d9d9e8`
* `ink-200`: `#b3b3d1`
* `ink-300`: `#8080b0` (Cor padrão de rótulos secundários / muted text)
* `ink-400`: `#5a5a91`
* `ink-500`: `#3d3d6b` (Bordas de tabelas e divisores)
* `ink-600`: `#2e2e52` (Linhas de grade de gráficos e scrollbars)
* `ink-700`: `#1e1e38` (Fundo de inputs e tooltips do Recharts)
* `ink-800`: `#12121f` (Fundo de cards e containers secundários)
* `ink-900`: `#080810` (Fundo geral da viewport / track de scrollbars)

### B. Paleta de Destaque (`volt`)
Tons verde-limão de alto contraste utilizados para botões principais, loaders e linhas ativas:
* `volt-50`: `#f5ffe0`
* `volt-100`: `#e8ffa8`
* `volt-200`: `#d4ff6e`
* `volt-300`: `#c2ff3d` (Hover e destaques ativos)
* `volt-400`: `#b2ff00` (Foco padrão e background ativo do botão primário)
* `volt-500`: `#9de800`
* `volt-600`: `#7abd00`
* `volt-700`: `#5a8f00`
* `volt-800`: `#3d6200`
* `volt-900`: `#1e3100`

### C. Cores Semânticas de Estado
* **Alerta / Atraso Crítico (`rose`):**
  * `rose-400`: `#fb7185` (Métricas críticas de tempo e atraso acima de 15 dias)
  * `rose-500`: `#f43f5e` (Borda de botões/cards em estado alarmante)
* **Atenção / Atraso Médio (`amber`):**
  * `amber-400`: `#fbbf24` (Atrasos médios até 15 dias)
  * `amber-500`: `#f59e0b` (Exibição de alertas e fallbacks de dados)

---

## 3. Mapeamento de Variáveis Semânticas CSS
A aplicação implementa mapeamento de variáveis CSS para suporte a temas claros e escuros em `index.css`:

* **Light Mode (Modo Padrão `:root`):**
  * `--background`: `#fafbfc` (Cinza claro limpo)
  * `--foreground`: `#1a2332` (Slate blue escuro)
  * `--card`: `#ffffff` (Card branco clássico)
  * `--border`: `#d4dce4` (Divisor sutil)
  * `--primary`: `#115e67` (Verde-azulado profundo institucional)
  * `--secondary`: `#f4f6f8` (Fundo de cabeçalhos de tabelas e loaders)
* **Dark Mode (Modo `.dark`):**
  * `--background`: `oklch(0.145 0 0)`
  * `--card`: `oklch(0.145 0 0)`
  * `--foreground`: `oklch(0.985 0 0)`
  * `--border`: `oklch(0.269 0 0)`

---

## 4. Keyframes e Animações
* **`animate-fade-in` (`0.4s ease-out`):** Suaviza o aparecimento de páginas e componentes montados.
* **`animate-slide-up` (`0.4s ease-out`):** Utilizado na abertura do painel de filtros e drawers para efeito de deslizar verticalmente de baixo para cima.
* **`animate-slide-in` (`0.3s ease-out`):** Efeito de deslizar da esquerda para a direita.
* **`animate-pulse` (`2s infinite`):** Utilizado para skeletons de carregamento de dados.

---

## Próximos Passos recomendados para Leitura
* Para conferir como os tokens de cores são aplicados no layout, veja a [Arquitetura de Telas](./01-arquitetura-de-telas.md) e [Layout Shell](./01b-layout-shell.md).
* Para conferir os componentes que utilizam os botões da paleta `volt`, leia o catálogo de [Componentes de Formulário](./04-componentes/forms-and-inputs.md).
