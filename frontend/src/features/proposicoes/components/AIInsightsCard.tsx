import { useState } from "react";
import {
  Sparkles,
  RotateCcw,
  Building2,
  Tag,
} from "lucide-react";

interface AIInsightsCardProps {
  proposition: {
    numero: string;
    tipo: string;
    diasTotais: number;
    diasNaEtapa: number;
    faseAtual: string;
    casaAtual: string;
    atraso: number;
    eventosRelevantes: number;
    recorrenciasFase: number;
    medianaFase: number;
    fasesPercorridas: number;
  };
  phasesHistory?: Array<{
    fase: string;
    duracaoDias: number;
    atrasoDias: number;
    isCurrent: boolean;
  }>;
}

interface SimilarProposition {
  numero: string;
  tipo: string;
  fase: string;
  diasPipeline: number;
  atraso: number;
}

const mockSimilarPropositions: SimilarProposition[] = [
  { numero: "3421/2024", tipo: "PLP", fase: "Comissão Temática", diasPipeline: 234, atraso: 5 },
  { numero: "1823/2024", tipo: "PL", fase: "Plenário", diasPipeline: 456, atraso: 38 },
  { numero: "4156/2025", tipo: "PL", fase: "Análise Técnica", diasPipeline: 89, atraso: 0 },
  { numero: "2198/2024", tipo: "PL", fase: "Revisão", diasPipeline: 312, atraso: 18 },
];

export function AIInsightsCard({ proposition, phasesHistory = [] }: AIInsightsCardProps) {
  const [activeTab, setActiveTab] = useState<"resumo" | "atraso" | "similares">("resumo");

  const getDelayStatus = () => {
    if (proposition.atraso <= 0) return { label: "No prazo", color: "bg-muted text-muted-foreground" };
    if (proposition.atraso <= 15) return { label: "Atraso leve", color: "bg-amber-100 text-amber-700 border-amber-200" };
    return { label: "Atraso crítico", color: "bg-red-100 text-red-700 border-red-200" };
  };

  const delayStatus = getDelayStatus();

  // Mock phases history if not provided
  const phases = phasesHistory.length > 0 ? phasesHistory : [
    { fase: "Recebimento", duracaoDias: 6, atrasoDias: 0, isCurrent: false },
    { fase: "Comissão Temática", duracaoDias: 58, atrasoDias: 13, isCurrent: false },
    { fase: "Plenário", duracaoDias: 85, atrasoDias: 31, isCurrent: false },
    { fase: "CCJ", duracaoDias: 45, atrasoDias: 12, isCurrent: true },
  ];

  const maxDuration = Math.max(...phases.map(p => p.duracaoDias), 1);

  // Generate associated factors
  const factors = [];
  if (proposition.recorrenciasFase > 0) {
    factors.push({
      icon: RotateCcw,
      text: `${proposition.recorrenciasFase} retornos de fase detectados — indicativo de complexidade técnica ou incompatibilidade entre emendas`,
    });
  }
  factors.push({
    icon: Building2,
    text: `Comissão de Constituição e Justiça figura entre os órgãos com maior permanência mediana no sistema (87 dias)`,
  });
  factors.push({
    icon: Tag,
    text: `Direitos Digitais é um dos temas com maior tempo mediano — 73 dias por proposição similar`,
  });

  return (
    <div className="bg-[#f7f9fa] border border-border rounded-lg overflow-hidden border-l-2 border-l-primary">
      {/* Header */}
      <div className="px-6 py-4 border-b border-border bg-gradient-to-r from-primary/5 to-transparent">
        <div className="flex items-center gap-2 mb-3">
          <Sparkles className="w-4 h-4 text-primary" />
          <h3 className="font-semibold text-foreground">Análise Assistida</h3>
        </div>

        {/* Tabs */}
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab("resumo")}
            className={`px-3 py-1.5 text-[13px] font-medium rounded-lg transition-colors ${
              activeTab === "resumo"
                ? "bg-primary text-primary-foreground"
                : "bg-card text-foreground hover:bg-secondary"
            }`}
          >
            Resumo
          </button>
          {proposition.atraso > 0 && (
            <button
              onClick={() => setActiveTab("atraso")}
              className={`px-3 py-1.5 text-[13px] font-medium rounded-lg transition-colors ${
                activeTab === "atraso"
                  ? "bg-primary text-primary-foreground"
                  : "bg-card text-foreground hover:bg-secondary"
              }`}
            >
              Explicação do Atraso
            </button>
          )}
          <button
            onClick={() => setActiveTab("similares")}
            className={`px-3 py-1.5 text-[13px] font-medium rounded-lg transition-colors ${
              activeTab === "similares"
                ? "bg-primary text-primary-foreground"
                : "bg-card text-foreground hover:bg-secondary"
            }`}
          >
            Proposições Similares
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="px-6 py-5">
        {/* TAB 1 - Resumo */}
        {activeTab === "resumo" && (
          <div className="space-y-4">
            {/* Stat Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              <div className="bg-secondary rounded-md p-3">
                <p className="text-[11px] uppercase text-muted-foreground mb-1">Em tramitação</p>
                <p className="text-[18px] font-medium text-foreground">{proposition.diasTotais}d</p>
                <p className="text-[11px] text-muted-foreground">dias totais</p>
              </div>
              <div className={`rounded-md p-3 ${proposition.atraso > 0 ? 'bg-amber-50' : 'bg-secondary'}`}>
                <p className="text-[11px] uppercase text-muted-foreground mb-1">Etapa atual</p>
                <p className={`text-[18px] font-medium ${proposition.atraso > 0 ? 'text-amber-700' : 'text-foreground'}`}>
                  {proposition.diasNaEtapa}d
                </p>
                <p className={`text-[11px] ${proposition.atraso > 0 ? 'text-amber-600 font-medium' : 'text-muted-foreground'}`}>
                  +{proposition.atraso}d acima mediana
                </p>
              </div>
              <div className="bg-secondary rounded-md p-3">
                <p className="text-[11px] uppercase text-muted-foreground mb-1">Eventos</p>
                <p className="text-[18px] font-medium text-foreground">{proposition.eventosRelevantes}</p>
                <p className="text-[11px] text-muted-foreground">relevantes</p>
              </div>
              <div className="bg-secondary rounded-md p-3">
                <p className="text-[11px] uppercase text-muted-foreground mb-1">Retornos de fase</p>
                <p className="text-[18px] font-medium text-foreground">{proposition.recorrenciasFase}</p>
                <p className="text-[11px] text-muted-foreground">recorrências</p>
              </div>
            </div>

            {/* Tag Row */}
            <div className="flex flex-wrap gap-2">
              <span className="inline-flex items-center px-3 py-1 bg-primary text-primary-foreground rounded-full text-[11px] font-medium">
                {proposition.faseAtual}
              </span>
              <span className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-700 border border-blue-200 rounded-full text-[11px] font-medium">
                {proposition.casaAtual}
              </span>
              <span className={`inline-flex items-center px-3 py-1 border rounded-full text-[11px] font-medium ${delayStatus.color}`}>
                {delayStatus.label}
              </span>
              <span className="inline-flex items-center px-3 py-1 bg-muted text-muted-foreground rounded-full text-[11px] font-medium">
                {proposition.fasesPercorridas} de 8 fases
              </span>
            </div>

            {/* Disclaimer */}
            <p className="text-[11px] text-muted-foreground italic border-t border-border pt-3">
              Gerado automaticamente com base nos dados normalizados de tramitação.
            </p>
          </div>
        )}

        {/* TAB 2 - Explicação do Atraso */}
        {activeTab === "atraso" && proposition.atraso > 0 && (
          <div className="space-y-4">
            {/* Deviation Banner */}
            <div className="flex items-center gap-4 p-4 bg-amber-50 border border-amber-200 rounded-lg">
              <div className="text-[28px] font-medium text-amber-700">
                +{proposition.atraso}d
              </div>
              <div className="flex-1">
                <p className="text-[12px] text-foreground">
                  acima da mediana histórica para a {proposition.faseAtual}
                </p>
                <p className="text-[11px] text-muted-foreground mt-0.5">
                  Referência: {proposition.medianaFase}d · Acumulado atual: {proposition.diasNaEtapa}d
                </p>
              </div>
              <span className={`inline-flex items-center px-3 py-1.5 border rounded-full text-[11px] font-medium whitespace-nowrap ${delayStatus.color}`}>
                {delayStatus.label}
              </span>
            </div>

            {/* Desvio por fase */}
            <div>
              <p className="text-[11px] uppercase text-muted-foreground mb-3">Desvio por fase</p>
              <div className="space-y-2">
                {phases.map((phase, idx) => (
                  <div key={idx} className="flex items-center gap-3">
                    <div className="w-[190px] truncate">
                      <span className={`text-[12px] ${phase.isCurrent ? 'text-primary font-medium' : 'text-muted-foreground'}`}>
                        {phase.fase}
                      </span>
                    </div>
                    <div className="flex-1 h-6 bg-secondary rounded-sm overflow-hidden">
                      <div
                        className={`h-full ${phase.atrasoDias && phase.atrasoDias > 0 ? 'bg-amber-500' : 'bg-primary'}`}
                        style={{ width: `${(phase.duracaoDias / maxDuration) * 100}%` }}
                      />
                    </div>
                    <div className="w-[32px] text-right">
                      <span className="text-[12px] text-muted-foreground">{phase.duracaoDias}d</span>
                    </div>
                    <div className="w-[36px] text-right">
                      {phase.atrasoDias && phase.atrasoDias > 0 ? (
                        <span className="text-[11px] text-amber-600">+{phase.atrasoDias}d</span>
                      ) : (
                        <span className="text-[11px] text-muted-foreground">—</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Fatores associados */}
            <div>
              <p className="text-[11px] uppercase text-muted-foreground mb-3">Fatores associados</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {factors.slice(0, 4).map((factor, idx) => {
                  const Icon = factor.icon;
                  return (
                    <div key={idx} className="flex items-start gap-3 bg-secondary rounded-md p-3">
                      <Icon className="w-4 h-4 text-muted-foreground flex-shrink-0 mt-0.5" />
                      <p className="text-[12px] text-foreground leading-relaxed">{factor.text}</p>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Disclaimer */}
            <p className="text-[11px] text-muted-foreground italic border-t border-border pt-3">
              Análise baseada em comparação estatística com tramitações similares. Não representa avaliação causal definitiva.
            </p>
          </div>
        )}

        {/* TAB 3 - Proposições Similares */}
        {activeTab === "similares" && (
          <div className="space-y-4">
            {/* Subtitle */}
            <p className="text-[12px] text-muted-foreground">
              Proposições com perfil similar — mesmo tipo, tema e comportamento de tramitação
            </p>

            {/* List */}
            <div className="divide-y divide-border">
              {mockSimilarPropositions.map((prop, idx) => (
                <div key={idx} className="flex items-center gap-4 py-3">
                  <div className="w-[100px]">
                    <span className="text-[12px] font-medium text-foreground">
                      {prop.tipo} {prop.numero}
                    </span>
                  </div>
                  <span className="inline-flex items-center px-2.5 py-1 bg-primary text-primary-foreground rounded-full text-[11px]">
                    {prop.fase}
                  </span>
                  {prop.atraso > 0 ? (
                    <span className="inline-flex items-center px-2.5 py-1 bg-amber-100 text-amber-700 border border-amber-200 rounded-full text-[11px]">
                      +{prop.atraso}d atraso
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-2.5 py-1 bg-muted text-muted-foreground rounded-full text-[11px]">
                      No prazo
                    </span>
                  )}
                  <div className="ml-auto text-right">
                    <span className="text-[12px] text-muted-foreground">{prop.diasPipeline} dias</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Disclaimer */}
            <p className="text-[11px] text-muted-foreground italic border-t border-border pt-3">
              Sugestão baseada em tipo, tema e comportamento de tramitação. Requer base histórica mínima de 50 casos similares para ativação plena.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
