import { useState } from "react";
import {
  ArrowLeft,
  FileText,
  Calendar,
  Clock,
  Building2,
  TrendingUp,
  RotateCcw,
  ArrowRightLeft,
  ExternalLink,
  Download,
  Share2,
} from "lucide-react";
import { MetricCard } from "./components/MetricCard";
import { PhaseTimeline, PhaseEntry } from "./components/PhaseTimeline";
import { EventTimeline, TimelineEvent } from "./components/EventTimeline";
import { HouseTransitDiagram, TransitStep } from "./components/HouseTransitDiagram";
import { DataReliability } from "./components/DataReliability";
import { InfoTooltip } from "./components/InfoTooltip";

// Mock data for demonstration
const mockProposition = {
  numero: "2547/2023",
  tipo: "PL",
  ementa:
    "Dispõe sobre a proteção de dados pessoais no âmbito da administração pública federal e estabelece diretrizes para o tratamento de informações sensíveis, cria mecanismos de fiscalização e penalidades, e altera a Lei nº 13.709/2018 (Lei Geral de Proteção de Dados).",
  tema: "Direitos Digitais e Proteção de Dados",
  casaAtual: "Câmara dos Deputados",
  faseAtual: "Comissão de Constituição e Justiça",
  autor: "Dep. Maria Silva (PT-SP)",
  dataApresentacao: "12/03/2023",
  statusAtraso: "em-atraso",
  diasAtraso: 12,
  coberturaDados: 94,
};

const mockMetrics = {
  diasTotais: 789,
  diasEtapaAtual: 45,
  fasesPercorridas: 5,
  eventosRelevantes: 23,
  recorrenciasFase: 2,
  transicoesEntreCasas: 1,
};

const mockPhases: PhaseEntry[] = [
  {
    id: "1",
    fase: "Recebimento e Despacho Inicial",
    ocorrencia: 1,
    dataEntrada: "12/03/2023",
    dataSaida: "18/03/2023",
    duracaoDias: 6,
    isRecorrente: false,
    isCurrent: false,
  },
  {
    id: "2",
    fase: "Comissão de Ciência e Tecnologia",
    ocorrencia: 1,
    dataEntrada: "18/03/2023",
    dataSaida: "15/05/2023",
    duracaoDias: 58,
    atrasoDias: 13,
    isRecorrente: false,
    isCurrent: false,
  },
  {
    id: "3",
    fase: "Comissão de Trabalho e Administração Pública",
    ocorrencia: 1,
    dataEntrada: "15/05/2023",
    dataSaida: "28/08/2023",
    duracaoDias: 105,
    atrasoDias: 42,
    isRecorrente: false,
    isCurrent: false,
  },
  {
    id: "4",
    fase: "Revisão - Retorno para Comissão de Ciência e Tecnologia",
    ocorrencia: 2,
    dataEntrada: "28/08/2023",
    dataSaida: "15/11/2023",
    duracaoDias: 79,
    atrasoDias: 24,
    isRecorrente: true,
    isCurrent: false,
  },
  {
    id: "5",
    fase: "Plenário - Primeira Discussão",
    ocorrencia: 1,
    dataEntrada: "15/11/2023",
    dataSaida: "08/02/2024",
    duracaoDias: 85,
    atrasoDias: 31,
    isRecorrente: false,
    isCurrent: false,
  },
  {
    id: "6",
    fase: "Comissão de Constituição e Justiça",
    ocorrencia: 1,
    dataEntrada: "08/02/2024",
    dataSaida: undefined,
    duracaoDias: 45,
    atrasoDias: 12,
    isRecorrente: false,
    isCurrent: true,
  },
];

const mockEvents: TimelineEvent[] = [
  {
    id: "1",
    data: "12/03/2023",
    hora: "10:15",
    orgao: "Mesa Diretora - Câmara",
    tipoEvento: "despacho",
    titulo: "Protocolo e Numeração",
    descricao: "Proposição protocolada e numerada como PL 2547/2023",
    isRelevante: true,
    flags: { mudancaFase: true },
  },
  {
    id: "2",
    data: "18/03/2023",
    hora: "14:30",
    orgao: "Mesa Diretora - Câmara",
    tipoEvento: "despacho",
    titulo: "Distribuição para Comissão",
    descricao: "Distribuída para Comissão de Ciência e Tecnologia",
    isRelevante: true,
    flags: { mudancaFase: true },
  },
  {
    id: "3",
    data: "25/03/2023",
    hora: "09:00",
    orgao: "Comissão de Ciência e Tecnologia",
    tipoEvento: "despacho",
    titulo: "Designação de Relator",
    descricao: "Designado relator: Dep. Carlos Mendes (PDT-MG)",
    isRelevante: true,
  },
  {
    id: "4",
    data: "12/04/2023",
    hora: "15:00",
    orgao: "Comissão de Ciência e Tecnologia",
    tipoEvento: "outro",
    titulo: "Audiência Pública",
    descricao: "Realizada audiência pública com especialistas em proteção de dados e representantes da sociedade civil",
    isRelevante: true,
  },
  {
    id: "5",
    data: "28/04/2023",
    hora: "11:45",
    orgao: "Comissão de Ciência e Tecnologia",
    tipoEvento: "parecer",
    titulo: "Parecer do Relator",
    descricao: "Parecer do relator favorável com substitutivo propondo alterações técnicas e ajustes de redação",
    isRelevante: true,
  },
  {
    id: "6",
    data: "15/05/2023",
    hora: "16:20",
    orgao: "Comissão de Ciência e Tecnologia",
    tipoEvento: "deliberacao",
    titulo: "Aprovação por Unanimidade",
    descricao: "Parecer aprovado por unanimidade com elogios à abrangência da proposta",
    isRelevante: true,
    flags: { mudancaFase: true },
  },
  {
    id: "7",
    data: "15/05/2023",
    hora: "16:45",
    orgao: "Mesa Diretora - Câmara",
    tipoEvento: "despacho",
    titulo: "Redistribuição",
    descricao: "Distribuída para Comissão de Trabalho e Administração Pública",
    isRelevante: true,
    flags: { mudancaFase: true },
  },
  {
    id: "8",
    data: "22/05/2023",
    hora: "10:00",
    orgao: "Comissão de Trabalho e Administração Pública",
    tipoEvento: "despacho",
    titulo: "Designação de Relatora",
    descricao: "Designada relatora: Dep. Ana Paula Lima (REDE-CE)",
    isRelevante: true,
  },
  {
    id: "9",
    data: "18/06/2023",
    hora: "14:15",
    orgao: "Comissão de Trabalho e Administração Pública",
    tipoEvento: "emenda",
    titulo: "Apresentação de Emendas",
    descricao: "Apresentadas 7 emendas ao substitutivo versando sobre aplicação no setor público",
    isRelevante: true,
  },
  {
    id: "10",
    data: "12/07/2023",
    hora: "09:30",
    orgao: "Comissão de Trabalho e Administração Pública",
    tipoEvento: "outro",
    titulo: "Solicitação de Prazo Adicional",
    descricao: "Solicitado prazo adicional para análise de emendas devido à complexidade técnica (atraso detectado)",
    isRelevante: true,
    flags: { atraso: true },
  },
  {
    id: "11",
    data: "05/08/2023",
    hora: "11:00",
    orgao: "Comissão de Trabalho e Administração Pública",
    tipoEvento: "parecer",
    titulo: "Parecer da Relatora",
    descricao: "Parecer da relatora favorável com incorporação parcial de emendas e sugestões de aprimoramento",
    isRelevante: true,
  },
  {
    id: "12",
    data: "28/08/2023",
    hora: "15:40",
    orgao: "Comissão de Trabalho e Administração Pública",
    tipoEvento: "deliberacao",
    titulo: "Aprovação com Ressalvas",
    descricao: "Parecer aprovado com ressalvas, retorno à comissão de origem solicitado para verificação de compatibilidade",
    isRelevante: true,
    flags: { mudancaFase: true },
  },
  {
    id: "13",
    data: "28/08/2023",
    hora: "16:00",
    orgao: "Mesa Diretora - Câmara",
    tipoEvento: "despacho",
    titulo: "Retorno para Comissão de Origem",
    descricao: "Retorno para Comissão de Ciência e Tecnologia para análise de compatibilidade entre emendas",
    isRelevante: true,
    flags: { mudancaFase: true },
  },
  {
    id: "14",
    data: "05/09/2023",
    hora: "10:30",
    orgao: "Comissão de Ciência e Tecnologia",
    tipoEvento: "despacho",
    titulo: "Redesignação de Relator",
    descricao: "Redesignado relator: Dep. Roberto Alves (MDB-BA)",
    isRelevante: true,
  },
  {
    id: "15",
    data: "28/10/2023",
    hora: "14:00",
    orgao: "Comissão de Ciência e Tecnologia",
    tipoEvento: "parecer",
    titulo: "Parecer Complementar",
    descricao: "Parecer complementar aprovando compatibilidade das emendas com o texto original",
    isRelevante: true,
  },
  {
    id: "16",
    data: "15/11/2023",
    hora: "16:30",
    orgao: "Mesa Diretora - Câmara",
    tipoEvento: "despacho",
    titulo: "Encaminhamento para Plenário",
    descricao: "Encaminhada para discussão em plenário após conclusão das comissões",
    isRelevante: true,
    flags: { mudancaFase: true },
  },
  {
    id: "17",
    data: "22/11/2023",
    hora: "10:00",
    orgao: "Plenário - Câmara",
    tipoEvento: "outro",
    titulo: "Primeira Discussão",
    descricao: "Primeira discussão em plenário - apresentação do relatório consolidado e abertura de debates",
    isRelevante: true,
  },
  {
    id: "18",
    data: "06/12/2023",
    hora: "15:20",
    orgao: "Plenário - Câmara",
    tipoEvento: "emenda",
    titulo: "Apresentação de Destaques",
    descricao: "Apresentados 12 destaques para votação em separado de dispositivos específicos",
    isRelevante: true,
  },
  {
    id: "19",
    data: "20/12/2023",
    hora: "14:45",
    orgao: "Plenário - Câmara",
    tipoEvento: "deliberacao",
    titulo: "Votação de Destaques",
    descricao: "Aprovados 8 dos 12 destaques apresentados após intenso debate",
    isRelevante: true,
  },
  {
    id: "20",
    data: "08/02/2024",
    hora: "17:30",
    orgao: "Plenário - Câmara",
    tipoEvento: "deliberacao",
    titulo: "Aprovação em Plenário",
    descricao: "Aprovado texto final em plenário com modificações, encaminhado para análise de constitucionalidade",
    isRelevante: true,
    flags: { mudancaFase: true },
  },
  {
    id: "21",
    data: "08/02/2024",
    hora: "18:00",
    orgao: "Mesa Diretora - Câmara",
    tipoEvento: "despacho",
    titulo: "Distribuição para CCJ",
    descricao: "Distribuída para Comissão de Constituição e Justiça (análise de constitucionalidade)",
    isRelevante: true,
    flags: { mudancaFase: true },
  },
  {
    id: "22",
    data: "15/02/2024",
    hora: "09:00",
    orgao: "Comissão de Constituição e Justiça",
    tipoEvento: "despacho",
    titulo: "Designação de Relator CCJ",
    descricao: "Designado relator: Dep. Paulo Ribeiro (PL-GO)",
    isRelevante: true,
  },
  {
    id: "23",
    data: "15/04/2024",
    hora: "11:30",
    orgao: "Comissão de Constituição e Justiça",
    tipoEvento: "parecer",
    titulo: "Parecer pela Constitucionalidade",
    descricao: "Parecer do relator pela constitucionalidade, juridicidade e técnica legislativa apresentado",
    isRelevante: true,
  },
];

const mockTransitSteps: TransitStep[] = [
  {
    casa: "Câmara",
    tipo: "origem",
    dataEntrada: "12/03/2023",
    duracaoDias: 789,
  },
];

const mockReliability = {
  cobertura: 94,
  statusHistorico: "completo" as const,
  ultimaAtualizacao: "27/05/2026 às 14:23",
  fontes: [
    "Sistema de Tramitação da Câmara dos Deputados (API oficial)",
    "Portal da Legislação Federal",
    "Diário Oficial da União - Seção 1",
  ],
  limitacoes: [
    "Eventos anteriores a 01/01/2020 podem ter registro parcial devido à migração de sistemas",
    "Despachos internos de comissões podem ter atraso de até 48h para publicação",
    "Documentos anexos estão sujeitos à disponibilidade das fontes oficiais",
  ],
};

interface PropositionDetailProps {
  onBack?: () => void;
}

export default function PropositionDetail({ onBack }: PropositionDetailProps) {
  const [selectedPhaseId, setSelectedPhaseId] = useState<string | null>(null);

  const getAtrasoColor = () => {
    if (mockProposition.diasAtraso > 15) return "bg-red-100 text-red-800 border-red-200";
    if (mockProposition.diasAtraso > 0) return "bg-amber-100 text-amber-800 border-amber-200";
    return "bg-green-100 text-green-800 border-green-200";
  };

  const getCoberturaColor = () => {
    if (mockProposition.coberturaDados >= 90) return "bg-emerald-100 text-emerald-800 border-emerald-200";
    if (mockProposition.coberturaDados >= 70) return "bg-amber-100 text-amber-800 border-amber-200";
    return "bg-red-100 text-red-800 border-red-200";
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-card border-b border-border sticky top-0 z-10 shadow-sm">
        <div className="max-w-[1400px] mx-auto px-4 md:px-6 py-3 md:py-4">
          {/* Breadcrumb */}
          <div className="flex items-center gap-2 mb-3 text-xs text-muted-foreground">
            <button onClick={onBack} className="hover:text-primary transition-colors">
              Dashboard
            </button>
            <span>/</span>
            <button onClick={onBack} className="hover:text-primary transition-colors">
              Proposições
            </button>
            <span>/</span>
            <span className="text-foreground font-medium">
              {mockProposition.tipo} {mockProposition.numero}
            </span>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between">
            <button
              onClick={onBack}
              className="flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors"
            >
              <ArrowLeft className="w-4 md:w-5 h-4 md:h-5" />
              <span className="text-xs md:text-sm font-medium">Voltar para lista</span>
            </button>

            <div className="flex items-center gap-2 md:gap-3">
              <button className="hidden sm:flex items-center gap-2 px-3 md:px-4 py-1.5 md:py-2 bg-secondary text-secondary-foreground rounded-lg hover:bg-secondary/80 transition-colors">
                <Share2 className="w-4 h-4" />
                <span className="text-xs md:text-sm">Compartilhar</span>
              </button>
              <button className="flex items-center gap-2 px-3 md:px-4 py-1.5 md:py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors">
                <Download className="w-4 h-4" />
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
                      {mockProposition.tipo} {mockProposition.numero}
                    </h1>
                    <span className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 border border-blue-200 rounded-lg text-xs sm:text-sm font-medium w-fit">
                      {mockProposition.tema}
                    </span>
                  </div>
                  <p className="text-xs sm:text-sm text-muted-foreground mb-1">
                    Autoria: {mockProposition.autor} • Apresentação: {mockProposition.dataApresentacao}
                  </p>
                </div>

                <div className="flex flex-row md:flex-col gap-2 items-start md:items-end">
                  <span className={`inline-flex items-center px-3 py-1.5 border rounded-lg text-xs sm:text-sm font-medium ${getAtrasoColor()}`}>
                    {mockProposition.diasAtraso > 0 ? `+${mockProposition.diasAtraso}d atraso` : "No prazo"}
                  </span>
                  <span className={`inline-flex items-center px-3 py-1.5 border rounded-lg text-xs sm:text-sm font-medium ${getCoberturaColor()}`}>
                    {mockProposition.coberturaDados}% cobertura
                  </span>
                </div>
              </div>

              <p className="text-sm md:text-base text-foreground leading-relaxed mb-4">
                {mockProposition.ementa}
              </p>

              <div className="pt-4 border-t border-border space-y-4">
                {/* Progress Bar */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-medium text-muted-foreground">
                      Progresso no Pipeline Legislativo
                    </span>
                    <span className="text-xs font-semibold text-primary">
                      {mockMetrics.fasesPercorridas} de 8 fases
                    </span>
                  </div>
                  <div className="h-2 bg-secondary rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary rounded-full transition-all"
                      style={{ width: `${(mockMetrics.fasesPercorridas / 8) * 100}%` }}
                    />
                  </div>
                </div>

                {/* Current Status */}
                <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-6">
                  <div className="flex items-center gap-2">
                    <Building2 className="w-4 h-4 text-muted-foreground" />
                    <span className="text-xs sm:text-sm text-muted-foreground">
                      Casa Atual: <span className="font-medium text-foreground">{mockProposition.casaAtual}</span>
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-muted-foreground" />
                    <span className="text-xs sm:text-sm text-muted-foreground">
                      Fase Atual: <span className="font-medium text-foreground">{mockProposition.faseAtual}</span>
                    </span>
                  </div>
                  <button className="flex items-center gap-2 text-xs sm:text-sm text-primary hover:text-primary/80 transition-colors sm:ml-auto">
                    <ExternalLink className="w-4 h-4" />
                    Ver no portal oficial
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Metrics Cards */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <MetricCard
            label="Dias Totais Acumulados"
            value={mockMetrics.diasTotais}
            icon={Calendar}
            subtitle="Desde 12/03/2023"
            tooltip="Tempo total desde a apresentação da proposição até o momento atual. Este contador inclui todos os dias corridos, independente de recesso parlamentar."
          />
          <MetricCard
            label="Dias na Etapa Atual"
            value={mockMetrics.diasEtapaAtual}
            icon={Clock}
            highlight
            subtitle="CCJ - Em análise"
            tooltip="Tempo acumulado na fase atual (Comissão de Constituição e Justiça). Valor comparado com a mediana histórica para detectar atrasos."
          />
          <MetricCard
            label="Fases Percorridas"
            value={`${mockMetrics.fasesPercorridas}/8`}
            icon={TrendingUp}
            subtitle="Fases canônicas"
            tooltip="Número de fases legislativas já concluídas das 8 fases canônicas do processo: Recebimento, Comissões Temáticas, CCJ, Plenário, Revisão, Redação Final, Sanção e Publicação."
          />
          <MetricCard
            label="Eventos Relevantes"
            value={mockMetrics.eventosRelevantes}
            icon={FileText}
            subtitle="Documentados"
            tooltip="Eventos que impactaram significativamente a tramitação: mudanças de fase, deliberações, pareceres, emendas e despachos estruturantes. Eventos administrativos não são contabilizados."
          />
          <MetricCard
            label="Recorrências de Fase"
            value={mockMetrics.recorrenciasFase}
            icon={RotateCcw}
            subtitle="Retornos detectados"
            tooltip="Número de vezes que a proposição retornou a fases já visitadas anteriormente. Recorrências indicam necessidade de ajustes, compatibilização ou análises complementares."
          />
          <MetricCard
            label="Transições entre Casas"
            value={mockMetrics.transicoesEntreCasas}
            icon={ArrowRightLeft}
            subtitle="Câmara ↔ Senado"
            tooltip="Número de vezes que a proposição transitou entre Câmara dos Deputados e Senado Federal. Para projetos que ainda não foram ao Senado, este valor é zero."
          />
        </div>

        {/* Phase Timeline */}
        <PhaseTimeline phases={mockPhases} onPhaseClick={setSelectedPhaseId} />

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* House Transit */}
          <HouseTransitDiagram steps={mockTransitSteps} historicoUnificado={true} />

          {/* Data Reliability */}
          <DataReliability {...mockReliability} />
        </div>

        {/* Event Timeline - Collapsible */}
        <EventTimeline events={mockEvents} filterByPhaseId={selectedPhaseId} />

        {/* Methodological Notes */}
        <div className="bg-gradient-to-br from-blue-50 to-blue-50/30 border border-blue-200 rounded-lg p-6">
          <div className="flex items-start gap-4">
            <div className="flex items-center justify-center w-11 h-11 bg-blue-600 rounded-xl flex-shrink-0 shadow-sm">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-base font-semibold text-blue-900 mb-3 flex items-center gap-2">
                Sobre a Metodologia Analítica
                <span className="text-xs font-normal text-blue-600 bg-blue-100 px-2 py-0.5 rounded">
                  Narrativa Temporal Unificada
                </span>
              </h3>
              <div className="grid md:grid-cols-2 gap-3 text-sm text-blue-800">
                <div className="flex items-start gap-2.5">
                  <div className="w-1.5 h-1.5 rounded-full bg-blue-600 mt-1.5 flex-shrink-0" />
                  <p className="leading-relaxed">
                    <strong>Fases canônicas</strong> agregam períodos de tramitação;{" "}
                    <strong>eventos relevantes</strong> documentam deliberações e transições estruturantes.
                  </p>
                </div>
                <div className="flex items-start gap-2.5">
                  <div className="w-1.5 h-1.5 rounded-full bg-blue-600 mt-1.5 flex-shrink-0" />
                  <p className="leading-relaxed">
                    <strong>Indicadores de atraso</strong> comparam o tempo atual com a mediana histórica.
                    Valores acima de 15 dias são críticos.
                  </p>
                </div>
                <div className="flex items-start gap-2.5">
                  <div className="w-1.5 h-1.5 rounded-full bg-blue-600 mt-1.5 flex-shrink-0" />
                  <p className="leading-relaxed">
                    <strong>Dados normalizados</strong> de múltiplas fontes oficiais (APIs do Congresso, DOU).
                  </p>
                </div>
                <div className="flex items-start gap-2.5">
                  <div className="w-1.5 h-1.5 rounded-full bg-blue-600 mt-1.5 flex-shrink-0" />
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
