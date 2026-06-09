# 01b - Layout Shell e Comportamento Responsivo

Este documento detalha o esqueleto estrutural (Shell) do frontend do LexTrack, descrevendo como os componentes são organizados no espaço e como a interface reage a diferentes resoluções de tela.

## O Shell Global (`AppLayout`)
A moldura de tela da aplicação é governada pelo [AppLayout.tsx](../../frontend/src/app/layouts/AppLayout.tsx):

```typescript
export function AppLayout() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <Outlet />
    </div>
  )
}
```

* **`min-h-screen`**: Garante que o fundo da aplicação ocupe sempre pelo menos 100% da altura da viewport, evitando quebras visuais em telas de alta resolução com poucos dados.
* **`bg-background text-foreground`**: Aplica as variáveis CSS dinâmicas para a cor de fundo e do texto (sincronizadas com Light/Dark Mode no nível raiz).

---

## Grades e Containers de Conteúdo
O alinhamento horizontal das páginas (Dashboard e Detalhes) utiliza uma largura máxima fixa centralizada:

* **Container Principal:**
  `max-w-[1400px] mx-auto px-4 md:px-6`
  * Garante que em monitores ultra-wide (resoluções acima de 1080p), o dashboard não fique excessivamente esticado horizontalmente, preservando a facilidade de leitura dos gráficos e tabelas.
  * Define um espaçamento lateral de `1rem` (px-4) em mobile e `1.5rem` (px-6) em telas desktop.

---

## Comportamento Responsivo e Stacking (Empilhamento)

O LexTrack foi construído sob uma abordagem **responsive-first**, adaptando grades complexas de forma fluida:

### 1. Visualização Desktop (Monitores >= 1024px)
* **Grades:** Os KPIs principais são organizados em uma linha de 4 colunas (`grid-cols-4`). Gráficos de evolução temporal e a cobertura de dados dividem a tela em um esquema de 2/3 e 1/3 colunas (`lg:grid-cols-3` com `lg:col-span-2` para a linha temporal).
* **Navegação:** Exibição lado a lado de diagramas de trânsito de casas legislativas e dados de confiabilidade.
* **Tabelas:** Linhas horizontais estendidas contendo todas as colunas de dados de triagem.

### 2. Visualização Tablet (Telas entre 768px e 1023px)
* **Grades:** KPIs principais são empilhados em 2 colunas (`md:grid-cols-2`). Os gráficos de evolução e cobertura empilham verticalmente.
* **Tabelas:** Redução de espaçamentos horizontais.

### 3. Visualização Mobile (Telas < 768px)
* **Empilhamento Vertical:** Todos os componentes do grid (KPIs, gráficos e seções de drill-down) são forçados a colunas únicas (`grid-cols-1`).
* **Menu de Filtros:** O painel de Filtros Avançados converte-se em um formulário empilhado de fácil rolagem.
* **Contingência de Tabelas:** O componente de tabela de proposições adiciona uma barra de rolagem horizontal nativa (`overflow-x-auto`) para evitar quebras de texto nas ementas e nomes de autores.
* **Ocultação de Ações:** Botões secundários e microcopies extensos de botões (ex: "Exportar Análise") são ocultados ou simplificados para ícones autodescritivos usando classes como `hidden sm:inline`.

---

## Próximos Passos recomendados para Leitura
* Para entender o design semântico e princípios visuais, veja os [Princípios de Design](./02-design-principles.md).
* Para consultar as cores e fontes que compõem o layout shell, acesse o [Design Tokens](./03-design-tokens.md).
