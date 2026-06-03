import { Shield, AlertTriangle, CheckCircle2, Database, Clock, Info } from "lucide-react";

interface DataReliabilityProps {
  cobertura: number;
  statusHistorico: "completo" | "parcial" | "fallback";
  ultimaAtualizacao: string;
  fontes: string[];
  limitacoes?: string[];
}

export function DataReliability({
  cobertura,
  statusHistorico,
  ultimaAtualizacao,
  fontes,
  limitacoes,
}: DataReliabilityProps) {
  const getStatusConfig = () => {
    switch (statusHistorico) {
      case "completo":
        return {
          icon: CheckCircle2,
          color: "text-emerald-600 bg-emerald-50 border-emerald-200",
          label: "Histórico Completo",
          description: "Todos os eventos foram capturados das fontes oficiais",
        };
      case "parcial":
        return {
          icon: AlertTriangle,
          color: "text-amber-600 bg-amber-50 border-amber-200",
          label: "Histórico Parcial",
          description: "Alguns eventos podem estar ausentes ou incompletos",
        };
      case "fallback":
        return {
          icon: Database,
          color: "text-blue-600 bg-blue-50 border-blue-200",
          label: "Dados de Fallback Local",
          description: "Informações baseadas em cache local ou fontes alternativas",
        };
    }
  };

  const statusConfig = getStatusConfig();
  const StatusIcon = statusConfig.icon;

  const getCoberturaColor = (cobertura: number) => {
    if (cobertura >= 90) return "bg-emerald-500";
    if (cobertura >= 70) return "bg-amber-500";
    return "bg-red-500";
  };

  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-foreground flex items-center gap-2">
          <Shield className="w-5 h-5 text-primary" />
          Confiabilidade dos Dados
        </h2>
        <p className="text-sm text-muted-foreground mt-0.5">
          Qualidade, cobertura e origem das informações de tramitação
        </p>
      </div>

      {/* Status do Histórico */}
      <div className={`mb-6 flex items-start gap-3 p-4 border rounded-lg ${statusConfig.color}`}>
        <StatusIcon className="w-5 h-5 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <p className="font-medium mb-1">{statusConfig.label}</p>
          <p className="text-sm opacity-90">{statusConfig.description}</p>
        </div>
      </div>

      {/* Cobertura */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-foreground">Cobertura de Dados</span>
          <span className="text-sm font-semibold text-foreground">{cobertura}%</span>
        </div>
        <div className="h-2 bg-muted rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all ${getCoberturaColor(cobertura)}`}
            style={{ width: `${cobertura}%` }}
          />
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          Percentual de campos obrigatórios preenchidos e validados
        </p>
      </div>

      {/* Última Atualização */}
      <div className="mb-6 flex items-center gap-3 p-3 bg-secondary rounded-lg">
        <Clock className="w-4 h-4 text-muted-foreground" />
        <div>
          <p className="text-xs text-muted-foreground">Última Atualização</p>
          <p className="text-sm font-medium text-foreground">{ultimaAtualizacao}</p>
        </div>
      </div>

      {/* Fontes */}
      <div className="mb-6">
        <h3 className="text-sm font-medium text-foreground mb-3 flex items-center gap-2">
          <Database className="w-4 h-4" />
          Fontes de Dados
        </h3>
        <div className="space-y-2">
          {fontes.map((fonte, index) => (
            <div
              key={index}
              className="flex items-center gap-2 text-sm text-muted-foreground"
            >
              <div className="w-1.5 h-1.5 rounded-full bg-primary" />
              <span>{fonte}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Limitações */}
      {limitacoes && limitacoes.length > 0 && (
        <div className="border-t border-border pt-6">
          <h3 className="text-sm font-medium text-foreground mb-3 flex items-center gap-2">
            <Info className="w-4 h-4" />
            Observações Metodológicas
          </h3>
          <div className="space-y-2">
            {limitacoes.map((limitacao, index) => (
              <div
                key={index}
                className="flex items-start gap-2 text-xs text-muted-foreground"
              >
                <span className="text-muted-foreground mt-0.5">•</span>
                <span>{limitacao}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
