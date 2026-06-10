import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  FileText,
  Activity,
  Clock,
  TrendingUp,
  Download,
  Calendar,
  Search,
  Filter,
  X,
} from "lucide-react";
import { KPICard } from "@/shared/components/KPICard";
import { PipelineStage } from "@/features/proposicoes/components/PipelineStage";
import { HouseTransitions } from "@/features/proposicoes/components/HouseTransitions";
import { BottleneckAnalytics } from "@/features/proposicoes/components/BottleneckAnalytics";
import { PropositionsTable, Proposition } from "@/features/proposicoes/components/PropositionsTable";
import { FilterChips, FilterOption } from "@/features/filtros/FilterChips";
import { useDashboard } from "@/shared/lib/hooks/useDashboard";
import { listarProposicoes } from "@/shared/lib/api";
import { mapProposicaoToProposition } from "@/shared/lib/mappers";
import { PROPOSICOES_MOCK } from "@/shared/lib/mock-data";
import { TIPOS_PROPOSICAO, STATUS_PROPOSICAO } from "@/shared/constants";
import type { FiltrosProposicao } from "@/shared/types";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

const FILTROS_VAZIOS: FiltrosProposicao = {
  busca: "",
  orgaoOrigem: "",
  tipo: "",
  status: "",
  dataInicio: "",
  dataFim: "",
};

export function DashboardPage() {
  const navigate = useNavigate();
  const [filtros, setFiltros] = useState<FiltrosProposicao>(FILTROS_VAZIOS);
  const [filterOpen, setFilterOpen] = useState(false);
  const [localSearch, setLocalSearch] = useState("");
  const [proposicoesData, setProposicoesData] = useState<{ items: Proposition[]; total: number }>({ items: [], total: 0 });
  const [pagina, setPagina] = useState(1);
  const [loadingProps, setLoadingProps] = useState(false);

  // Debounce search term local state change to filters state
  useEffect(() => {
    const handler = setTimeout(() => {
      setFiltros((prev) => ({ ...prev, busca: localSearch }));
      setPagina(1);
    }, 400);
    return () => clearTimeout(handler);
  }, [localSearch]);

  // Bind to useDashboard hook for real API statistics and charts
  const {
    metricas,
    pipelineData,
    timeSeriesData,
    bottleneckData,
    houseTransitionData,
    estoqueData,
    handoffData,
    coberturaData,
    qualidadeData,
  } = useDashboard(filtros);

  // Load propositions list with filters and pagination
  useEffect(() => {
    setLoadingProps(true);
    listarProposicoes(filtros, pagina, 10)
      .then((res) => {
        const mapped = res.items.map((p) => mapProposicaoToProposition(p));
        setProposicoesData({ items: mapped, total: res.total });
      })
      .catch((err) => {
        console.error("Erro ao listar proposições da API, usando fallback mock:", err);
        // Fallback to local mocks
        const mappedMock = PROPOSICOES_MOCK.map((p) => mapProposicaoToProposition(p));
        setProposicoesData({ items: mappedMock, total: PROPOSICOES_MOCK.length });
      })
      .finally(() => {
        setLoadingProps(false);
      });
  }, [filtros, pagina]);

  const handlePropositionClick = (id: string) => {
    navigate(`/proposicoes/${id}`);
  };

  const handleExport = () => {
    // Mock export action
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify({ metricas, bottleneckData, houseTransitionData }));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `lextrack_relatorio_${new Date().toISOString().split('T')[0]}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  // Convert filtros fields to FilterOption array for FilterChips display
  const getActiveFilters = (): FilterOption[] => {
    const list: FilterOption[] = [];
    if (filtros.orgaoOrigem) {
      list.push({
        id: "casa",
        category: "casa",
        label: filtros.orgaoOrigem === "Câmara dos Deputados" ? "Câmara" : filtros.orgaoOrigem === "Senado Federal" ? "Senado" : filtros.orgaoOrigem,
      });
    }
    if (filtros.tipo) {
      list.push({
        id: "tipo",
        category: "tipo",
        label: filtros.tipo,
      });
    }
    if (filtros.status) {
      list.push({
        id: "status",
        category: "status",
        label: filtros.status,
      });
    }
    return list;
  };

  const handleRemoveFilter = (filterId: string) => {
    if (filterId === "casa") {
      setFiltros((prev) => ({ ...prev, orgaoOrigem: "" }));
    } else if (filterId === "tipo") {
      setFiltros((prev) => ({ ...prev, tipo: "" }));
    } else if (filterId === "status") {
      setFiltros((prev) => ({ ...prev, status: "" }));
    }
    setPagina(1);
  };

  const handleClearAllFilters = () => {
    setLocalSearch("");
    setFiltros(FILTROS_VAZIOS);
    setPagina(1);
  };

  const activeChips = getActiveFilters();

  return (
    <div className="p-6 space-y-6 animate-fade-in text-foreground bg-background">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="font-display font-700 text-2xl text-foreground">
            Sistema de Monitoramento Legislativo Federal
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Análise de tramitação e gargalos processuais - Congresso Nacional
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-secondary text-secondary-foreground rounded-lg hover:bg-secondary/80 transition-colors">
            <Calendar className="w-4 h-4 text-primary" />
            <span className="text-sm font-medium">Maio 2026</span>
          </button>
          <button
            onClick={handleExport}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg font-semibold hover:bg-primary/90 transition-colors"
          >
            <Download className="w-4 h-4 text-primary-foreground" />
            <span className="text-sm">Exportar Relatório</span>
          </button>
        </div>
      </div>

      {/* Unified Search and Advanced Filters */}
      <div className="space-y-3 bg-card border border-border rounded-lg p-4 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Buscar por número, ementa, autor ou palavra-chave..."
              value={localSearch}
              onChange={(e) => setLocalSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 bg-input-background border border-border rounded-lg text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
            />
            {localSearch && (
              <button
                onClick={() => setLocalSearch("")}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
          <button
            onClick={() => setFilterOpen(!filterOpen)}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-lg border transition-colors ${
              filterOpen || activeChips.length > 0
                ? "bg-primary text-primary-foreground border-primary hover:bg-primary/90"
                : "bg-secondary text-secondary-foreground border-transparent hover:bg-secondary/80"
            }`}
          >
            <Filter className="w-4 h-4" />
            <span className="text-sm font-medium">Filtros Avançados</span>
            {activeChips.length > 0 && (
              <span className="inline-flex items-center justify-center w-5 h-5 bg-primary-foreground text-primary rounded-full text-xs font-semibold">
                {activeChips.length}
              </span>
            )}
          </button>
        </div>

        {/* Advanced Filters Drawer Panel */}
        {filterOpen && (
          <div className="pt-4 border-t border-border grid grid-cols-1 md:grid-cols-4 gap-4 animate-slide-up">
            {/* Casa Legislativa */}
            <div>
              <label className="text-[10px] font-bold text-muted-foreground uppercase mb-1.5 block">
                Órgão / Casa
              </label>
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    setFiltros((prev) => ({ ...prev, orgaoOrigem: "" }));
                    setPagina(1);
                  }}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                    !filtros.orgaoOrigem
                      ? "bg-primary text-primary-foreground border-primary"
                      : "bg-secondary text-secondary-foreground border-transparent hover:bg-secondary/80"
                  }`}
                >
                  Todos
                </button>
                <button
                  onClick={() => {
                    setFiltros((prev) => ({ ...prev, orgaoOrigem: "Câmara dos Deputados" }));
                    setPagina(1);
                  }}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                    filtros.orgaoOrigem === "Câmara dos Deputados"
                      ? "bg-primary text-primary-foreground border-primary"
                      : "bg-secondary text-secondary-foreground border-transparent hover:bg-secondary/80"
                  }`}
                >
                  Câmara
                </button>
                <button
                  onClick={() => {
                    setFiltros((prev) => ({ ...prev, orgaoOrigem: "Senado Federal" }));
                    setPagina(1);
                  }}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                    filtros.orgaoOrigem === "Senado Federal"
                      ? "bg-primary text-primary-foreground border-primary"
                      : "bg-secondary text-secondary-foreground border-transparent hover:bg-secondary/80"
                  }`}
                >
                  Senado
                </button>
              </div>
            </div>

            {/* Tipo de Proposição */}
            <div>
              <label className="text-[10px] font-bold text-muted-foreground uppercase mb-1.5 block">
                Tipo
              </label>
              <select
                value={filtros.tipo}
                onChange={(e) => {
                  setFiltros((prev) => ({ ...prev, tipo: e.target.value }));
                  setPagina(1);
                }}
                className="w-full px-3 py-2 bg-input-background border border-border rounded-lg text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="">Qualquer tipo</option>
                {TIPOS_PROPOSICAO.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>

            {/* Situação / Status */}
            <div>
              <label className="text-[10px] font-bold text-muted-foreground uppercase mb-1.5 block">
                Status
              </label>
              <select
                value={filtros.status}
                onChange={(e) => {
                  setFiltros((prev) => ({ ...prev, status: e.target.value }));
                  setPagina(1);
                }}
                className="w-full px-3 py-2 bg-input-background border border-border rounded-lg text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="">Qualquer status</option>
                {STATUS_PROPOSICAO.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>

            {/* Datas */}
            <div>
              <label className="text-[10px] font-bold text-muted-foreground uppercase mb-1.5 block">
                Período de Apresentação
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="date"
                  value={filtros.dataInicio}
                  onChange={(e) => {
                    setFiltros((prev) => ({ ...prev, dataInicio: e.target.value }));
                    setPagina(1);
                  }}
                  className="w-full px-2 py-1.5 bg-input-background border border-border rounded-lg text-xs text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                />
                <span className="text-[10px] text-muted-foreground font-semibold">ATÉ</span>
                <input
                  type="date"
                  value={filtros.dataFim}
                  onChange={(e) => {
                    setFiltros((prev) => ({ ...prev, dataFim: e.target.value }));
                    setPagina(1);
                  }}
                  className="w-full px-2 py-1.5 bg-input-background border border-border rounded-lg text-xs text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
            </div>
          </div>
        )}

        {/* Filter Chips Display */}
        <FilterChips
          activeFilters={activeChips}
          onRemoveFilter={handleRemoveFilter}
          onClearAll={handleClearAllFilters}
        />
      </div>

      {/* KPIs Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Total de Proposições"
          value={metricas?.totalProposicoes ?? "2.847"}
          subtitle="Registradas no painel"
          icon={FileText}
          trend={{ value: "+12% vs mês anterior", isPositive: true }}
        />
        <KPICard
          title="Em Tramitação Ativa"
          value={metricas?.totalEmTramitacao ?? "1.423"}
          subtitle="Câmara e Senado"
          icon={Activity}
          trend={{ value: "+8% vs mês anterior", isPositive: true }}
        />
        <KPICard
          title="Com Atraso Crítico"
          value={metricas?.proposicoesComAtraso ?? "234"}
          subtitle=">15 dias acima da mediana"
          icon={Clock}
          trend={{ value: "-5% vs mês anterior", isPositive: true }}
          isAlarm
        />
        <KPICard
          title="Tempo Mediano Global"
          value={metricas?.tempoMedioTramitacao ? `${metricas.tempoMedioTramitacao} dias` : "54 dias"}
          subtitle="Por fase de tramitação"
          icon={TrendingUp}
          trend={{ value: "+3 dias vs trimestre", isPositive: false }}
        />
      </div>

      {/* Estoque de Proposições por Fase */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-card border border-border rounded-lg p-6">
          <h2 className="text-lg font-semibold text-foreground mb-1">
            Estoque Operacional Ativo
          </h2>
          <p className="text-sm text-muted-foreground mb-4">
            Matérias em tramitação ativa e permanência de trabalho corrente
          </p>
          {estoqueData && estoqueData.ativo.length > 0 ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
              {estoqueData.ativo.map((item) => (
                <div key={item.codigo} className="bg-secondary/40 border border-border rounded-lg p-4 flex flex-col justify-between hover:border-primary/50 transition-colors">
                  <span className="text-xs text-muted-foreground font-medium block truncate" title={item.nome}>
                    {item.nome}
                  </span>
                  <div className="flex items-baseline gap-2 mt-2">
                    <span className="text-2xl font-bold text-foreground">{item.total}</span>
                    <span className="text-[10px] text-muted-foreground uppercase">matérias</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-sm text-muted-foreground p-6 text-center border border-dashed border-border rounded-lg">
              Nenhum estoque ativo registrado.
            </div>
          )}
        </div>

        <div className="bg-card border border-border rounded-lg p-6 flex flex-col justify-between">
          <div>
            <h2 className="text-lg font-semibold text-foreground mb-1">
              Estoque Passivo / Histórico
            </h2>
            <p className="text-sm text-muted-foreground mb-4">
              Ciclo processual encerrado e memória legislativa
            </p>
            {estoqueData && estoqueData.passivo.length > 0 ? (
              <div className="space-y-4">
                {estoqueData.passivo.map((item) => (
                  <div key={item.codigo} className="bg-secondary/40 border border-border rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted-foreground font-semibold uppercase">{item.nome}</span>
                      <span className="bg-primary/10 text-primary text-xs px-2.5 py-0.5 rounded-full font-bold">
                        {item.total} matérias
                      </span>
                    </div>
                    <p className="text-[11px] text-muted-foreground mt-2">
                      Total de proposições que concluíram definitivamente seu trâmite regulamentar.
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-muted-foreground p-6 text-center border border-dashed border-border rounded-lg">
                Nenhum estoque passivo registrado.
              </div>
            )}
          </div>
          <div className="p-3 bg-secondary/30 border border-border rounded-lg mt-4">
            <p className="text-[11px] text-muted-foreground">
              O estoque passivo reflete matérias arquivadas, sancionadas ou retiradas de forma definitiva.
            </p>
          </div>
        </div>
      </div>

      {/* Pipeline Stage Visualization */}
      <div className="bg-card border border-border rounded-lg p-6">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
          <div>
            <h2 className="text-lg font-semibold text-foreground">
              Pipeline de Tramitação Legislativa
            </h2>
            <p className="text-sm text-muted-foreground mt-0.5">
              Distribuição por fase processual canônica com tempo mediano por etapa
            </p>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-primary" />
            <span className="text-xs text-muted-foreground">
              Taxa de conclusão: 5.6% • Mediana global: {metricas?.tempoMedioTramitacao ?? 54} dias
            </span>
          </div>
        </div>
        <div className="flex items-end gap-0 overflow-x-auto pb-4">
          {(pipelineData as { name: string; count: number; percentage: number; medianDays: number }[]).map((stage, idx) => (
            <PipelineStage
              key={stage.name}
              name={stage.name}
              count={stage.count}
              percentage={stage.percentage}
              medianDays={stage.medianDays}
              isActive={idx === 2}
            />
          ))}
        </div>
      </div>

      {/* House Transitions Widget */}
      <HouseTransitions
        transitions={houseTransitionData.transitions}
        totalCamara={houseTransitionData.totalCamara}
        totalSenado={houseTransitionData.totalSenado}
        handoffData={handoffData || undefined}
      />

      {/* Charts & Reliability section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Time Series chart */}
        <div className="lg:col-span-2 bg-card border border-border rounded-lg p-6">
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-foreground">
              Evolução Temporal de Proposições
            </h2>
            <p className="text-sm text-muted-foreground mt-0.5">
              Entradas e saídas mensais do sistema de tramitação
            </p>
          </div>
          <div className="h-[280px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={timeSeriesData}>
                <CartesianGrid key="grid" strokeDasharray="3 3" stroke="var(--border)" opacity={0.4} />
                <XAxis
                  key="xaxis"
                  dataKey="mes"
                  tick={{ fontSize: 12, fill: "var(--muted-foreground)" }}
                  stroke="var(--border)"
                />
                <YAxis key="yaxis" tick={{ fontSize: 12, fill: "var(--muted-foreground)" }} stroke="var(--border)" />
                <Tooltip
                  key="tooltip"
                  contentStyle={{
                    backgroundColor: "var(--card)",
                    border: "1px solid var(--border)",
                    borderRadius: "8px",
                    color: "var(--foreground)",
                    fontSize: "12px",
                  }}
                />
                <Legend
                  key="legend"
                  wrapperStyle={{ fontSize: "12px" }}
                  iconType="circle"
                />
                <Line
                  key="line-entradas"
                  type="monotone"
                  dataKey="entradas"
                  stroke="var(--primary)"
                  strokeWidth={2.5}
                  dot={{ fill: "var(--primary)", r: 4 }}
                  name="Entradas"
                />
                <Line
                  key="line-saidas"
                  type="monotone"
                  dataKey="saidas"
                  stroke="var(--volt-400)"
                  strokeWidth={2.5}
                  dot={{ fill: "var(--volt-400)", r: 4 }}
                  name="Saídas"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Cobertura e Qualidade da Base */}
        <div className="bg-card border border-border rounded-lg p-6 flex flex-col justify-between">
          <div>
            <div className="mb-4">
              <h2 className="text-lg font-semibold text-foreground">
                Qualidade da Base Local
              </h2>
              <p className="text-sm text-muted-foreground mt-0.5">
                Completude e integridade dos registros locais
              </p>
            </div>
            {qualidadeData ? (
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-sm text-muted-foreground">Completude Geral</span>
                    <span className="text-sm font-bold text-foreground">
                      {qualidadeData.completudePorcentagem}%
                    </span>
                  </div>
                  <div className="h-2 bg-secondary rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${
                        qualidadeData.completudePorcentagem >= 80 ? "bg-emerald-500" : "bg-amber-500"
                      }`}
                      style={{ width: `${qualidadeData.completudePorcentagem}%` }}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4 pt-2">
                  <div className="bg-secondary/40 border border-border rounded-lg p-3">
                    <span className="text-[10px] text-muted-foreground uppercase font-bold block">
                      Campos Analisados
                    </span>
                    <span className="text-lg font-bold text-foreground">{qualidadeData.camposAnalisados}</span>
                  </div>
                  <div className="bg-secondary/40 border border-border rounded-lg p-3">
                    <span className="text-[10px] text-muted-foreground uppercase font-bold block">
                      Total Matérias
                    </span>
                    <span className="text-lg font-bold text-foreground">{qualidadeData.totalProposicoes}</span>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">Carregando qualidade da base...</p>
            )}

            <div className="mt-6 border-t border-border pt-4">
              <h2 className="text-sm font-semibold text-foreground mb-1">
                Cobertura de Ingestão
              </h2>
              <p className="text-xs text-muted-foreground mb-3">
                Volume ingerido localmente contra o total nas APIs oficiais
              </p>
              {coberturaData && coberturaData.length > 0 ? (
                <div className="max-h-[160px] overflow-y-auto space-y-2 pr-1">
                  {coberturaData.map((c, idx) => (
                    <div key={idx} className="flex items-center justify-between text-xs p-2 bg-secondary/50 rounded border border-border">
                      <div>
                        <span className="font-semibold text-foreground">{c.tipoProposicao}</span>
                        <span className="text-muted-foreground ml-1.5">({c.ano})</span>
                      </div>
                      <div className="text-right">
                        <span className="text-foreground font-medium">{c.totalLocal} / {c.totalApiOficial}</span>
                        <span className={`ml-2 px-1.5 py-0.5 rounded font-bold ${
                          c.percentualCobertura >= 95 ? "bg-emerald-100 text-emerald-800" : "bg-amber-100 text-amber-800"
                        }`}>
                          {c.percentualCobertura}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-muted-foreground">Nenhum snapshot de cobertura registrado.</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Bottlenecks Analytics widget */}
      <BottleneckAnalytics
        porOrgao={bottleneckData.porOrgao}
        porFase={bottleneckData.porFase}
        porTema={bottleneckData.porTema}
      />

      {/* Propositions Table widget */}
      <div className="space-y-4">
        <div>
          <h2 className="text-lg font-semibold text-foreground">
            Proposições em Análise Detalhada
          </h2>
          <p className="text-sm text-muted-foreground mt-0.5">
            Acompanhamento individualizado com indicadores de atraso, cobertura e status de tramitação
          </p>
        </div>

        {loadingProps && proposicoesData.items.length === 0 ? (
          <div className="flex items-center justify-center p-12 bg-card border border-border rounded-lg">
            <span className="text-sm text-muted-foreground">Carregando proposições...</span>
          </div>
        ) : (
          <>
            <PropositionsTable
              propositions={proposicoesData.items}
              onPropositionClick={handlePropositionClick}
            />

            {/* Pagination Controls */}
            {proposicoesData.total > 10 && (
              <div className="flex items-center justify-between mt-4">
                <span className="text-xs text-muted-foreground">
                  Mostrando {proposicoesData.items.length} de {proposicoesData.total} proposições
                </span>
                <div className="flex gap-2">
                  <button
                    disabled={pagina === 1}
                    onClick={() => setPagina((prev) => prev - 1)}
                    className="px-3 py-1.5 bg-secondary text-secondary-foreground border border-border rounded-lg text-xs font-semibold hover:bg-secondary/80 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Anterior
                  </button>
                  <button
                    disabled={pagina * 10 >= proposicoesData.total}
                    onClick={() => setPagina((prev) => prev + 1)}
                    className="px-3 py-1.5 bg-secondary text-secondary-foreground border border-border rounded-lg text-xs font-semibold hover:bg-secondary/80 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Próxima
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
