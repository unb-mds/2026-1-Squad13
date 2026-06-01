import { useState } from "react";
import {
  FileText,
  Activity,
  Clock,
  TrendingUp,
  Search,
  Filter,
  Download,
  Calendar,
} from "lucide-react";
import { KPICard } from "./components/KPICard";
import { PipelineStage } from "./components/PipelineStage";
import { PropositionsTable, Proposition } from "./components/PropositionsTable";
import { BottleneckAnalytics } from "./components/BottleneckAnalytics";
import { HouseTransitions } from "./components/HouseTransitions";
import PropositionDetail from "./PropositionDetail";
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

const mockPropositions: Proposition[] = [
  {
    id: "1",
    numero: "2547/2023",
    tipo: "PL",
    ementa:
      "Dispõe sobre a proteção de dados pessoais no âmbito da administração pública federal e estabelece diretrizes para tratamento de informações sensíveis.",
    casaAtual: "Câmara",
    faseAtual: "Comissão de Constituição e Justiça",
    diasNaEtapa: 45,
    ultimoEventoRelevante: "Parecer do relator apresentado",
    dataUltimoEvento: "15/04/2026",
    autor: "Dep. Maria Silva (PT-SP)",
    atraso: 12,
    coberturaDados: 94,
    confiabilidade: "alta",
    statusTramitacao: "em-tramitacao",
    transitouEntreCasas: false,
  },
  {
    id: "2",
    numero: "1823/2024",
    tipo: "PL",
    ementa:
      "Altera a Lei nº 8.666/93 para estabelecer critérios de sustentabilidade nas licitações públicas e contratações governamentais.",
    casaAtual: "Senado",
    faseAtual: "Plenário - Discussão",
    diasNaEtapa: 92,
    ultimoEventoRelevante: "Destaque aprovado em plenário",
    dataUltimoEvento: "02/03/2026",
    autor: "Sen. João Santos (PSDB-RJ)",
    atraso: 38,
    coberturaDados: 87,
    confiabilidade: "alta",
    statusTramitacao: "em-atraso",
    transitouEntreCasas: true,
  },
  {
    id: "3",
    numero: "3421/2024",
    tipo: "PLP",
    ementa:
      "Estabelece marco regulatório para inteligência artificial no Brasil, definindo princípios éticos e responsabilidades.",
    casaAtual: "Câmara",
    faseAtual: "Comissão Temática - Análise",
    diasNaEtapa: 23,
    ultimoEventoRelevante: "Audiência pública realizada com especialistas",
    dataUltimoEvento: "20/05/2026",
    autor: "Dep. Carlos Mendes (PDT-MG)",
    atraso: 0,
    coberturaDados: 76,
    confiabilidade: "media",
    statusTramitacao: "em-tramitacao",
    transitouEntreCasas: false,
  },
  {
    id: "4",
    numero: "892/2023",
    tipo: "PEC",
    ementa:
      "Propõe alteração na Constituição Federal para incluir o acesso à internet como direito fundamental.",
    casaAtual: "Senado",
    faseAtual: "Comissão Especial",
    diasNaEtapa: 156,
    ultimoEventoRelevante: "Substitutivo apresentado pela relatoria",
    dataUltimoEvento: "10/01/2026",
    autor: "Sen. Ana Paula (PP-RS)",
    atraso: 67,
    coberturaDados: 91,
    confiabilidade: "alta",
    statusTramitacao: "em-atraso",
    transitouEntreCasas: true,
  },
  {
    id: "5",
    numero: "4156/2025",
    tipo: "PL",
    ementa:
      "Institui o Programa Nacional de Modernização da Gestão Pública e estabelece diretrizes para transformação digital.",
    casaAtual: "Câmara",
    faseAtual: "Recebimento e Despacho",
    diasNaEtapa: 12,
    ultimoEventoRelevante: "Proposição protocolada e numerada",
    dataUltimoEvento: "23/05/2026",
    autor: "Dep. Roberto Alves (MDB-BA)",
    atraso: -3,
    coberturaDados: 68,
    confiabilidade: "media",
    statusTramitacao: "em-tramitacao",
    transitouEntreCasas: false,
  },
  {
    id: "6",
    numero: "2198/2024",
    tipo: "PL",
    ementa:
      "Dispõe sobre a criação de incentivos fiscais para empresas que investirem em energias renováveis e sustentabilidade ambiental.",
    casaAtual: "Senado",
    faseAtual: "Revisão - Comissões",
    diasNaEtapa: 67,
    ultimoEventoRelevante: "Emenda aprovada na comissão",
    dataUltimoEvento: "28/03/2026",
    autor: "Dep. Fernanda Costa (PSOL-SP)",
    atraso: 18,
    coberturaDados: 55,
    confiabilidade: "baixa",
    statusTramitacao: "em-atraso",
    transitouEntreCasas: true,
  },
  {
    id: "7",
    numero: "5234/2025",
    tipo: "PL",
    ementa:
      "Altera dispositivos da Lei de Diretrizes e Bases da Educação para incluir educação digital no currículo básico nacional.",
    casaAtual: "Câmara",
    faseAtual: "Recebimento e Despacho",
    diasNaEtapa: 8,
    ultimoEventoRelevante: "Aguardando despacho inicial",
    dataUltimoEvento: "27/05/2026",
    autor: "Sen. Luiza Oliveira (PT-PE)",
    atraso: 0,
    coberturaDados: 82,
    confiabilidade: "alta",
    statusTramitacao: "aguardando",
    transitouEntreCasas: false,
  },
  {
    id: "8",
    numero: "1567/2023",
    tipo: "PL",
    ementa:
      "Regulamenta o trabalho remoto no setor público federal e estabelece critérios de elegibilidade e controle de produtividade.",
    casaAtual: "Sanção",
    faseAtual: "Sancionada",
    diasNaEtapa: 3,
    ultimoEventoRelevante: "Publicada no Diário Oficial da União",
    dataUltimoEvento: "24/05/2026",
    autor: "Dep. Paulo Ribeiro (PL-GO)",
    atraso: 0,
    coberturaDados: 98,
    confiabilidade: "alta",
    statusTramitacao: "aprovada",
    transitouEntreCasas: true,
  },
  {
    id: "9",
    numero: "3892/2024",
    tipo: "PL",
    ementa:
      "Institui política nacional de segurança cibernética e estabelece diretrizes para proteção de infraestruturas críticas.",
    casaAtual: "Câmara",
    faseAtual: "Comissão Temática - Análise",
    diasNaEtapa: 34,
    ultimoEventoRelevante: "Solicitação de prazo para análise técnica",
    dataUltimoEvento: "08/04/2026",
    autor: "Dep. Marcos Ferreira (PSDB-SC)",
    atraso: 5,
    coberturaDados: 79,
    confiabilidade: "media",
    statusTramitacao: "em-tramitacao",
    transitouEntreCasas: false,
  },
  {
    id: "10",
    numero: "4521/2023",
    tipo: "PL",
    ementa:
      "Dispõe sobre transparência na utilização de recursos públicos em contratos de publicidade e comunicação governamental.",
    casaAtual: "Senado",
    faseAtual: "Revisão - Redação Final",
    diasNaEtapa: 18,
    ultimoEventoRelevante: "Aprovado em revisão com emendas",
    dataUltimoEvento: "17/05/2026",
    autor: "Sen. Patricia Lima (REDE-CE)",
    atraso: 0,
    coberturaDados: 93,
    confiabilidade: "alta",
    statusTramitacao: "em-tramitacao",
    transitouEntreCasas: true,
  },
];

// 8 Canonical Brazilian Legislative Phases
const pipelineData = [
  { name: "Recebimento e Despacho", count: 142, percentage: 100, medianDays: 8 },
  { name: "Comissão Temática - Análise", count: 98, percentage: 69, medianDays: 45 },
  { name: "Comissão de Constituição e Justiça", count: 76, percentage: 53.5, medianDays: 62 },
  { name: "Plenário - Discussão e Votação", count: 45, percentage: 31.7, medianDays: 38 },
  { name: "Revisão na Casa Revisora", count: 32, percentage: 22.5, medianDays: 71 },
  { name: "Revisão - Comissões", count: 21, percentage: 14.8, medianDays: 54 },
  { name: "Revisão - Redação Final", count: 12, percentage: 8.5, medianDays: 15 },
  { name: "Sanção e Publicação", count: 8, percentage: 5.6, medianDays: 12 },
];

const timeSeriesData = [
  { mes: "Nov/25", entradas: 24, saidas: 18 },
  { mes: "Dez/25", entradas: 31, saidas: 22 },
  { mes: "Jan/26", entradas: 28, saidas: 25 },
  { mes: "Fev/26", entradas: 35, saidas: 29 },
  { mes: "Mar/26", entradas: 42, saidas: 31 },
  { mes: "Abr/26", entradas: 38, saidas: 34 },
  { mes: "Mai/26", entradas: 45, saidas: 28 },
];

const bottleneckData = {
  porOrgao: [
    { nome: "Comissão de Constituição e Justiça - Câmara", proposicoes: 34, tempoMediano: 87, rank: 1 },
    { nome: "Comissão de Finanças e Tributação - Senado", proposicoes: 28, tempoMediano: 79, rank: 2 },
    { nome: "Comissão de Assuntos Econômicos - Senado", proposicoes: 22, tempoMediano: 71, rank: 3 },
    { nome: "Comissão de Educação - Câmara", proposicoes: 18, tempoMediano: 58, rank: 4 },
    { nome: "Mesa Diretora - Câmara", proposicoes: 31, tempoMediano: 45, rank: 5 },
  ],
  porFase: [
    { nome: "Revisão na Casa Revisora", proposicoes: 32, tempoMediano: 71, rank: 1 },
    { nome: "Comissão de Constituição e Justiça", proposicoes: 76, tempoMediano: 62, rank: 2 },
    { nome: "Revisão - Comissões", proposicoes: 21, tempoMediano: 54, rank: 3 },
    { nome: "Comissão Temática - Análise", proposicoes: 98, tempoMediano: 45, rank: 4 },
    { nome: "Plenário - Discussão e Votação", proposicoes: 45, tempoMediano: 38, rank: 5 },
  ],
  porTema: [
    { nome: "Reforma Tributária", proposicoes: 12, tempoMediano: 95, rank: 1 },
    { nome: "Direitos Digitais e Proteção de Dados", proposicoes: 18, tempoMediano: 73, rank: 2 },
    { nome: "Infraestrutura e Concessões", proposicoes: 15, tempoMediano: 68, rank: 3 },
    { nome: "Educação e Cultura", proposicoes: 24, tempoMediano: 52, rank: 4 },
    { nome: "Meio Ambiente e Sustentabilidade", proposicoes: 21, tempoMediano: 47, rank: 5 },
  ],
};

const houseTransitionData = {
  transitions: [
    { origem: "Câmara" as const, destino: "Senado" as const, quantidade: 18, tempoMedioTransicao: 7 },
    { origem: "Senado" as const, destino: "Câmara" as const, quantidade: 12, tempoMedioTransicao: 9 },
  ],
  totalCamara: 847,
  totalSenado: 576,
};

export default function App() {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterOpen, setFilterOpen] = useState(false);
  const [showDetail, setShowDetail] = useState(false);

  if (showDetail) {
    return <PropositionDetail onBack={() => setShowDetail(false)} />;
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-card border-b border-border sticky top-0 z-10 shadow-sm">
        <div className="max-w-[1600px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
                <FileText className="w-6 h-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-foreground">
                  Sistema de Monitoramento Legislativo Federal
                </h1>
                <p className="text-sm text-muted-foreground">
                  Análise de tramitação e gargalos processuais - Congresso Nacional
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button className="flex items-center gap-2 px-4 py-2 bg-secondary text-secondary-foreground rounded-lg hover:bg-secondary/80 transition-colors">
                <Calendar className="w-4 h-4" />
                <span className="text-sm">Maio 2026</span>
              </button>
              <button className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors">
                <Download className="w-4 h-4" />
                <span className="text-sm">Exportar Relatório</span>
              </button>
            </div>
          </div>

          {/* Search and Filters */}
          <div className="flex items-center gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Buscar por número, ementa, autor, órgão ou palavra-chave..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 bg-input-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>
            <button
              onClick={() => setFilterOpen(!filterOpen)}
              className="flex items-center gap-2 px-4 py-2.5 bg-secondary text-secondary-foreground rounded-lg hover:bg-secondary/80 transition-colors"
            >
              <Filter className="w-4 h-4" />
              <span className="text-sm">Filtros Avançados</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-[1600px] mx-auto px-6 py-6 space-y-6">
        {/* KPIs */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard
            title="Total de Proposições"
            value="2.847"
            subtitle="Últimos 12 meses"
            icon={FileText}
            trend={{ value: "+12%", isPositive: true }}
          />
          <KPICard
            title="Em Tramitação Ativa"
            value="1.423"
            subtitle="Câmara e Senado"
            icon={Activity}
            trend={{ value: "+8%", isPositive: true }}
          />
          <KPICard
            title="Com Atraso Crítico"
            value="234"
            subtitle=">15 dias acima da mediana"
            icon={Clock}
            trend={{ value: "-5%", isPositive: true }}
          />
          <KPICard
            title="Tempo Mediano Global"
            value="54 dias"
            subtitle="Por fase de tramitação"
            icon={TrendingUp}
          />
        </div>

        {/* Pipeline */}
        <div className="bg-card border border-border rounded-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-semibold text-foreground">
                Pipeline de Tramitação Legislativa
              </h2>
              <p className="text-sm text-muted-foreground mt-0.5">
                Distribuição por fase processual canônica com tempo mediano por etapa
              </p>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-primary" />
                <span className="text-xs text-muted-foreground">
                  Taxa de conclusão: 5.6% • Mediana global: 54 dias
                </span>
              </div>
            </div>
          </div>
          <div className="flex items-end gap-2 overflow-x-auto pb-2">
            {pipelineData.map((stage, idx) => (
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

        {/* House Transitions */}
        <HouseTransitions {...houseTransitionData} />

        {/* Charts and Bottlenecks */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Time Series Chart */}
          <div className="lg:col-span-2 bg-card border border-border rounded-lg p-6">
            <div className="mb-6">
              <h2 className="text-lg font-semibold text-foreground">
                Evolução Temporal de Proposições
              </h2>
              <p className="text-sm text-muted-foreground mt-0.5">
                Entradas e saídas mensais do sistema de tramitação
              </p>
            </div>
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={timeSeriesData}>
                <CartesianGrid key="grid" strokeDasharray="3 3" stroke="#e8ecef" />
                <XAxis
                  key="xaxis"
                  dataKey="mes"
                  tick={{ fontSize: 12, fill: "#5a6c7d" }}
                  stroke="#d4dce4"
                />
                <YAxis key="yaxis" tick={{ fontSize: 12, fill: "#5a6c7d" }} stroke="#d4dce4" />
                <Tooltip
                  key="tooltip"
                  contentStyle={{
                    backgroundColor: "#ffffff",
                    border: "1px solid #d4dce4",
                    borderRadius: "8px",
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
                  stroke="#115e67"
                  strokeWidth={2}
                  dot={{ fill: "#115e67", r: 4 }}
                  name="Entradas"
                />
                <Line
                  key="line-saidas"
                  type="monotone"
                  dataKey="saidas"
                  stroke="#2d8a96"
                  strokeWidth={2}
                  dot={{ fill: "#2d8a96", r: 4 }}
                  name="Saídas"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Data Quality Indicator */}
          <div className="bg-card border border-border rounded-lg p-6">
            <div className="mb-4">
              <h2 className="text-lg font-semibold text-foreground">
                Cobertura de Dados
              </h2>
              <p className="text-sm text-muted-foreground mt-0.5">
                Qualidade e completude das informações
              </p>
            </div>
            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-muted-foreground">
                    Eventos documentados
                  </span>
                  <span className="text-sm font-semibold text-foreground">94.2%</span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-emerald-500 rounded-full transition-all"
                    style={{ width: "94.2%" }}
                  />
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-muted-foreground">
                    Metadados completos
                  </span>
                  <span className="text-sm font-semibold text-foreground">87.8%</span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-emerald-500 rounded-full transition-all"
                    style={{ width: "87.8%" }}
                  />
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-muted-foreground">
                    Histórico de tramitação
                  </span>
                  <span className="text-sm font-semibold text-foreground">91.5%</span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-emerald-500 rounded-full transition-all"
                    style={{ width: "91.5%" }}
                  />
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-muted-foreground">
                    Documentos anexos
                  </span>
                  <span className="text-sm font-semibold text-foreground">73.4%</span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-amber-500 rounded-full transition-all"
                    style={{ width: "73.4%" }}
                  />
                </div>
              </div>
            </div>
            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-xs text-blue-800">
                Cobertura consolidada de <span className="font-semibold">86.7%</span> das proposições com dados completos para análise preditiva.
              </p>
            </div>
          </div>
        </div>

        {/* Bottleneck Analytics */}
        <BottleneckAnalytics {...bottleneckData} />

        {/* Propositions Table */}
        <div>
          <div className="mb-4">
            <h2 className="text-lg font-semibold text-foreground">
              Proposições em Análise Detalhada
            </h2>
            <p className="text-sm text-muted-foreground mt-0.5">
              Acompanhamento individualizado com indicadores de atraso, cobertura e status de tramitação
            </p>
          </div>
          <PropositionsTable
            propositions={mockPropositions}
            onPropositionClick={() => setShowDetail(true)}
          />
        </div>
      </main>
    </div>
  );
}
