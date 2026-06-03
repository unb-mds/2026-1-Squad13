interface PipelineStageProps {
  name: string;
  count: number;
  percentage: number;
  medianDays: number;
  isActive?: boolean;
}

export function PipelineStage({ name, count, percentage, medianDays, isActive }: PipelineStageProps) {
  // Calculate bar height (max 120px)
  const barHeight = Math.max((percentage / 100) * 120, 6);

  // Calculate opacity based on percentage (0.35 to 0.90 range)
  // Active stage always gets full opacity
  const barOpacity = isActive ? 1 : 0.35 + (percentage / 100) * 0.55;

  return (
    <div className="flex flex-col items-center flex-1 min-w-0">
      {/* 1. Count Label - Fixed 32px slot */}
      <div className="h-8 flex items-center justify-center">
        <span
          className={`font-normal ${
            isActive ? "text-xl font-medium text-primary" : "text-2xl text-foreground"
          }`}
        >
          {count}
        </span>
      </div>

      {/* 2. Bar Area - Fixed 120px height, bar grows upward */}
      <div className="h-[120px] w-full flex items-end px-2">
        <div
          className="w-full rounded-t bg-primary"
          style={{ height: `${barHeight}px`, opacity: barOpacity }}
        />
      </div>

      {/* 3. Baseline Rule - 1px horizontal line */}
      <div className="w-full h-px bg-border/60" />

      {/* 4. Median Badge - Below baseline */}
      <div className="mt-1.5">
        <span
          className={`inline-block px-[7px] py-0.5 rounded-full text-[10px] font-medium ${
            isActive
              ? "bg-primary text-white"
              : "bg-secondary text-muted-foreground"
          }`}
        >
          {medianDays}d mediana
        </span>
      </div>

      {/* 5. Phase Name - 10px, line-clamp-2 */}
      <div className="text-center px-1 mt-1">
        <p
          className={`text-[10px] leading-tight line-clamp-2 ${
            isActive ? "text-muted-foreground" : "text-muted-foreground/70"
          }`}
        >
          {name}
        </p>
      </div>
    </div>
  );
}
