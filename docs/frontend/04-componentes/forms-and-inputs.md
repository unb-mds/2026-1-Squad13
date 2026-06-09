# Catálogo de Componentes - Forms and Inputs (Atomic UI)

Este documento mapeia os componentes de formulários e elementos atômicos de interface localizados na biblioteca de UI básica do LexTrack.

---

## 1. Visão Geral e Objetivo
Os componentes atômicos servem como a fundação de interface para garantir consistência visual no preenchimento de filtros, submissão de ações e sinalização visual através de pequenos elementos (como Badges e Spinners). Todos esses componentes estão centralizados no mesmo arquivo físico para otimizar imports e facilitar manutenção.

* **Local de Implementação:** [index.tsx](../../../frontend/src/shared/ui/index.tsx)

---

## 2. Componentes Catalogados

### A. Button (`Button`)
Componente de botão interativo com suporte a estados de carregamento (Spinner interno) e variações semânticas.

#### Interface TypeScript (Props)
```typescript
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  loading?: boolean;
  leftIcon?: React.ReactNode;
}
```

#### Estilos e Variações
* **Primary (Destaque):** Fundo `bg-volt-400`, texto escuro `text-ink-900` e hover `hover:bg-volt-300`.
* **Secondary (Neutro/Ação Secundária):** Fundo `bg-ink-700`, borda `border-ink-600` e hover `hover:bg-ink-600`.
* **Ghost (Sem fundo):** Sem borda, texto `text-ink-300` com hover `hover:bg-ink-700/60` e texto branco.
* **Danger (Ação Destrutiva/Alerta):** Fundo translúcido `bg-rose-500/15`, texto `text-rose-400` e hover `hover:bg-rose-500/25` com borda sutil.

---

### B. Input (`Input`)
Componente de campo de texto com suporte a rótulos (labels), ícones à esquerda (Left Icon) e mensagem de erro em vermelho.

#### Interface TypeScript (Props)
```typescript
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  leftIcon?: React.ReactNode;
}
```

#### Comportamento Visual
* **Foco:** Borda e anel na cor Volt (`focus:ring-volt-400/50 focus:border-volt-400/50`).
* **Estado de Erro:** Exibe borda vermelha (`border-rose-500/50`) e um parágrafo inferior com a mensagem do erro (`text-rose-400`).
* **Ícone:** Se `leftIcon` for fornecido, adiciona padding esquerdo de `pl-9` para evitar sobreposição entre texto e ícone.

---

### C. Select (`Select`)
Menu suspenso estilizado para seleção de opções simples, utilizado principalmente nos filtros de busca da proposição.

#### Interface TypeScript (Props)
```typescript
interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
}
```

#### Estilos
* Fundo `bg-ink-700/50`, borda `border-ink-600/50`, texto branco e foco com brilho Volt. Desativa a seta nativa do navegador (`appearance-none`) para controle do visual em navegadores baseados em Chromium/Webkit.

---

### D. Badge (`Badge`)
Indicador visual compacto de status ou categoria.

#### Interface TypeScript (Props)
```typescript
interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' | 'volt';
  className?: string;
}
```

#### Mapeamento de Cores
* **default:** Cinza escuro com texto cinza claro (`bg-ink-600/50 text-ink-300`).
* **success:** Verde translúcido com texto verde (`bg-emerald-500/15 text-emerald-400`).
* **warning:** Amarelo/âmbar translúcido com texto âmbar (`bg-amber-500/15 text-amber-400`).
* **danger:** Vermelho translúcido com texto vermelho (`bg-rose-500/15 text-rose-400`).
* **info:** Azul translúcido com texto azul (`bg-blue-500/15 text-blue-400`).
* **volt:** Verde Volt translúcido com texto Volt (`bg-volt-400/15 text-volt-300`).

---

### E. Spinner (`Spinner`)
Componente animado de progresso utilizado para loadings menores ou no corpo dos botões.

* **Implementação:** Usa o ícone `Loader2` do `lucide-react` com a classe de animação nativa do Tailwind (`animate-spin`) e cor padrão Volt (`text-volt-400`).
* **Acessibilidade:** Possui a propriedade `role="status"` e `aria-label="Carregando"` para leitores de tela.

---

## 3. Problemas e Limitações
1. **Controle Estilizado do Select:** O componente `Select` não possui um ícone de seta customizado embutido em CSS, o que pode dar aparência plana dependendo do navegador, já que `appearance-none` foi aplicado mas nenhum chevron foi adicionado de volta à direita.
2. **Duplicação de Cards:** A biblioteca de UI atômica contém `Card`, `CardHeader` e `CardBody` com estilos específicos escuros (ex: `bg-ink-800`), enquanto o componente `KPICard` em `shared/components/` usa classes neutras (`bg-card border-border`) que dependem do sistema de temas.

---

## 4. Oportunidades de Melhoria
* **Padronizar Elementos de Card:** Unificar as bordas e fundos dos cards atômicos de `shared/ui` com os de `shared/components/` usando as variáveis globais (`bg-card`, `border-border`) ao invés de fixar em classes do Tailwind (`bg-ink-800`).
* **Melhorar Acessibilidade do Select:** Adicionar ícones de chevron funcionais dentro do `Select` de forma flexível utilizando wrappers posicionados de forma absoluta.
