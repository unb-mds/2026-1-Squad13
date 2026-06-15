import { FileText, Activity, Clock, TrendingUp, LucideIcon } from "lucide-react";

export interface KPICardMetadata {
  key: string;
  trendKey: string;
  title: string;
  definition: string;
  source: string;
  rule: string;
  fallbackValue: string;
  subtitle: string;
  icon: LucideIcon;
  fallbackTrend: {
    value: string;
    isPositive: boolean;
  };
  isAlarm?: boolean;
}

export const KPI_CARDS_CONFIG: Record<string, KPICardMetadata> = {
  totalProposicoes: {
    key: "totalProposicoes",
    trendKey: "totalProposicoesTrend",
    title: "Total de Proposições",
    definition: "Total de proposições legislativas registradas na base local no recorte selecionado.",
    source: "Banco de Dados do LexTrack",
    rule: "Contagem simples filtrada pelos critérios do usuário.",
    fallbackValue: "2.847",
    subtitle: "Registradas no sistema",
    icon: FileText,
    fallbackTrend: { value: "+12% vs mês anterior", isPositive: true },
  },
  totalEmTramitacao: {
    key: "totalEmTramitacao",
    trendKey: "totalEmTramitacaoTrend",
    title: "Em Tramitação Ativa",
    definition: "Proposições ativas que estão atualmente em alguma fase do rito legislativo.",
    source: "Banco de Dados do LexTrack",
    rule: "Total de proposições cujo status atual não é terminal (exclui arquivadas, rejeitadas, sancionadas ou vetadas).",
    fallbackValue: "1.423",
    subtitle: "Matérias ainda em curso",
    icon: Activity,
    fallbackTrend: { value: "+8% vs mês anterior", isPositive: true },
  },
  proposicoesComAtraso: {
    key: "proposicoesComAtraso",
    trendKey: "proposicoesComAtrasoTrend",
    title: "Atraso Crítico",
    definition: "Proposições em atraso em relação à mediana histórica do rito e tipo.",
    source: "Métrica de Conformidade do LexTrack (IAR)",
    rule: "Contagem de proposições ativas com Índice de Atraso Relativo (IAR) ≥ 1.5.",
    fallbackValue: "234",
    subtitle: "Acima de 1.5x a mediana do grupo",
    icon: Clock,
    fallbackTrend: { value: "-5% vs mês anterior", isPositive: true },
    isAlarm: true,
  },
  tempoMedioTramitacao: {
    key: "tempoMedioTramitacao",
    trendKey: "tempoMedioTramitacaoTrend",
    title: "Tempo Médio Global",
    definition: "Média do tempo total acumulado em dias por todas as proposições registradas.",
    source: "Agregação do Banco de Dados",
    rule: "Média aritmética do tempo decorrido em dias entre a data de apresentação e a data de encerramento (ou data atual, se ativa).",
    fallbackValue: "54 dias",
    subtitle: "Tempo típico de trâmite",
    icon: TrendingUp,
    fallbackTrend: { value: "+3 dias vs trimestre", isPositive: false },
  },
};
