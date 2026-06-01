# Especificações Técnicas - Frontend (Protótipo)

## 1. Visão Geral
O sistema é um dashboard analítico para monitoramento de proposições legislativas federais (PL, PEC, PLP), com foco em identificar gargalos, atrasos e qualidade de dados.

## 2. Stack Tecnológica
- **Framework**: React 18
- **Build Tool**: Vite
- **Linguagem**: TypeScript
- **Estilização**: Tailwind CSS 3 + shadcn/ui
- **Ícones**: Lucide React
- **Gráficos**: Recharts
- **Gestão de Estado**: Local (useState) no protótipo

## 3. Arquitetura de Componentes

### 3.1. Páginas Principais
- `App.tsx`: Dashboard principal com visão macro do sistema.
- `PropositionDetail.tsx`: Visão detalhada de uma proposição específica.

### 3.2. Componentes de Negócio (`src/app/components/`)
- `KPICard.tsx`: Exibe métricas chave (Total, Ativas, Atraso, Tempo Mediano) com tendências.
- `PipelineStage.tsx`: Representação visual das 8 fases canônicas da tramitação.
- `PropositionsTable.tsx`: Listagem com filtros e indicadores de status/confiabilidade.
- `BottleneckAnalytics.tsx`: Listas rankeadas de gargalos por órgão, fase e tema.
- `HouseTransitions.tsx`: Fluxo de proposições entre Câmara e Senado.
- `PhaseTimeline.tsx`: Linha do tempo de fases processuais percorridas.
- `EventTimeline.tsx`: Log detalhado de eventos legislativos (despachos, pareceres, etc.).
- `HouseTransitDiagram.tsx`: Visualização do trânsito entre as casas legislativas.
- `DataReliability.tsx`: Indicadores de completude e fontes de dados.

### 3.3. Componentes UI (Baseados em shadcn/ui)
- Cards, Buttons, Inputs, Tooltips, Badges, Tables, etc.

## 4. Funcionalidades Detalhadas

### 4.1. Dashboard (Macro)
- **KPIs**: 
  - Total de Proposições (Últimos 12 meses).
  - Em Tramitação Ativa (Câmara e Senado).
  - Com Atraso Crítico (>15 dias acima da mediana).
  - Tempo Mediano Global.
- **Pipeline Legislativo**: Visualização horizontal das 8 fases:
  1. Recebimento e Despacho
  2. Comissão Temática - Análise
  3. Comissão de Constituição e Justiça (CCJ)
  4. Plenário - Discussão e Votação
  5. Revisão na Casa Revisora
  6. Revisão - Comissões
  7. Revisão - Redação Final
  8. Sanção e Publicação
- **Gráficos**:
  - Evolução Temporal (Entradas vs Saídas mensais).
  - Cobertura de Dados (Eventos, Metadados, Histórico, Documentos).
- **Análise de Gargalos**: Rankings de órgãos e temas mais lentos.

### 4.2. Detalhe da Proposição (Micro)
- **Cabeçalho**: Tipo, número, tema, autoria e ementa completa.
- **Métricas Específicas**:
  - Dias totais acumulados.
  - Dias na etapa atual (com destaque visual para atraso).
  - Fases percorridas (progresso visual).
  - Eventos relevantes documentados.
  - Recorrências de fase (retornos detectados).
  - Transições entre casas (Câmara ↔ Senado).
- **Timeline de Fases**: Histórico cronológico de cada comissão/fase por onde a PL passou.
- **Timeline de Eventos**: Log de cada ação (despacho, parecer, emenda) com filtros por fase.
- **Confiabilidade**: Detalhamento das fontes e limitações da análise.

## 5. Modelo de Dados (Interfaces TypeScript)

### 5.1. Proposição
```typescript
interface Proposition {
  id: string;
  numero: string;
  tipo: string;
  ementa: string;
  casaAtual: string;
  faseAtual: string;
  diasNaEtapa: number;
  ultimoEventoRelevante: string;
  dataUltimoEvento: string;
  autor: string;
  atraso: number;
  coberturaDados: number;
  confiabilidade: 'alta' | 'media' | 'baixa';
  statusTramitacao: 'em-tramitacao' | 'em-atraso' | 'aguardando' | 'aprovada';
  transitouEntreCasas: boolean;
}
```

### 5.2. Evento de Timeline
```typescript
interface TimelineEvent {
  id: string;
  data: string;
  hora: string;
  orgao: string;
  tipoEvento: 'despacho' | 'parecer' | 'deliberacao' | 'emenda' | 'outro';
  titulo: string;
  descricao: string;
  isRelevante: boolean;
  flags?: {
    mudancaFase?: boolean;
    atraso?: boolean;
  };
}
```

## 6. Lógica de Negócio e Visualização
- **Indicadores de Atraso**:
  - Verde: No prazo / dentro da mediana.
  - Amarelo: Atraso leve (1-15 dias acima da mediana).
  - Vermelho: Atraso crítico (>15 dias acima da mediana).
- **Cobertura de Dados**:
  - >90%: Verde (Alta).
  - 70-90%: Amarelo (Média).
  - <70%: Vermelho (Baixa).
- **Recorrência**: Detectada quando o campo `ocorrencia` na `PhaseEntry` é > 1.

## 8. Design System e Identidade Visual

### 8.1. Cores Principais (Tokens CSS)
- **Primary**: `#115e67` (Verde Petróleo - Cor principal da marca)
- **Secondary**: `#f4f6f8` (Cinza muito claro para fundos e botões secundários)
- **Background**: `#fafbfc` (Quase branco)
- **Foreground**: `#1a2332` (Azul escuro quase preto para textos)
- **Muted**: `#e8ecef` / **Muted Foreground**: `#5a6c7d`
- **Border**: `#d4dce4`

### 8.2. Cores de Status
- **Em Curso/Tramitação**: `#2563eb` (Blue-600)
- **Em Atraso**: `#dc2626` (Red-600)
- **Concluída/Aprovada**: `#059669` (Emerald-600)
- **Aguardando**: `#f59e0b` (Amber-500)

### 8.3. Tipografia e Raio
- **Fonte Base**: 16px
- **Border Radius**: `0.5rem` (8px)
- **Pesos**: Normal (400) e Medium (500)

## 9. Notas Metodológicas
- A análise utiliza uma "Narrativa Temporal Unificada".
- Fases canônicas agregam períodos de tramitação para simplificar a visão do usuário.
- O cálculo de atraso é baseado na comparação com a mediana histórica de cada etapa.
