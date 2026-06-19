import { Clock } from "lucide-react";
import type { BreakdownFase } from "@/shared/types";

export interface BreakdownFaseCardProps {
  tempoPorFase: BreakdownFase[];
}

export function BreakdownFaseCard({ tempoPorFase }: BreakdownFaseCardProps) {
  if (!tempoPorFase || tempoPorFase.length < 2) return null;

  const maxDias = Math.max(...tempoPorFase.map((t) => t.dias));

  return (
    <div className="bg-card border border-border rounded-lg p-4 md:p-6 shadow-sm">
      <div className="flex items-center gap-3 mb-4 border-b border-border pb-4">
        <div className="p-2 bg-primary/10 rounded-lg text-primary">
          <Clock className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-foreground">Tempo por Fase</h2>
          <p className="text-sm text-muted-foreground">Tempo acumulado em cada comissão ou fase</p>
        </div>
      </div>

      <div className="space-y-4">
        {tempoPorFase.map((item, index) => (
          <div key={`${item.fase}-${index}`} className="flex flex-col gap-1.5">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium text-foreground truncate mr-2" title={item.fase}>
                {item.fase}
              </span>
              <span className="text-muted-foreground whitespace-nowrap bg-secondary px-2 py-0.5 rounded text-xs font-semibold">
                {item.dias} dias
              </span>
            </div>
            <div className="h-2 w-full bg-secondary/50 rounded-full overflow-hidden">
              <div
                className="h-full bg-primary/80 rounded-full"
                style={{ width: `${Math.max(2, (item.dias / maxDias) * 100)}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
