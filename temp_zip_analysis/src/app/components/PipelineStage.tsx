interface PipelineStageProps {
  name: string;
  count: number;
  percentage: number;
  medianDays: number;
  isActive?: boolean;
}

export function PipelineStage({ name, count, percentage, medianDays, isActive }: PipelineStageProps) {
  return (
    <div className="flex flex-col items-center gap-2 flex-1 min-w-0">
      <div className="relative w-full">
        <div
          className={`h-2 rounded-full transition-all ${
            isActive ? "bg-primary" : "bg-muted"
          }`}
          style={{ width: `${Math.max(percentage, 5)}%` }}
        />
      </div>
      <div className="text-center">
        <div className={`text-2xl font-semibold ${isActive ? "text-primary" : "text-foreground"}`}>
          {count}
        </div>
        <div className="text-xs text-muted-foreground mt-0.5 px-2 line-clamp-2">
          {name}
        </div>
        <div className="text-xs text-muted-foreground mt-0.5">
          {percentage.toFixed(1)}%
        </div>
        <div className="text-xs font-medium text-foreground mt-1">
          {medianDays}d
        </div>
      </div>
    </div>
  );
}
