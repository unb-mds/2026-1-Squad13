import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  FileText,
  Calendar,
  Clock,
  Building2,
  TrendingUp,
  RotateCcw,
  ArrowRightLeft,
  Download,
  Share2,
} from "lucide-react";
import { MetricCard } from "@/shared/components/MetricCard";
import { PhaseTimeline } from "@/features/proposicoes/components/PhaseTimeline";
import { EventTimeline } from "@/features/proposicoes/components/EventTimeline";
import { HouseTransitDiagram } from "@/features/proposicoes/components/HouseTransitDiagram";
import { DataReliability } from "@/features/proposicoes/components/DataReliability";
import { InfoTooltip } from "@/shared/components/InfoTooltip";
import { AIInsightsCard } from "@/features/proposicoes/components/AIInsightsCard";
import { useProposicao } from "@/shared/lib/hooks/useProposicao";
import { Spinner } from "@/shared/ui";

export function DetalheProposicaoPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [selectedPhaseId, setSelectedPhaseId] = useState<string | null>(null);

  // Bind to useProposicao hook
  const {
    proposicao,
    phases,
    events,
    transitSteps,
    reliability,
    loading,
  } = useProposicao(id);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Spinner className="w-10 h-10 text-primary" />
      </div>
    );
  }

  if (!proposicao) {
    return (
      <div className="p-6 text-center text-foreground bg-background min-h-screen">
        <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
        <p className="text-white font-medium mb-1">Proposição não encontrada</p>
        <button onClick={() => navigate("/dashboard")} className="text-sm text-primary hover:underline">
          Voltar para a Dashboard
        </button>
      </div>
    );
  }

  // Compute metrics dynamically from phases and events
  const totalDuration = proposicao.diasTotais;
  const totalRecurrences = phases.filter((p) => p.isRecorrente).length;
  const transitCount = transitSteps.length > 1 ? transitSteps.length - 1 : 0;
  const relevantEventsCount = events.length;
  const uniquePhasesCount = new Set(phases.map(p => p.fase)).size;

  const getAtrasoColor = () => {
    if (proposicao.atraso > 15) return "bg-red-100/10 text-red-400 border-red-500/25";
    if (proposicao.atraso > 0) return "bg-amber-100/10 text-amber-400 border-amber-500/25";
    return "bg-green-100/10 text-green-400 border-green-500/25";
  };

  const getCoberturaColor = () => {
    if (proposicao.coberturaDados >= 90) return "bg-emerald-100/10 text-emerald-400 border-emerald-500/25";
    if (proposicao.coberturaDados >= 70) return "bg-amber-100/10 text-amber-400 border-amber-500/25";
    return "bg-red-100/10 text-red-400 border-red-500/25";
  };

  const handleExportAnalysis = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify({ proposicao, phases, events, transitSteps }));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `lextrack_analise_${proposicao.tipo}_${proposicao.numero.replace('/', '_')}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="min-h-screen bg-background text-foreground animate-fade-in">
      {/* Header */}
      <header className="bg-card border-b border-border sticky top-0 z-10 shadow-sm">
        <div className="max-w-[1400px] mx-auto px-4 md:px-6 py-3 md:py-4">
          {/* Breadcrumb */}
          <div className="flex items-center gap-2 mb-3 text-xs text-muted-foreground">
            <button onClick={() => navigate("/dashboard")} className="hover:text-primary transition-colors">
              Dashboard
            </button>
            <span>/</span>
            <button onClick={() => navigate("/proposicoes")} className="hover:text-primary transition-colors">
              Proposições
            </button>
            <span>/</span>
            <span className="text-foreground font-medium">
              {proposicao.tipo} {proposicao.numero}
            </span>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between">
            <button
              onClick={() => navigate(-1)}
              className="flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors"
            >
              <ArrowLeft className="w-4 md:w-5 h-4 md:h-5" />
              <span className="text-xs md:text-sm font-medium">Voltar</span>
            </button>

            <div className="flex items-center gap-2 md:gap-3">
              <button className="hidden sm:flex items-center gap-2 px-3 md:px-4 py-1.5 md:py-2 bg-secondary text-secondary-foreground rounded-lg hover:bg-secondary/80 transition-colors">
                <Share2 className="w-4 h-4 text-secondary-foreground" />
                <span className="text-xs md:text-sm">Compartilhar</span>
              </button>
              <button
                onClick={handleExportAnalysis}
                className="flex items-center gap-2 px-3 md:px-4 py-1.5 md:py-2 bg-primary text-primary-foreground rounded-lg font-semibold hover:bg-primary/90 transition-colors"
              >
                <Download className="w-4 h-4 text-primary-foreground" />
                <span className="text-xs md:text-sm hidden sm:inline">Exportar Análise</span>
                <span className="text-xs sm:hidden">Exportar</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-[1400px] mx-auto px-4 md:px-6 py-4 md:py-6 space-y-4 md:space-y-6">
        {/* Proposition Header */}
        <div className="bg-card border border-border rounded-lg p-4 md:p-6">
          <div className="flex flex-col md:flex-row items-start gap-4 md:gap-6">
            <div className="flex items-center justify-center w-16 h-16 bg-primary/10 rounded-lg flex-shrink-0">
              <FileText className="w-8 h-8 text-primary" />
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4 mb-3">
                <div className="flex-1">
                  <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3 mb-2">
                    <h1 className="text-xl md:text-2xl font-semibold text-foreground">
                      {proposicao.tipo} {proposicao.numero}
                    </h1>
                    <span className="inline-flex items-center px-3 py-1 bg-primary/10 text-primary border border-primary/20 rounded-lg text-xs sm:text-sm font-medium w-fit">
                      {proposicao.tipo === "PL" ? "Projeto de Lei" : proposicao.tipo === "PEC" ? "Proposta de Emenda Constitucional" : "Matéria Legislativa"}
                    </span>
                  </div>
                  <p className="text-xs sm:text-sm text-muted-foreground mb-1">
                    Autoria: {proposicao.autor} • Última movimentação: {proposicao.dataUltimoEvento}
                  </p>
                </div>

                <div className="flex flex-row md:flex-col gap-2 items-start md:items-end">
                  <span className={`inline-flex items-center px-3 py-1.5 border rounded-lg text-xs sm:text-sm font-medium ${getAtrasoColor()}`}>
                    {proposicao.atraso > 0 ? `+${proposicao.atraso}d atraso` : "No prazo"}
                  </span>
                  <span className={`inline-flex items-center px-3 py-1.5 border rounded-lg text-xs sm:text-sm font-medium ${getCoberturaColor()}`}>
                    {proposicao.coberturaDados}% cobertura
                  </span>
                </div>
              </div>

              <p className="text-sm md:text-base text-foreground leading-relaxed mb-4">
                {proposicao.ementa}
              </p>

              <div className="pt-4 border-t border-border space-y-4">
                {/* Progress Bar */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-medium text-muted-foreground">
                      Progresso no Pipeline Legislativo
                    </span>
                    <span className="text-xs font-semibold text-primary">
                      {uniquePhasesCount} de 8 fases
                    </span>
                  </div>
                  <div className="h-2 bg-secondary rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary rounded-full transition-all"
                      style={{
                        width: `${Math.min(
                          (uniquePhasesCount / 8) * 100,
                          100
                        )}%`,
                      }}
                    />
                  </div>
                </div>

                {/* Current Status */}
                <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-6">
                  <div className="flex items-center gap-2">
                    <Building2 className="w-4 h-4 text-muted-foreground" />
                    <span className="text-xs sm:text-sm text-muted-foreground">
                      Casa Atual: <span className="font-medium text-foreground">{proposicao.casaAtual}</span>
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-muted-foreground" />
                    <span className="text-xs sm:text-sm text-muted-foreground">
                      Fase Atual: <span className="font-medium text-foreground">{proposicao.faseAtual}</span>
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Metrics Cards */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <MetricCard
            label="Dias Totais Acumulados"
            value={totalDuration}
            icon={Calendar}
            subtitle="Tempo total de tramitação"
            tooltip="Tempo total decorrido desde a apresentação da proposição."
          />
          <MetricCard
            label="Dias na Etapa Atual"
            value={proposicao.diasNaEtapa}
            icon={Clock}
            highlight
            subtitle={`${proposicao.faseAtual} - Em análise`}
            tooltip="Tempo acumulado na fase atual de tramitação."
          />
          <MetricCard
            label="Fases Percorridas"
            value={`${uniquePhasesCount}/8`}
            icon={TrendingUp}
            subtitle="Fases canônicas"
            tooltip="Número de fases legislativas por onde a proposição já tramitou."
          />
          <MetricCard
            label="Eventos Relevantes"
            value={relevantEventsCount}
            icon={FileText}
            subtitle="Documentados"
            tooltip="Eventos que impactaram a tramitação: relatórios, audiências, emendas, etc."
          />
          <MetricCard
            label="Recorrências de Fase"
            value={totalRecurrences}
            icon={RotateCcw}
            subtitle="Retornos detectados"
            tooltip="Número de vezes que a matéria retornou para etapas já visitadas anteriormente."
          />
          <MetricCard
            label="Transições entre Casas"
            value={transitCount}
            icon={ArrowRightLeft}
            subtitle="Câmara ↔ Senado"
            tooltip="Número de trânsitos registrados entre as duas casas legislativas."
          />
        </div>

        {/* AI Insights */}
        <AIInsightsCard
          proposition={{
            numero: proposicao.numero,
            tipo: proposicao.tipo,
            diasTotais: totalDuration,
            diasNaEtapa: proposicao.diasNaEtapa,
            faseAtual: proposicao.faseAtual,
            casaAtual: proposicao.casaAtual,
            atraso: proposicao.atraso,
            eventosRelevantes: relevantEventsCount,
            recorrenciasFase: totalRecurrences,
            medianaFase: 45,
            fasesPercorridas: uniquePhasesCount,
          }}
          phasesHistory={phases.map((p) => ({
            fase: p.fase,
            duracaoDias: p.duracaoDias,
            atrasoDias: p.atrasoDias || 0,
            isCurrent: p.isCurrent,
          }))}
        />

        {/* Phase Timeline */}
        <PhaseTimeline phases={phases} onPhaseClick={setSelectedPhaseId} />

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* House Transit */}
          <HouseTransitDiagram steps={transitSteps} historicoUnificado={true} />

          {/* Data Reliability */}
          <DataReliability {...reliability} />
        </div>

        {/* Event Timeline - Collapsible */}
        <EventTimeline events={events} filterByPhaseId={selectedPhaseId} />

        {/* Methodological Notes */}
        <div className="bg-gradient-to-br from-blue-50/5 to-blue-50/20 border border-blue-500/20 rounded-lg p-6">
          <div className="flex items-start gap-4">
            <div className="flex items-center justify-center w-11 h-11 bg-primary rounded-xl flex-shrink-0 shadow-sm">
              <FileText className="w-6 h-6 text-primary-foreground" />
            </div>
            <div className="flex-1">
              <h3 className="text-base font-semibold text-white mb-3 flex items-center gap-2">
                Sobre a Metodologia Analítica
                <span className="text-xs font-normal text-primary bg-primary/10 px-2 py-0.5 rounded">
                  Narrativa Temporal Unificada
                </span>
              </h3>
              <div className="grid md:grid-cols-2 gap-3 text-sm text-muted-foreground">
                <div className="flex items-start gap-2.5">
                  <div className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5 flex-shrink-0" />
                  <p className="leading-relaxed">
                    <strong>Fases canônicas</strong> agregam períodos de tramitação;{" "}
                    <strong>eventos relevantes</strong> documentam deliberações e transições estruturantes.
                  </p>
                </div>
                <div className="flex items-start gap-2.5">
                  <div className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5 flex-shrink-0" />
                  <p className="leading-relaxed">
                    <strong>Indicadores de atraso</strong> comparam o tempo atual com a mediana histórica.
                    Valores acima de 15 dias são críticos.
                  </p>
                </div>
                <div className="flex items-start gap-2.5">
                  <div className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5 flex-shrink-0" />
                  <p className="leading-relaxed">
                    <strong>Dados normalizados</strong> de múltiplas fontes oficiais (APIs do Congresso, DOU).
                  </p>
                </div>
                <div className="flex items-start gap-2.5">
                  <div className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5 flex-shrink-0" />
                  <p className="leading-relaxed inline-flex items-center gap-1.5">
                    <strong>Cobertura de dados</strong> reflete completude e confiabilidade da análise.
                    <InfoTooltip content="A cobertura considera: (1) metadados obrigatórios, (2) histórico de eventos, (3) documentos anexos, e (4) consistência temporal. Valores >90% são excelentes." />
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
