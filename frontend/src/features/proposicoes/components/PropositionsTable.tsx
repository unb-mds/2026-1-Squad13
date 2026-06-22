import { ArrowUpDown, ExternalLink, ArrowRightLeft } from "lucide-react";
import type { StatusProposicao, BreakdownFase } from "@/shared/types";
import { corStatus } from "@/shared/lib/utils";

export interface Proposition {
  id: string;
  numero: string;
  tipo: string;
  ementa: string;
  casaAtual: "Câmara" | "Senado" | "Sanção";
  faseAtual: string;
  diasNaEtapa: number;
  diasTotais: number;
  ultimoEventoRelevante: string;
  dataUltimoEvento: string;
  autor: string;
  atraso: number;
  coberturaDados: number;
  confiabilidade: "alta" | "media" | "baixa";
  statusTramitacao: "em-tramitacao" | "em-atraso" | "aprovada" | "arquivada" | "aguardando";
  status: StatusProposicao;
  statusLabel: string;
  transitouEntreCasas?: boolean;
  tempoPorFase?: BreakdownFase[];
}

interface PropositionsTableProps {
  propositions: Proposition[];
  onSort?: (field: string) => void;
  onPropositionClick?: (propositionId: string) => void;
}

export function PropositionsTable({ propositions, onSort, onPropositionClick }: PropositionsTableProps) {
  const getCasaColor = (casa: Proposition["casaAtual"]) => {
    switch (casa) {
      case "Câmara":
        return "bg-blue-100 text-blue-800 border-blue-200";
      case "Senado":
        return "bg-purple-100 text-purple-800 border-purple-200";
      case "Sanção":
        return "bg-emerald-100 text-emerald-800 border-emerald-200";
    }
  };

  const getAtrasoColor = (atraso: number) => {
    if (atraso <= 0) return "text-muted-foreground";
    if (atraso <= 15) return "text-amber-600";
    return "text-red-600 font-semibold";
  };

  return (
    <div className="bg-card border border-border rounded-lg overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-secondary border-b border-border">
            <tr>
              <th className="text-left px-4 py-3 text-sm font-medium text-foreground">
                <button
                  className="flex items-center gap-1 hover:text-primary transition-colors"
                  onClick={() => onSort?.("numero")}
                >
                  Proposição
                  <ArrowUpDown className="w-3 h-3" />
                </button>
              </th>
              <th className="text-left px-4 py-3 text-sm font-medium text-foreground">
                Ementa
              </th>
              <th className="text-left px-4 py-3 text-sm font-medium text-foreground">
                <button
                  className="flex items-center gap-1 hover:text-primary transition-colors"
                  onClick={() => onSort?.("casaAtual")}
                >
                  Casa Atual
                  <ArrowUpDown className="w-3 h-3" />
                </button>
              </th>
              <th className="text-left px-4 py-3 text-sm font-medium text-foreground">
                Fase Atual
              </th>
              <th className="text-left px-4 py-3 text-sm font-medium text-foreground">
                <button
                  className="flex items-center gap-1 hover:text-primary transition-colors"
                  onClick={() => onSort?.("diasNaEtapa")}
                >
                  Dias na Etapa
                  <ArrowUpDown className="w-3 h-3" />
                </button>
              </th>
              <th className="text-left px-4 py-3 text-sm font-medium text-foreground">
                Andamento Bruto (API)
              </th>
              <th className="text-left px-4 py-3 text-sm font-medium text-foreground">
                <button
                  className="flex items-center gap-1 hover:text-primary transition-colors"
                  onClick={() => onSort?.("atraso")}
                >
                  Alerta de Atraso
                  <ArrowUpDown className="w-3 h-3" />
                </button>
              </th>
              <th className="text-left px-4 py-3 text-sm font-medium text-foreground">
                Cobertura
              </th>
              <th className="text-left px-4 py-3 text-sm font-medium text-foreground">
                Status de Negócio
              </th>
              <th className="w-12"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {propositions.map((prop) => (
              <tr
                key={prop.id}
                onClick={() => onPropositionClick?.(prop.id)}
                className="hover:bg-secondary/50 transition-colors cursor-pointer"
              >
                <td className="px-4 py-4">
                  <div className="flex flex-col">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-foreground">
                        {prop.tipo} {prop.numero}
                      </span>
                      {prop.transitouEntreCasas && (
                        <span className="inline-flex items-center text-primary" title="Transitou entre casas">
                          <ArrowRightLeft className="w-3.5 h-3.5" />
                        </span>
                      )}
                    </div>
                    <span className="text-xs text-muted-foreground mt-0.5">{prop.autor}</span>
                  </div>
                </td>
                <td className="px-4 py-4">
                  <p className="text-sm text-foreground line-clamp-2 max-w-md">
                    {prop.ementa}
                  </p>
                </td>
                <td className="px-4 py-4">
                  <span
                    className={`inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium border ${getCasaColor(
                      prop.casaAtual
                    )}`}
                  >
                    {prop.casaAtual}
                  </span>
                </td>
                <td className="px-4 py-4">
                  <span className="text-sm text-foreground">{prop.faseAtual}</span>
                </td>
                <td className="px-4 py-4">
                  <span className="text-sm font-medium text-foreground">
                    {prop.diasNaEtapa} dias
                  </span>
                </td>
                <td className="px-4 py-4">
                  <div className="flex flex-col max-w-xs">
                    <span className="text-sm text-foreground line-clamp-1">
                      {prop.ultimoEventoRelevante}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {prop.dataUltimoEvento}
                    </span>
                  </div>
                </td>
                <td className="px-4 py-4">
                  <div className="flex flex-col">
                    <span className={`text-sm font-medium ${getAtrasoColor(prop.atraso)}`}>
                      {prop.atraso > 0 ? `+${prop.atraso}` : prop.atraso} dias
                    </span>
                    {prop.atraso > 15 && (
                      <span className="text-xs text-red-600 mt-0.5">Crítico</span>
                    )}
                  </div>
                </td>
                <td className="px-4 py-4">
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden min-w-[60px]">
                      <div
                        className={`h-full rounded-full ${
                          prop.coberturaDados >= 80
                            ? "bg-emerald-500"
                            : prop.coberturaDados >= 50
                            ? "bg-amber-500"
                            : "bg-slate-400"
                        }`}
                        style={{ width: `${prop.coberturaDados}%` }}
                      />
                    </div>
                    <span className="text-xs text-muted-foreground whitespace-nowrap">
                      {prop.coberturaDados}%
                    </span>
                  </div>
                </td>
                <td className="px-4 py-4">
                  <span
                    className={`inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium border ${corStatus(
                      prop.status
                    )}`}
                  >
                    {prop.status}
                  </span>
                </td>
                <td className="px-4 py-4">
                  <button className="text-muted-foreground hover:text-primary transition-colors">
                    <ExternalLink className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
