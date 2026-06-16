import { useState, useMemo, useEffect } from "react";
import {
  FileText,
  ArrowRightLeft,
  CheckCircle2,
  AlertTriangle,
  Link2,
  ChevronDown,
  ChevronUp,
  Calendar,
  Building2,
  Search,
} from "lucide-react";

export interface TimelineEvent {
  id: string;
  data: string;
  hora?: string;
  orgao: string;
  tipoEvento:
    | "mudanca-fase"
    | "deliberacao"
    | "apensamento"
    | "transicao-casa"
    | "despacho"
    | "parecer"
    | "emenda"
    | "outro";
  titulo: string;
  descricao: string;
  isRelevante: boolean;
  flags?: {
    mudancaFase?: boolean;
    atraso?: boolean;
    transitoCasas?: boolean;
    apensamento?: boolean;
  };
}

interface EventTimelineProps {
  events: TimelineEvent[];
  filterByPhaseId?: string | null;
}

export function EventTimeline({ events }: EventTimelineProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [filter, setFilter] = useState<"resumo" | "todos">("resumo");
  const [searchQuery, setSearchQuery] = useState("");
  const [visibleCount, setVisibleCount] = useState(15);
  const [expandedEventIds, setExpandedEventIds] = useState<Record<string, boolean>>({});

  // Reseta a paginação e os sub-cards expandidos ao mudar o filtro ou o termo de busca
  useEffect(() => {
    setVisibleCount(15);
    setExpandedEventIds({});
  }, [filter, searchQuery]);

  const toggleEventExpansion = (eventId: string) => {
    setExpandedEventIds((prev) => ({
      ...prev,
      [eventId]: !prev[eventId],
    }));
  };

  const shouldTruncate = (text: string) => text && text.length > 280;
  const truncateText = (text: string) => text.slice(0, 260);

  const getEventIcon = (tipo: TimelineEvent["tipoEvento"]) => {
    switch (tipo) {
      case "mudanca-fase":
        return ArrowRightLeft;
      case "deliberacao":
        return CheckCircle2;
      case "apensamento":
        return Link2;
      case "transicao-casa":
        return ArrowRightLeft;
      case "parecer":
        return FileText;
      default:
        return FileText;
    }
  };

  const getEventColor = (tipo: TimelineEvent["tipoEvento"]) => {
    switch (tipo) {
      case "mudanca-fase":
        return "text-primary bg-primary/10 border-primary/20";
      case "deliberacao":
        return "text-emerald-600 bg-emerald-50 border-emerald-200";
      case "apensamento":
        return "text-amber-600 bg-amber-50 border-amber-200";
      case "transicao-casa":
        return "text-purple-600 bg-purple-50 border-purple-200";
      default:
        return "text-muted-foreground bg-muted border-border";
    }
  };

  const getResumoLeftBorder = (event: TimelineEvent) => {
    if (event.flags?.atraso) return "border-l-red-400";
    if (event.tipoEvento === "deliberacao") return "border-l-emerald-400";
    if (event.flags?.mudancaFase) return "border-l-primary";
    if (event.tipoEvento === "parecer") return "border-l-blue-400";
    if (event.flags?.transitoCasas || event.tipoEvento === "transicao-casa") return "border-l-purple-400";
    return "border-l-border";
  };

  // Contadores unificados em um único laço de repetição com useMemo
  const { resumoCount } = useMemo(() => {
    let resumo = 0;
    events.forEach((event) => {
      if (event.isRelevante && (
        event.flags?.mudancaFase ||
        event.flags?.transitoCasas ||
        event.flags?.atraso ||
        event.tipoEvento === "deliberacao" ||
        event.tipoEvento === "parecer"
      )) {
        resumo++;
      }
    });
    return { resumoCount: resumo };
  }, [events]);

  const todosCount = events.length;

  // Filtragem unificada e otimizada com busca textual e granularidade
  const filteredEvents = useMemo(() => {
    return events.filter((event) => {
      // Filtro de busca textual (case-insensitive)
      if (searchQuery.trim() !== "") {
        const query = searchQuery.toLowerCase();
        const matchTitle = event.titulo?.toLowerCase().includes(query);
        const matchDesc = event.descricao?.toLowerCase().includes(query);
        const matchOrgao = event.orgao?.toLowerCase().includes(query);
        if (!matchTitle && !matchDesc && !matchOrgao) {
          return false;
        }
      }

      // Filtro de granularidade
      if (filter === "resumo") {
        if (!event.isRelevante) return false;
        return (
          event.flags?.mudancaFase ||
          event.flags?.transitoCasas ||
          event.flags?.atraso ||
          event.tipoEvento === "deliberacao" ||
          event.tipoEvento === "parecer"
        );
      }
      return true;
    });
  }, [events, filter, searchQuery]);

  // Lista fatiada para a exibição (paginação)
  const displayedEvents = useMemo(() => {
    return filteredEvents.slice(0, visibleCount);
  }, [filteredEvents, visibleCount]);

  // Função utilitária segura para formatar links clicáveis na descrição original
  const renderDescriptionWithLinks = (text: string) => {
    if (!text) return null;
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    const parts = text.split(urlRegex);

    return parts.map((part, i) => {
      if (part.match(urlRegex)) {
        return (
          <a
            key={i}
            href={part}
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary hover:underline break-all font-medium transition-colors"
          >
            {part}
          </a>
        );
      }
      return part;
    });
  };

  return (
    <div className={`bg-card rounded-lg overflow-hidden transition-all ${
      isExpanded ? 'border-2 border-primary/30 shadow-lg' : 'border border-border'
    }`}>
      {/* Collapsible Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className={`w-full text-left p-6 transition-all group ${
          isExpanded ? 'bg-primary/5 border-b border-primary/20' : 'hover:bg-secondary/30'
        }`}
      >
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h2 className="text-lg font-semibold text-foreground group-hover:text-primary transition-colors">
                Timeline Detalhada de Eventos
              </h2>
              <span className="inline-flex items-center px-2.5 py-1 bg-primary/10 text-primary border border-primary/20 rounded-lg text-xs font-medium">
                {resumoCount} marcos • {todosCount} total
              </span>
            </div>
            <p className="text-sm text-muted-foreground">
              {isExpanded
                ? "Histórico completo com eventos canônicos, flags analíticos e descrições originais"
                : "Clique para expandir o histórico detalhado de tramitação com pareceres, deliberações e despachos"}
            </p>

            {/* Preview quando fechado */}
            {!isExpanded && (
              <div className="mt-4 flex items-center gap-4 text-xs text-muted-foreground">
                <div className="flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-full bg-blue-500" />
                  <span>{events.filter(e => e.flags?.mudancaFase).length} mudanças de fase</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-full bg-emerald-500" />
                  <span>{events.filter(e => e.tipoEvento === 'deliberacao').length} deliberações</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-full bg-purple-500" />
                  <span>{events.filter(e => e.flags?.transitoCasas).length} trânsitos</span>
                </div>
                {events.filter(e => e.flags?.atraso).length > 0 && (
                  <div className="flex items-center gap-1.5">
                    <div className="w-2 h-2 rounded-full bg-red-500" />
                    <span>{events.filter(e => e.flags?.atraso).length} atrasos detectados</span>
                  </div>
                )}
              </div>
            )}
          </div>
          <div className="flex items-center gap-3">
            <div className={`transition-transform ${isExpanded ? 'rotate-0' : ''}`}>
              {isExpanded ? (
                <ChevronUp className="w-6 h-6 text-primary flex-shrink-0" />
              ) : (
                <ChevronDown className="w-6 h-6 text-muted-foreground group-hover:text-primary transition-colors flex-shrink-0" />
              )}
            </div>
          </div>
        </div>
      </button>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="border-t border-border">
          {/* Filters and Search Bar */}
          <div className="px-6 py-4 bg-secondary/30 border-b border-border flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setFilter("resumo")}
                className={`px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
                  filter === "resumo"
                    ? "bg-primary text-primary-foreground"
                    : "bg-card text-foreground hover:bg-secondary border border-border"
                }`}
              >
                Resumo ({resumoCount})
              </button>
              <button
                onClick={() => setFilter("todos")}
                className={`px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
                  filter === "todos"
                    ? "bg-primary text-primary-foreground"
                    : "bg-card text-foreground hover:bg-secondary border border-border"
                }`}
              >
                Todos ({todosCount})
              </button>
            </div>

            {/* Input de Busca */}
            <div className="relative w-full sm:w-64">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground pointer-events-none" />
              <input
                type="text"
                placeholder="Buscar na timeline..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-8 py-1.5 text-sm bg-card border border-border rounded-lg placeholder-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all text-foreground"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery("")}
                  className="absolute right-3 top-2.5 text-xs text-muted-foreground hover:text-foreground font-medium transition-colors"
                >
                  Limpar
                </button>
              )}
            </div>
          </div>

          {/* Events List */}
          <div className="p-6">
            <div className="relative">
              {/* Timeline Line */}
              <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-border" />

              {/* Events */}
              <div className="space-y-5">
                {displayedEvents.map((event) => {
                  const Icon = getEventIcon(event.tipoEvento);
                  const colorClass = getEventColor(event.tipoEvento);

                  return (
                    <div key={event.id} className="relative pl-12">
                      {/* Timeline Dot with Icon */}
                      <div
                        className={`absolute left-0 top-0 w-8 h-8 rounded-lg border flex items-center justify-center ${colorClass} shadow-sm`}
                      >
                        <Icon className="w-4 h-4" />
                      </div>

                      {/* Event Content */}
                      <div className={`bg-card border border-border rounded-lg p-4 hover:shadow-md transition-shadow ${
                        filter === "resumo" ? `border-l-2 ${getResumoLeftBorder(event)}` : ""
                      }`}>
                        {/* Header */}
                        <div className="flex items-start justify-between gap-4 mb-3">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1.5">
                              <Calendar className="w-3.5 h-3.5 text-muted-foreground" />
                              <span className="text-xs font-medium text-muted-foreground">
                                {event.data}
                                {event.hora && ` às ${event.hora}`}
                              </span>
                            </div>
                            <h4 className="text-sm font-semibold text-foreground mb-1.5">
                              {event.titulo}
                            </h4>
                            <p className="text-xs text-muted-foreground flex items-center gap-1.5">
                              <Building2 className="w-3.5 h-3.5" />
                              {event.orgao}
                            </p>
                          </div>

                          {/* Flags */}
                          {event.flags && Object.values(event.flags).some(Boolean) && (
                            <div className="flex flex-wrap gap-1.5 items-start">
                              {event.flags.mudancaFase && (
                                <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-blue-100 text-blue-700 border border-blue-200 rounded text-xs font-medium whitespace-nowrap">
                                  <ArrowRightLeft className="w-3 h-3" />
                                  Mudança
                                </span>
                              )}
                              {event.flags.transitoCasas && (
                                <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-purple-100 text-purple-700 border border-purple-200 rounded text-xs font-medium whitespace-nowrap">
                                  <ArrowRightLeft className="w-3 h-3" />
                                  Trânsito
                                </span>
                              )}
                              {event.flags.atraso && (
                                <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-red-100 text-red-700 border border-red-200 rounded text-xs font-medium whitespace-nowrap">
                                  <AlertTriangle className="w-3 h-3" />
                                  Atraso
                                </span>
                              )}
                              {event.flags.apensamento && (
                                <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-amber-100 text-amber-700 border border-amber-200 rounded text-xs font-medium whitespace-nowrap">
                                  <Link2 className="w-3 h-3" />
                                  Apensado
                                </span>
                              )}
                            </div>
                          )}
                        </div>

                        {/* Definição de descrição extra não-redundante */}
                        {(() => {
                          const hasExtraDescription = event.descricao && event.descricao.trim() !== event.titulo.trim();

                          return (
                            <>
                              {/* Botão para ver descrição no modo Resumo (apenas se houver conteúdo extra) */}
                              {filter === "resumo" && hasExtraDescription && (
                                <div className="mt-3 flex items-center justify-end">
                                  <button
                                    onClick={() => toggleEventExpansion(event.id)}
                                    className="text-xs font-semibold text-primary hover:text-primary/80 transition-colors flex items-center gap-1.5 focus:outline-none"
                                  >
                                    {expandedEventIds[event.id] ? "Ocultar descrição" : "Ver descrição"}
                                    <ChevronDown className={`w-3.5 h-3.5 transition-transform duration-200 ${
                                      expandedEventIds[event.id] ? "rotate-180" : ""
                                    }`} />
                                  </button>
                                </div>
                              )}

                              {/* Descrição - exibida apenas se houver conteúdo extra e estiver ativada */}
                              {(filter !== "resumo" || expandedEventIds[event.id]) && hasExtraDescription && (
                                <div className="mt-3 pt-3 border-t border-border">
                                  <p className="text-xs uppercase tracking-wide text-muted-foreground mb-2">
                                    Descrição Original
                                  </p>
                                  <div className="text-sm text-foreground leading-relaxed bg-secondary/30 p-3 rounded-lg">
                                    {shouldTruncate(event.descricao) && !expandedEventIds[event.id] ? (
                                      <>
                                        {renderDescriptionWithLinks(truncateText(event.descricao))}...
                                        <button
                                          onClick={() => toggleEventExpansion(event.id)}
                                          className="text-xs font-semibold text-primary hover:underline ml-1.5 inline-flex items-center gap-0.5 focus:outline-none whitespace-nowrap"
                                        >
                                          Ver mais
                                        </button>
                                      </>
                                    ) : (
                                      <>
                                        {renderDescriptionWithLinks(event.descricao)}
                                        {shouldTruncate(event.descricao) && (
                                          <button
                                            onClick={() => toggleEventExpansion(event.id)}
                                            className="text-xs font-semibold text-primary hover:underline ml-1.5 inline-flex items-center gap-0.5 focus:outline-none whitespace-nowrap"
                                          >
                                            Ver menos
                                          </button>
                                        )}
                                      </>
                                    )}
                                  </div>
                                </div>
                              )}
                            </>
                          );
                        })()}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Botão Ver Mais */}
              {filteredEvents.length > visibleCount && (
                <div className="flex justify-center mt-6 pt-4 border-t border-border/50">
                  <button
                    onClick={() => setVisibleCount((prev) => prev + 15)}
                    className="px-4 py-2 text-sm font-medium bg-card text-foreground hover:bg-secondary border border-border rounded-lg flex items-center gap-2 transition-all shadow-sm hover:shadow"
                  >
                    <span>Ver mais eventos</span>
                    <span className="text-xs text-muted-foreground bg-secondary px-2 py-0.5 rounded-full font-semibold">
                      +{filteredEvents.length - visibleCount}
                    </span>
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
