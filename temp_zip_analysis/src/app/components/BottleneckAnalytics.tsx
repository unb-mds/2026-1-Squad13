import { TrendingDown, Clock, AlertCircle } from "lucide-react";
import { useState } from "react";

interface BottleneckItem {
  nome: string;
  proposicoes: number;
  tempoMediano: number;
  rank: number;
}

interface BottleneckAnalyticsProps {
  porOrgao: BottleneckItem[];
  porFase: BottleneckItem[];
  porTema: BottleneckItem[];
}

export function BottleneckAnalytics({ porOrgao, porFase, porTema }: BottleneckAnalyticsProps) {
  const [activeTab, setActiveTab] = useState<"orgao" | "fase" | "tema">("orgao");

  const getCurrentData = () => {
    switch (activeTab) {
      case "orgao":
        return porOrgao;
      case "fase":
        return porFase;
      case "tema":
        return porTema;
    }
  };

  const getSeveridadeColor = (tempoMediano: number) => {
    if (tempoMediano >= 80) return "text-red-600 bg-red-50";
    if (tempoMediano >= 50) return "text-amber-600 bg-amber-50";
    return "text-blue-600 bg-blue-50";
  };

  const getRankBadgeColor = (rank: number) => {
    if (rank === 1) return "bg-red-100 text-red-700 border-red-200";
    if (rank === 2) return "bg-amber-100 text-amber-700 border-amber-200";
    if (rank === 3) return "bg-orange-100 text-orange-700 border-orange-200";
    return "bg-slate-100 text-slate-600 border-slate-200";
  };

  return (
    <div className="bg-card border border-border rounded-lg overflow-hidden">
      <div className="p-6 border-b border-border">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-semibold text-foreground">
              Análise de Gargalos
            </h2>
            <p className="text-sm text-muted-foreground mt-0.5">
              Ranking por tempo mediano de tramitação
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">Últimos 90 dias</span>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab("orgao")}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
              activeTab === "orgao"
                ? "bg-primary text-primary-foreground"
                : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
            }`}
          >
            Por Órgão
          </button>
          <button
            onClick={() => setActiveTab("fase")}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
              activeTab === "fase"
                ? "bg-primary text-primary-foreground"
                : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
            }`}
          >
            Por Fase
          </button>
          <button
            onClick={() => setActiveTab("tema")}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
              activeTab === "tema"
                ? "bg-primary text-primary-foreground"
                : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
            }`}
          >
            Por Tema
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        <div className="space-y-3">
          {getCurrentData().map((item) => (
            <div
              key={item.nome}
              className={`flex items-center gap-4 p-4 rounded-lg border transition-all hover:shadow-sm ${
                item.rank <= 3 ? "border-l-4" : ""
              } ${
                item.rank === 1
                  ? "border-l-red-500"
                  : item.rank === 2
                  ? "border-l-amber-500"
                  : item.rank === 3
                  ? "border-l-orange-500"
                  : "border-border"
              }`}
            >
              {/* Rank Badge */}
              <div
                className={`flex items-center justify-center w-8 h-8 rounded-lg border font-semibold text-sm ${getRankBadgeColor(
                  item.rank
                )}`}
              >
                {item.rank}
              </div>

              {/* Info */}
              <div className="flex-1 min-w-0">
                <h4 className="font-medium text-foreground mb-1">{item.nome}</h4>
                <div className="flex items-center gap-4 text-sm">
                  <div className="flex items-center gap-1.5">
                    <AlertCircle className="w-3.5 h-3.5 text-muted-foreground" />
                    <span className="text-muted-foreground">{item.proposicoes} proposições</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <TrendingDown className="w-3.5 h-3.5 text-muted-foreground" />
                    <span className="text-muted-foreground">
                      Mediana: <span className="font-medium text-foreground">{item.tempoMediano} dias</span>
                    </span>
                  </div>
                </div>
              </div>

              {/* Severity Indicator */}
              <div
                className={`flex items-center justify-center w-16 h-16 rounded-lg ${getSeveridadeColor(
                  item.tempoMediano
                )}`}
              >
                <div className="text-center">
                  <div className="text-xl font-semibold">{item.tempoMediano}</div>
                  <div className="text-xs">dias</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
