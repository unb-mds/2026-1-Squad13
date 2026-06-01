import { ArrowRight, Building2 } from "lucide-react";

interface TransitionData {
  origem: "Câmara" | "Senado";
  destino: "Câmara" | "Senado";
  quantidade: number;
  tempoMedioTransicao: number;
}

interface HouseTransitionsProps {
  transitions: TransitionData[];
  totalCamara: number;
  totalSenado: number;
}

export function HouseTransitions({ transitions, totalCamara, totalSenado }: HouseTransitionsProps) {
  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-foreground">
          Transições Entre Casas Legislativas
        </h2>
        <p className="text-sm text-muted-foreground mt-0.5">
          Fluxo de proposições entre Câmara dos Deputados e Senado Federal
        </p>
      </div>

      {/* Current Distribution */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <div className="flex items-center justify-center w-10 h-10 bg-blue-100 rounded-lg">
              <Building2 className="w-5 h-5 text-blue-600" />
            </div>
            <div className="flex-1">
              <p className="text-xs text-blue-600 font-medium mb-1">CÂMARA DOS DEPUTADOS</p>
              <p className="text-2xl font-semibold text-blue-900">{totalCamara}</p>
              <p className="text-xs text-blue-700 mt-1">proposições em tramitação</p>
            </div>
          </div>
        </div>

        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <div className="flex items-center justify-center w-10 h-10 bg-purple-100 rounded-lg">
              <Building2 className="w-5 h-5 text-purple-600" />
            </div>
            <div className="flex-1">
              <p className="text-xs text-purple-600 font-medium mb-1">SENADO FEDERAL</p>
              <p className="text-2xl font-semibold text-purple-900">{totalSenado}</p>
              <p className="text-xs text-purple-700 mt-1">proposições em tramitação</p>
            </div>
          </div>
        </div>
      </div>

      {/* Transitions */}
      <div className="space-y-3">
        <h3 className="text-sm font-medium text-foreground mb-3">Fluxo de Transições (últimos 30 dias)</h3>
        {transitions.map((transition, idx) => (
          <div
            key={idx}
            className="flex items-center gap-4 p-4 bg-secondary/50 rounded-lg border border-border"
          >
            <div className="flex items-center gap-3 flex-1">
              <div
                className={`px-3 py-2 rounded-lg text-sm font-medium ${
                  transition.origem === "Câmara"
                    ? "bg-blue-100 text-blue-800"
                    : "bg-purple-100 text-purple-800"
                }`}
              >
                {transition.origem}
              </div>
              <ArrowRight className="w-5 h-5 text-muted-foreground" />
              <div
                className={`px-3 py-2 rounded-lg text-sm font-medium ${
                  transition.destino === "Câmara"
                    ? "bg-blue-100 text-blue-800"
                    : "bg-purple-100 text-purple-800"
                }`}
              >
                {transition.destino}
              </div>
            </div>

            <div className="flex items-center gap-6">
              <div className="text-right">
                <p className="text-sm text-muted-foreground">Quantidade</p>
                <p className="text-lg font-semibold text-foreground">{transition.quantidade}</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-muted-foreground">Tempo médio</p>
                <p className="text-lg font-semibold text-foreground">
                  {transition.tempoMedioTransicao} dias
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
