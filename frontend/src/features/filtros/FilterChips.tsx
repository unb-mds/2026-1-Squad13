import { X } from "lucide-react";

export interface FilterOption {
  id: string;
  label: string;
  category: "casa" | "tipo" | "status" | "cobertura";
}

interface FilterChipsProps {
  activeFilters: FilterOption[];
  onRemoveFilter: (filterId: string) => void;
  onClearAll: () => void;
}

export function FilterChips({ activeFilters, onRemoveFilter, onClearAll }: FilterChipsProps) {
  if (activeFilters.length === 0) return null;

  return (
    <div className="flex items-center gap-2 flex-wrap">
      {activeFilters.map((filter) => (
        <button
          key={filter.id}
          onClick={() => onRemoveFilter(filter.id)}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors group"
        >
          <span>{filter.label}</span>
          <X className="w-3.5 h-3.5 opacity-70 group-hover:opacity-100" />
        </button>
      ))}
      <button
        onClick={onClearAll}
        className="text-sm text-muted-foreground hover:text-primary transition-colors underline"
      >
        Limpar filtros
      </button>
    </div>
  );
}
