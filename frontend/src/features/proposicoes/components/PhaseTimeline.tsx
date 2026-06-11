import { Calendar, Clock, RotateCcw, AlertCircle, ChevronDown, ChevronRight } from "lucide-react";
import { useState } from "react";

export interface PhaseEntry {
  id: string;
  fase: string;
  ocorrencia: number;
  dataEntrada: string;
  dataSaida?: string;
  duracaoDias: number;
  atrasoDias?: number;
  isRecorrente: boolean;
  isCurrent: boolean;
  motivoTravamento?: string;
  numeroTurno?: number;
  subtipoFase?: string;
}

interface PhaseTimelineProps {
  phases: PhaseEntry[];
  onPhaseClick?: (phaseId: string) => void;
}

export function PhaseTimeline({ phases, onPhaseClick }: PhaseTimelineProps) {
  const [expandedPhases, setExpandedPhases] = useState<Set<string>>(new Set());

  const togglePhase = (phaseId: string) => {
    const newExpanded = new Set(expandedPhases);
    if (newExpanded.has(phaseId)) {
      newExpanded.delete(phaseId);
    } else {
      newExpanded.add(phaseId);
    }
    setExpandedPhases(newExpanded);
    onPhaseClick?.(phaseId);
  };

  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <div className="mb-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <h2 className="text-lg font-semibold text-foreground">Timeline por Fases Agregadas</h2>
            <p className="text-sm text-muted-foreground mt-0.5">
              Períodos consolidados de tramitação • Clique em cada fase para ver detalhes completos
            </p>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-blue-50 border border-blue-200 rounded-lg">
            <ChevronRight className="w-4 h-4 text-blue-600" />
            <span className="text-xs text-blue-700 font-medium">Expansível por fase</span>
          </div>
        </div>
      </div>

      <div className="space-y-2">
        {phases.map((phase, index) => {
          const isExpanded = expandedPhases.has(phase.id);

          return (
            <div
              key={phase.id}
              className={`relative border rounded-lg transition-all ${
                phase.isCurrent
                  ? "border-primary bg-primary/5 border-l-4"
                  : "border-border hover:border-primary/30 hover:bg-secondary/30"
              }`}
            >
              {/* Connection Line */}
              {index < phases.length - 1 && (
                <div className="absolute left-6 bottom-0 w-0.5 h-2 bg-border translate-y-full" />
              )}

              {/* Collapsed View */}
              <button
                onClick={() => togglePhase(phase.id)}
                className="w-full text-left p-4 flex items-center gap-4 hover:bg-secondary/20 transition-colors rounded-lg"
              >
                {/* Expand Icon */}
                <div className="flex-shrink-0">
                  {isExpanded ? (
                    <ChevronDown className="w-5 h-5 text-muted-foreground" />
                  ) : (
                    <ChevronRight className="w-5 h-5 text-muted-foreground" />
                  )}
                </div>

                {/* Timeline Indicator */}
                <div className="flex-shrink-0">
                  <div
                    className={`w-3 h-3 rounded-full border-2 ${
                      phase.isCurrent
                        ? "bg-primary border-primary"
                        : "bg-card border-muted-foreground"
                    }`}
                  />
                </div>

                {/* Phase Summary */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h3
                      className={`font-medium text-sm ${
                        phase.isCurrent ? "text-primary" : "text-foreground"
                      }`}
                    >
                      {phase.fase}
                    </h3>
                    {phase.isRecorrente && (
                      <span className="inline-flex items-center gap-1 px-1.5 py-0.5 bg-amber-100 text-amber-800 border border-amber-200 rounded text-xs">
                        <RotateCcw className="w-3 h-3" />
                        {phase.ocorrencia}ª vez
                      </span>
                    )}
                    {phase.isCurrent && (
                      <span className="inline-flex items-center px-2 py-0.5 bg-primary text-primary-foreground rounded text-xs font-medium">
                        Atual
                      </span>
                    )}
                  </div>
                  {!isExpanded && (
                    <p className="text-xs text-muted-foreground">
                      {phase.duracaoDias} dias
                      {phase.atrasoDias !== undefined && phase.atrasoDias > 0 && (
                        <span className="text-red-600 ml-2">
                          (+{phase.atrasoDias}d atraso)
                        </span>
                      )}
                    </p>
                  )}
                </div>

                {/* Duration Badge */}
                <div className="flex-shrink-0">
                  <div
                    className={`text-right px-3 py-1 rounded-lg ${
                      phase.atrasoDias && phase.atrasoDias > 15
                        ? "bg-red-100 text-red-700"
                        : phase.atrasoDias && phase.atrasoDias > 0
                        ? "bg-amber-100 text-amber-700"
                        : "bg-secondary text-foreground"
                    }`}
                  >
                    <div className="text-lg font-semibold">{phase.duracaoDias}</div>
                    <div className="text-xs">dias</div>
                  </div>
                </div>
              </button>

              {/* Expanded Details */}
              {isExpanded && (
                <div className="px-4 pb-4 space-y-3 border-t border-border mt-2 pt-3">
                  {/* Dates */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex items-start gap-2">
                      <Calendar className="w-4 h-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                      <div>
                        <p className="text-xs text-muted-foreground">Data de Entrada</p>
                        <p className="text-sm font-medium text-foreground">{phase.dataEntrada}</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-2">
                      {phase.dataSaida ? (
                        <>
                          <Calendar className="w-4 h-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                          <div>
                            <p className="text-xs text-muted-foreground">Data de Saída</p>
                            <p className="text-sm font-medium text-foreground">{phase.dataSaida}</p>
                          </div>
                        </>
                      ) : (
                        <>
                          <Clock className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                          <div>
                            <p className="text-xs text-muted-foreground">Status</p>
                            <p className="text-sm font-medium text-primary">Em andamento</p>
                          </div>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Metrics */}
                  <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm">
                    <div className="flex items-center gap-1.5">
                      <span className="text-muted-foreground">Duração:</span>
                      <span className="font-medium text-foreground">{phase.duracaoDias} dias</span>
                    </div>
                    {phase.numeroTurno !== undefined && phase.numeroTurno !== null && (
                      <div className="flex items-center gap-1.5 bg-blue-50 text-blue-700 px-2 py-0.5 rounded text-xs font-semibold">
                        <span>{phase.numeroTurno}º Turno</span>
                      </div>
                    )}
                    {phase.subtipoFase && (
                      <div className="flex items-center gap-1.5 bg-purple-50 text-purple-700 px-2 py-0.5 rounded text-xs font-semibold uppercase">
                        <span>{phase.subtipoFase}</span>
                      </div>
                    )}
                    {phase.atrasoDias !== undefined && (
                      <div className="flex items-center gap-1.5">
                        <span className="text-muted-foreground">Atraso:</span>
                        <span
                          className={`font-medium ${
                            phase.atrasoDias > 15
                              ? "text-red-600"
                              : phase.atrasoDias > 0
                              ? "text-amber-600"
                              : "text-green-600"
                          }`}
                        >
                          {phase.atrasoDias > 0 ? `+${phase.atrasoDias}` : phase.atrasoDias} dias
                        </span>
                      </div>
                    )}
                    {phase.isRecorrente && (
                      <div className="flex items-center gap-1.5">
                        <RotateCcw className="w-3.5 h-3.5 text-amber-600" />
                        <span className="text-sm text-amber-700 font-medium">
                          {phase.ocorrencia}ª ocorrência desta fase
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Travamento Alert */}
                  {phase.motivoTravamento && (
                    <div className="flex items-start gap-2 px-3 py-2 bg-amber-50 border border-amber-200 rounded-lg">
                      <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
                      <p className="text-xs text-amber-800">
                        <strong>Motivo de Travamento:</strong> {phase.motivoTravamento}
                      </p>
                    </div>
                  )}

                  {/* Atraso Alert */}
                  {phase.atrasoDias !== undefined && phase.atrasoDias > 15 && (
                    <div className="flex items-start gap-2 px-3 py-2 bg-red-50 border border-red-200 rounded-lg">
                      <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
                      <p className="text-xs text-red-800">
                        <strong>Atraso crítico:</strong> Tempo acima da mediana histórica para esta
                        fase. Proposição está {phase.atrasoDias} dias além do esperado.
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
