import { LucideIcon } from "lucide-react";

interface MetricCardProps {
  label: string;
  value: string | number;
  icon?: LucideIcon;
  highlight?: boolean;
  subtitle?: string;
  tooltip?: string;
}

export function MetricCard({ label, value, icon: Icon, highlight, subtitle, tooltip }: MetricCardProps) {
  return (
    <div
      className={`bg-card border rounded-lg p-4 ${
        highlight ? "border-primary bg-primary/5" : "border-border"
      }`}
      title={tooltip}
    >
      <div className="flex items-start justify-between mb-2">
        <span className="text-xs text-muted-foreground uppercase tracking-wide">{label}</span>
        {Icon && (
          <Icon className={`w-4 h-4 ${highlight ? "text-primary" : "text-muted-foreground"}`} />
        )}
      </div>
      <div className={`text-2xl font-semibold ${highlight ? "text-primary" : "text-foreground"}`}>
        {value}
      </div>
      {subtitle && (
        <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
      )}
    </div>
  );
}
