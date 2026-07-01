import { LucideIcon, TrendingUp, TrendingDown, Info } from "lucide-react";

interface KPICardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: {
    value: string;
    isPositive: boolean;
  };
  isAlarm?: boolean;
  metadata?: {
    definition: string;
    source: string;
    rule: string;
  };
}

export function KPICard({ title, value, subtitle, icon: Icon, trend, isAlarm, metadata }: KPICardProps) {
  return (
    <div
      className={`bg-card border rounded-lg p-6 transition-all ${
        isAlarm
          ? "border-l-4 border-l-destructive hover:bg-destructive/5 hover:shadow-lg"
          : "border-border hover:shadow-md"
      }`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-1.5 mb-1 relative group">
            <p className="text-sm text-muted-foreground">{title}</p>
            {metadata && (
              <div className="inline-block relative">
                <Info className="w-3.5 h-3.5 text-muted-foreground/50 hover:text-foreground cursor-pointer transition-colors" />
                <div className="invisible opacity-0 group-hover:visible group-hover:opacity-100 absolute left-0 bottom-6 z-50 w-64 p-3 bg-card border border-border rounded-lg shadow-xl text-xs text-foreground transition-all duration-200 pointer-events-none">
                  <div className="space-y-2">
                    <div>
                      <span className="font-semibold text-primary block mb-0.5">Definição</span>
                      <span className="text-muted-foreground">{metadata.definition}</span>
                    </div>
                    <div>
                      <span className="font-semibold text-primary block mb-0.5">Regra de Cálculo</span>
                      <span className="text-muted-foreground">{metadata.rule}</span>
                    </div>
                    <div>
                      <span className="font-semibold text-primary block mb-0.5">Fonte</span>
                      <span className="text-muted-foreground">{metadata.source}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
          <div className="flex items-baseline gap-2">
            <h3
              className={`font-semibold ${
                isAlarm ? "text-4xl text-destructive" : "text-3xl text-foreground"
              }`}
            >
              {value}
            </h3>
          </div>
          {subtitle && (
            <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
          )}
          {trend && (
            <div className="flex items-center gap-1.5 mt-2">
              {trend.isPositive ? (
                <TrendingUp className="w-3.5 h-3.5 text-green-600" />
              ) : (
                <TrendingDown className="w-3.5 h-3.5 text-red-600" />
              )}
              <span
                className={`text-xs font-medium ${
                  trend.isPositive ? "text-green-700" : "text-red-700"
                }`}
              >
                {trend.value}
              </span>
            </div>
          )}
        </div>
        <div
          className={`flex items-center justify-center w-12 h-12 rounded-lg ${
            isAlarm ? "bg-destructive/10" : "bg-primary/10"
          }`}
        >
          <Icon className={`w-6 h-6 ${isAlarm ? "text-destructive" : "text-primary"}`} />
        </div>
      </div>
    </div>
  );
}
