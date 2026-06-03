import { useState } from "react";
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

export function EventTimeline({ events, filterByPhaseId }: EventTimelineProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [filter, setFilter] = useState<"relevantes" | "todos">("relevantes");

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

  const filteredEvents = events.filter((event) => {
    if (filter === "relevantes") return event.isRelevante;
    return true;
  });

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
                {events.filter((e) => e.isRelevante).length} relevantes • {events.length} total
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
          {/* Filters */}
          <div className="px-6 py-4 bg-secondary/30 border-b border-border">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setFilter("relevantes")}
                className={`px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
                  filter === "relevantes"
                    ? "bg-primary text-primary-foreground"
                    : "bg-card text-foreground hover:bg-secondary border border-border"
                }`}
              >
                Relevantes ({events.filter((e) => e.isRelevante).length})
              </button>
              <button
                onClick={() => setFilter("todos")}
                className={`px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
                  filter === "todos"
                    ? "bg-primary text-primary-foreground"
                    : "bg-card text-foreground hover:bg-secondary border border-border"
                }`}
              >
                Todos ({events.length})
              </button>
            </div>
          </div>

          {/* Events List */}
          <div className="p-6">
            <div className="relative">
              {/* Timeline Line */}
              <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-border" />

              {/* Events */}
              <div className="space-y-5">
                {filteredEvents.map((event, index) => {
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
                      <div className="bg-card border border-border rounded-lg p-4 hover:shadow-md transition-shadow">
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

                        {/* Description */}
                        <div className="mt-3 pt-3 border-t border-border">
                          <p className="text-xs uppercase tracking-wide text-muted-foreground mb-2">
                            Descrição Original
                          </p>
                          <p className="text-sm text-foreground leading-relaxed bg-secondary/30 p-3 rounded-lg">
                            {event.descricao}
                          </p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
