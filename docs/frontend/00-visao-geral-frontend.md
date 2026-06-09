# 00 - Visão Geral do Frontend

Este documento apresenta uma visão conceitual e estrutural do frontend do **LexTrack**, fornecendo o ponto de partida técnico para engenheiros de software, designers e revisores.

## Tecnologias e Stack
O frontend do LexTrack foi projetado para ser responsivo, performático e semanticamente acoplado ao domínio legislativo, utilizando as seguintes tecnologias centrais:

1. **React 18**: Framework de componentização declarativa da interface de usuário.
2. **Vite**: Ferramenta de build ultra-rápida baseada em ES Modules nativos para o ambiente de desenvolvimento local.
3. **TypeScript**: Tipagem estática estrita para mapear dados e contratos da API com segurança em tempo de desenvolvimento.
4. **Tailwind CSS 3**: Utilitários utilitários de estilização em Vanilla CSS para máxima flexibilidade e ausência de folhas de estilo monolíticas.
5. **Recharts**: Biblioteca de visualização de dados otimizada para React, utilizada nos gráficos de linha, barras e pizza do dashboard.
6. **Lucide React**: Biblioteca de ícones vetoriais padronizados.

---

## Estrutura de Diretórios
O frontend segue uma estrutura de **Arquitetura Baseada em Features** (Feature-Based Architecture) sob a pasta `src/`:

```txt
frontend/src/
├── app/                  # Orquestração global do app
│   ├── layouts/          # Layouts de página (ex: AppLayout.tsx)
│   ├── providers/        # Contextos compartilhados (ex: AuthProvider)
│   └── router/           # Configurações de rotas (AppRouter em index.tsx)
├── features/             # Componentes acoplados à lógica de negócio
│   ├── dashboard/        # Gráficos e painéis do dashboard analítico
│   ├── filtros/          # Painel de filtros avançados e chips
│   ├── proposicoes/      # Tabelas, timelines e detalhes de proposições
│   ├── relatorios/       # Métricas de gargalos e rankings operacionais
│   └── tramitacoes/      # Timelines e previsões preditivas de IA
├── pages/                # Componentes de página inteira que montam as views
│   ├── consulta-proposicoes-page.tsx
│   ├── dashboard-page.tsx
│   ├── detalhe-proposicao-page.tsx
│   └── relatorios-page.tsx
├── shared/               # Recursos compartilhados e agnósticos a domínio
│   ├── components/       # Componentes reusáveis estruturais (KPICard, MetricCard)
│   ├── constants/        # Constantes e enums globais
│   ├── lib/              # Funções utilitárias, hooks e conexões de API
│   ├── types/            # Definições globais de tipos TypeScript
│   └── ui/               # Componentes visuais atômicos sem estado (index.tsx)
├── main.tsx              # Ponto de entrada da aplicação
└── index.css             # Estilos globais e injeção do Tailwind CSS
```

---

## Guia de Execução Local

### Pré-requisitos
* Node.js v18 ou superior instalado.
* Gerenciador de pacotes `npm` ou `yarn`.

### Instalação e Inicialização
1. Navegue para a pasta de frontend:
   ```bash
   cd frontend
   ```
2. Instale as dependências declaradas no `package.json`:
   ```bash
   npm install
   ```
3. Inicialize o servidor de desenvolvimento Vite localmente:
   ```bash
   npm run dev
   ```
   * O aplicativo estará disponível por padrão em `http://localhost:5173` ou conforme especificado na variável de ambiente `VITE_API_URL`.

### Testes e Validação
* Para rodar a suite de testes unitários baseada no **Vitest**:
  ```bash
  npm run test -- --run
  ```
* Para rodar a verificação de linter e formatação com o **ESLint**:
  ```bash
  npm run lint
  ```
* Para construir o pacote de produção compilado e otimizado:
  ```bash
  npm run build
  ```

---

## Próximos Passos recomendados para Leitura
* Para entender o fluxo de rotas e layouts de tela, consulte a [Arquitetura de Telas](./01-arquitetura-de-telas.md).
* Para compreender as bases estéticas do produto, leia os [Princípios de Design](./02-design-principles.md) e [Design Tokens](./03-design-tokens.md).
