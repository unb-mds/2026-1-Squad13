import { ArrowRight, Building2, CheckCircle2 } from "lucide-react";

export interface TransitStep {
  casa: "Câmara" | "Senado";
  tipo: "origem" | "revisora" | "retorno" | "final";
  dataEntrada?: string;
  dataSaida?: string;
  duracaoDias?: number;
}

interface HouseTransitDiagramProps {
  steps: TransitStep[];
  historicoUnificado: boolean;
}

export function HouseTransitDiagram({ steps, historicoUnificado }: HouseTransitDiagramProps) {
  const getCasaColor = (casa: "Câmara" | "Senado") => {
    return casa === "Câmara"
      ? "bg-blue-100 text-blue-800 border-blue-200"
      : "bg-purple-100 text-purple-800 border-purple-200";
  };

  const getTipoLabel = (tipo: TransitStep["tipo"]) => {
    switch (tipo) {
      case "origem":
        return "Casa de Origem";
      case "revisora":
        return "Casa Revisora";
      case "retorno":
        return "Retorno para Origem";
      case "final":
        return "Aprovação Final";
    }
  };

  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-foreground">
          Trânsito Entre Casas Legislativas
        </h2>
        <p className="text-sm text-muted-foreground mt-0.5">
          Fluxo completo da proposição entre Câmara dos Deputados e Senado Federal
        </p>
      </div>

      {/* Unified History Notice */}
      {historicoUnificado && (
        <div className="mb-6 flex items-center gap-3 p-4 bg-emerald-50 border border-emerald-200 rounded-lg">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
          <div>
            <p className="text-sm font-medium text-emerald-900">Histórico Unificado</p>
            <p className="text-xs text-emerald-700 mt-0.5">
              Os registros das duas casas foram consolidados em uma linha do tempo única
            </p>
          </div>
        </div>
      )}

      {/* Transit Diagram */}
      <div className="flex items-center gap-4 overflow-x-auto pb-2">
        {steps.map((step, index) => (
          <div key={index} className="flex items-center gap-4 flex-shrink-0">
            {/* Step Card */}
            <div className="flex flex-col items-center gap-3 min-w-[180px]">
              {/* House Badge */}
              <div
                className={`w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg border font-medium ${getCasaColor(
                  step.casa
                )}`}
              >
                <Building2 className="w-5 h-5" />
                <span>{step.casa}</span>
              </div>

              {/* Type Label */}
              <div className="text-center">
                <p className="text-xs font-medium text-foreground mb-1">
                  {getTipoLabel(step.tipo)}
                </p>
                {step.dataEntrada && (
                  <p className="text-xs text-muted-foreground">
                    Entrada: {step.dataEntrada}
                  </p>
                )}
                {step.dataSaida && (
                  <p className="text-xs text-muted-foreground">
                    Saída: {step.dataSaida}
                  </p>
                )}
                {step.duracaoDias !== undefined && (
                  <div className="mt-2 px-2 py-1 bg-secondary rounded text-xs font-semibold text-foreground">
                    {step.duracaoDias} dias
                  </div>
                )}
              </div>
            </div>

            {/* Arrow */}
            {index < steps.length - 1 && (
              <ArrowRight className="w-6 h-6 text-muted-foreground flex-shrink-0" />
            )}
          </div>
        ))}
      </div>

      {/* Summary */}
      <div className="mt-4 pt-4 border-t border-border">
        <div className="grid grid-cols-3 gap-3">
          <div className="text-center">
            <p className="text-xs text-muted-foreground mb-1">Total de Transições</p>
            <p className="text-lg font-semibold text-foreground">{steps.length - 1}</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-muted-foreground mb-1">Casas Envolvidas</p>
            <p className="text-lg font-semibold text-foreground">
              {new Set(steps.map((s) => s.casa)).size}
            </p>
          </div>
          <div className="text-center">
            <p className="text-xs text-muted-foreground mb-1">Tempo Total</p>
            <p className="text-lg font-semibold text-foreground">
              {steps.reduce((sum, s) => sum + (s.duracaoDias || 0), 0)} dias
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
