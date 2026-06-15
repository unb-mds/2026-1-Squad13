import { LucideIcon, TrendingUp, TrendingDown } from "lucide-react";

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
}

export function KPICard({ title, value, subtitle, icon: Icon, trend, isAlarm }: KPICardProps) {
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
          <p className="text-sm text-muted-foreground mb-1">{title}</p>
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
