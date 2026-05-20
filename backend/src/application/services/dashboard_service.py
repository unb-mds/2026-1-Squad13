import json
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, date

from application.ports.cache_provider import CacheProvider
from infrastructure.repositories.sql_proposicao_repository import (
    SQLProposicaoRepository,
)
from infrastructure.repositories.sql_evento_tramitacao_repository import (
    SQLEventoTramitacaoRepository,
)
from infrastructure.repositories.sql_fase_analitica_repository import (
    SQLFaseAnaliticaRepository,
)
from infrastructure.repositories.sql_dashboard_repository import SQLDashboardRepository
from domain.entities.evento_tramitacao import EventoTramitacao
from domain.entities.tipo_evento import TipoEvento
from domain.constants import LIMITE_DIAS_ATRASO


class DashboardService:
    """
    Serviço de Aplicação para calcular métricas e dados do dashboard.
    Centraliza a lógica usando o repositório SQL para performance no banco.
    """

    def __init__(
        self,
        repository: SQLProposicaoRepository,
        evento_repo: SQLEventoTramitacaoRepository,
        fase_repo: Optional[SQLFaseAnaliticaRepository] = None,
        cache_provider: Optional[CacheProvider] = None,
        dashboard_repo: Optional[SQLDashboardRepository] = None,
    ):
        self.repository = repository
        self.evento_repo = evento_repo
        self.fase_repo = fase_repo
        self.cache_provider = cache_provider
        self.dashboard_repo = dashboard_repo
        self.cache_ttl = 86400  # 24 horas em segundos

    def _get_cached(self, key: str) -> Optional[Any]:
        if not self.cache_provider:
            return None

        cached = self.cache_provider.get(key)
        if not cached:
            return None

        if isinstance(cached, str):
            try:
                return json.loads(cached)
            except json.JSONDecodeError:
                return None
        return cached

    def _set_cache(self, key: str, value: Any) -> None:
        if self.cache_provider:
            self.cache_provider.set(key, json.dumps(value), self.cache_ttl)

    def _gerar_cache_key(self, base_key: str, filtros: Optional[Dict] = None) -> str:
        """Gera uma chave de cache única baseada no hash dos filtros."""
        if not filtros:
            return base_key

        # Sanitiza filtros para garantir apenas tipos serializáveis (str, int, float, bool, None)
        filtros_sanitizados = {
            k: v
            for k, v in filtros.items()
            if isinstance(v, (str, int, float, bool)) or v is None
        }

        # Gera um hash MD5 determinístico dos filtros sanitizados
        filtros_json = json.dumps(filtros_sanitizados, sort_keys=True)
        filtros_hash = hashlib.md5(filtros_json.encode()).hexdigest()
        return f"{base_key}:{filtros_hash}"

    def _calcular_tempo_total(
        self,
        eventos: List[EventoTramitacao],
        fallback_tempo: int,
        proposicao: Optional[Any] = None,
    ) -> int:
        if not eventos:
            return fallback_tempo

        # Encontrar o primeiro evento de APRESENTACAO
        primeiro_evento = None
        for e in eventos:
            if e.tipo_evento == TipoEvento.APRESENTACAO.value:
                primeiro_evento = e
                break

        if not primeiro_evento:
            primeiro_evento = eventos[0]

        # Encontrar último evento terminal (se houver)
        ultimo_evento_terminal = None
        terminais = {
            TipoEvento.APROVACAO.value,
            TipoEvento.REJEICAO.value,
            TipoEvento.ARQUIVAMENTO.value,
            TipoEvento.PREJUDICIALIDADE.value,
            TipoEvento.SANCAO_OU_VETO.value,
            TipoEvento.PROMULGACAO.value,
        }

        for e in reversed(eventos):
            if e.tipo_evento in terminais:
                ultimo_evento_terminal = e
                break

        try:
            inicio = datetime.fromisoformat(
                primeiro_evento.data_evento.replace("Z", "+00:00")
            ).date()
            if ultimo_evento_terminal:
                fim_dt_iso = ultimo_evento_terminal.data_evento.replace("Z", "+00:00")
                fim = datetime.fromisoformat(fim_dt_iso).date()
                # Se temos a instância da proposição, marcamos a data de encerramento
                if proposicao:
                    proposicao.data_encerramento = fim.isoformat()
            else:
                fim = date.today()
                if proposicao:
                    proposicao.data_encerramento = None

            return (fim - inicio).days
        except (ValueError, AttributeError):
            return fallback_tempo

    def _extrair_status_atual(
        self, eventos: List[EventoTramitacao], fallback_status: str
    ) -> str:
        if not eventos:
            return fallback_status

        # Mapeamento simples para display
        mapa_status = {
            TipoEvento.APRESENTACAO.value: "Apresentada",
            TipoEvento.DESPACHO.value: "Em Tramitação",
            TipoEvento.RECEBIMENTO_ORGAO.value: "Em Tramitação",
            TipoEvento.DESIGNACAO_RELATOR.value: "Em Relatoria",
            TipoEvento.PARECER.value: "Parecer emitido",
            TipoEvento.INCLUSAO_PAUTA.value: "Em Pauta",
            TipoEvento.VOTACAO_COMISSAO.value: "Em Votação",
            TipoEvento.VOTACAO_PLENARIO.value: "Em Votação",
            TipoEvento.APROVACAO.value: "Aprovada",
            TipoEvento.REJEICAO.value: "Rejeitada",
            TipoEvento.REMESSA_OUTRA_CASA.value: "Enviada à outra Casa",
            TipoEvento.ARQUIVAMENTO.value: "Arquivada",
            TipoEvento.SANCAO_OU_VETO.value: "Sancionada/Vetada",
            TipoEvento.PROMULGACAO.value: "Promulgada",
        }

        # Procura retroativamente o primeiro status com mapeamento caso o último seja NAO_CLASSIFICADO
        for e in reversed(eventos):
            if e.tipo_evento in mapa_status:
                return mapa_status[e.tipo_evento]

        return fallback_status

    def _obter_dados_em_lote(self, proposicoes) -> List[dict]:
        if not proposicoes:
            return []

        ids = [str(p.id) for p in proposicoes]
        mapa_eventos = self.evento_repo.buscar_por_multiplas_proposicoes(ids)

        dados = []
        for p in proposicoes:
            eventos = mapa_eventos.get(str(p.id), [])
            tempo = self._calcular_tempo_total(eventos, p.tempo_total_dias or 0, p)
            status = self._extrair_status_atual(eventos, p.status)

            # Atraso crítico só faz sentido se a proposição ainda estiver aberta
            atraso_critico = (tempo > LIMITE_DIAS_ATRASO) and (p.data_encerramento is None)

            dados.append(
                {
                    "prop": p,
                    "tempo_total_dias": tempo,
                    "status": status,
                    "atraso_critico": atraso_critico,
                    "orgao_atual": p.orgao_atual,
                    "tipo": p.tipo,
                    "tags": p.tags,
                }
            )
        return dados

    def _agrupar_status(self, status_raw: str) -> str:
        status = status_raw.lower()

        # 1. Aprovadas / Concluídas positivamente
        if any(
            term in status
            for term in [
                "aprovad",
                "sancionad",
                "norma jurídica",
                "promulgad",
                "transformad",
                "enviado à sanção",
                "ofício ao senado - sancionado",
            ]
        ):
            return "Aprovada/Sancionada"

        # 2. Rejeitadas / Concluídas negativamente / Arquivadas
        if any(
            term in status
            for term in [
                "rejeitad",
                "arquivad",
                "retirad",
                "prejudicad",
                "indiferid",
                "devolvida",
                "negado",
                "materia despachada",
            ]
        ):
            return "Rejeitada/Arquivada"

        # 3. Em tramitação / Ativas
        if (
            any(
                term in status
                for term in [
                    "tramitação",
                    "análise",
                    "votação",
                    "pauta",
                    "apresentação",
                    "mesa",
                    "relator",
                    "parecer",
                    "aguardando",
                    "comissão",
                    "ofício",
                    "recebimento",
                    "leitura",
                    "despacho",
                    "relatório",
                ]
            )
            or status == "sem status"
        ):
            return "Em tramitação"

        return "Outros"

    def obter_metricas(self, filtros: Optional[Dict] = None) -> Dict:
        cache_key = self._gerar_cache_key("dashboard:metricas", filtros)

        cached = self._get_cached(cache_key)
        if cached:
            return cached

        if not self.dashboard_repo:
            raise ValueError("dashboard_repo é obrigatório para obter métricas")

        resultado = self.dashboard_repo.obter_metricas_gerais(filtros)
        self._set_cache(cache_key, resultado)
        return resultado

    def obter_dados_tipo(self, filtros: Optional[Dict] = None) -> List[Dict]:
        cache_key = self._gerar_cache_key("dashboard:dados_tipo", filtros)
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        if not self.dashboard_repo:
            raise ValueError("dashboard_repo é obrigatório para obter dados por tipo")

        resultado = self.dashboard_repo.obter_dados_tipo(filtros)
        self._set_cache(cache_key, resultado)
        return resultado


    def obter_dados_comissao(self, filtros: Optional[Dict] = None) -> List[Dict]:
        cache_key = self._gerar_cache_key("dashboard:dados_comissao", filtros)
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        if not self.dashboard_repo:
            raise ValueError("dashboard_repo é obrigatório para obter dados por comissão")

        resultado = self.dashboard_repo.obter_dados_comissao(filtros)
        self._set_cache(cache_key, resultado)
        return resultado

    def obter_dados_status(self, filtros: Optional[Dict] = None) -> List[Dict]:
        cache_key = self._gerar_cache_key("dashboard:dados_status", filtros)
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        if not self.dashboard_repo:
            raise ValueError("dashboard_repo é obrigatório para obter dados por status")

        resultado = self.dashboard_repo.obter_dados_status(filtros)
        self._set_cache(cache_key, resultado)
        return resultado

    def obter_gargalos(self, filtros: Optional[Dict] = None) -> List[Dict]:
        cache_key = self._gerar_cache_key("dashboard:gargalos", filtros)
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        if not self.dashboard_repo:
            raise ValueError("dashboard_repo é obrigatório para obter gargalos")

        resultado = self.dashboard_repo.obter_gargalos(filtros)
        self._set_cache(cache_key, resultado)
        return resultado

    def obter_comparacao_temas(self, filtros: Optional[Dict] = None) -> List[Dict]:
        cache_key = self._gerar_cache_key("dashboard:comparacao_temas", filtros)
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        if not self.dashboard_repo:
            raise ValueError("dashboard_repo é obrigatório para obter comparação de temas")

        dados_db = self.dashboard_repo.obter_proposicoes_para_temas(filtros)
        temas: Dict[str, Dict] = {}
        for d in dados_db:
            tags = d.get("tags")
            if not tags:
                continue
            for tag in tags:
                tag_formatada = tag.capitalize()
                if tag_formatada not in temas:
                    temas[tag_formatada] = {
                        "tema": tag_formatada,
                        "tempos": [],
                        "total": 0,
                        "aprovadas": 0,
                    }
                temas[tag_formatada]["total"] += 1
                if d.get("tempo_total_dias") is not None:
                    temas[tag_formatada]["tempos"].append(d["tempo_total_dias"])
                if d.get("status_agrupado") == "Aprovada/Sancionada":
                    temas[tag_formatada]["aprovadas"] += 1

        resultado = []
        for info in temas.values():
            tempo_medio = (
                sum(info["tempos"]) / len(info["tempos"]) if info["tempos"] else 0
            )
            taxa_aprovacao = (
                (info["aprovadas"] / info["total"] * 100) if info["total"] else 0
            )

            velocidade = "medio"
            if tempo_medio < 300:
                velocidade = "rapido"
            elif tempo_medio > 600:
                velocidade = "lento"

            resultado.append(
                {
                    "tema": info["tema"],
                    "tempoMedioDias": int(tempo_medio),
                    "taxaAprovacao": round(taxa_aprovacao),
                    "velocidade": velocidade,
                }
            )

        resultado = sorted(resultado, key=lambda x: x["tempoMedioDias"])

        self._set_cache(cache_key, resultado)
        return resultado

    def obter_tempo_por_fase(self) -> List[Dict]:
        """
        Calcula o tempo médio que proposições passam em cada fase analítica.

        Retorna apenas fases com ao menos uma proposição registrada,
        ordenadas por ordem_logica. Eventos sem fase_analitica_id são ignorados.
        """
        if self.fase_repo is None:
            return []

        fases = self.fase_repo.buscar_todas()
        if not fases:
            return []

        mapa_fases = {
            f.id: {"codigo": f.codigo, "nome": f.nome, "ordem": f.ordem_logica}
            for f in fases
        }

        todas = self.repository.filtrar()
        if not todas:
            return []

        ids = [str(p.id) for p in todas]
        mapa_eventos = self.evento_repo.buscar_por_multiplas_proposicoes(ids)

        # {fase_id: {"dias": [...], "proposicoes": set()}}
        acumulador: Dict[int, Dict] = {}

        for prop in todas:
            eventos = mapa_eventos.get(str(prop.id), [])
            # filtra eventos sem fase definida
            eventos_com_fase = [e for e in eventos if e.fase_analitica_id is not None]
            if not eventos_com_fase:
                continue

            fase_atual: Optional[int] = None
            data_entrada: Optional[str] = None

            for evento in eventos_com_fase:
                if evento.fase_analitica_id != fase_atual:
                    # registra tempo na fase anterior
                    if fase_atual is not None and data_entrada is not None:
                        try:
                            entrada = datetime.fromisoformat(data_entrada[:10]).date()
                            saida = datetime.fromisoformat(
                                evento.data_evento[:10]
                            ).date()
                            dias = (saida - entrada).days
                            if dias >= 0:
                                if fase_atual not in acumulador:
                                    acumulador[fase_atual] = {
                                        "dias": [],
                                        "proposicoes": set(),
                                    }
                                acumulador[fase_atual]["dias"].append(dias)
                                acumulador[fase_atual]["proposicoes"].add(str(prop.id))
                        except (ValueError, AttributeError):
                            pass

                    fase_atual = evento.fase_analitica_id
                    data_entrada = evento.data_evento

            # registra tempo da última fase (ainda em tramitação ou encerrada)
            if fase_atual is not None and data_entrada is not None:
                try:
                    entrada = datetime.fromisoformat(data_entrada[:10]).date()
                    saida = date.today()
                    dias = (saida - entrada).days
                    if dias >= 0:
                        if fase_atual not in acumulador:
                            acumulador[fase_atual] = {"dias": [], "proposicoes": set()}
                        acumulador[fase_atual]["dias"].append(dias)
                        acumulador[fase_atual]["proposicoes"].add(str(prop.id))
                except (ValueError, AttributeError):
                    pass

        resultado = []
        for fase_id, dados in acumulador.items():
            info = mapa_fases.get(fase_id)
            if info is None:
                continue
            tempo_medio = (
                sum(dados["dias"]) / len(dados["dias"]) if dados["dias"] else 0
            )
            resultado.append(
                {
                    "fase": info["nome"],
                    "codigoFase": info["codigo"],
                    "ordemLogica": info["ordem"],
                    "tempoMedioDias": int(tempo_medio),
                    "quantidadeProposicoes": len(dados["proposicoes"]),
                }
            )

        return sorted(resultado, key=lambda x: x["ordemLogica"])
