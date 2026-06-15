import logging
from datetime import UTC, datetime

from application.ports.camara_adapter import CamaraAdapterPort
from application.ports.cobertura_snapshot_repository import (
    CoberturaSnapshotRepositoryPort,
)
from application.ports.proposicao_repository import ProposicaoRepositoryPort
from application.ports.senado_adapter import SenadoAdapterPort
from domain.entities.cobertura_snapshot import CoberturaSnapshot

logger = logging.getLogger(__name__)

# Mapeamento entre a chave curta de fonte e o valor do campo `orgao_origem` no banco.
# Usado para garantir que o `contar()` filtre apenas proposições da fonte correta.
_ORGAO_NOME_POR_FONTE: dict[str, str] = {
    "camara": "Câmara dos Deputados",
    "senado": "Senado Federal",
}


class AtualizarCoberturaService:
    """
    Serviço que atualiza e expõe os snapshots de cobertura analítica.

    Cada snapshot é identificado pela tripla (ano, tipo_proposicao, fonte).
    Isso evita que a contagem de proposições da Câmara seja somada com a do Senado
    ao ser comparada com o total reportado por apenas uma das APIs, o que gerava
    percentuais de cobertura ficticiamente acima de 100%.
    """

    def __init__(
        self,
        cobertura_repo: CoberturaSnapshotRepositoryPort,
        proposicao_repo: ProposicaoRepositoryPort,
        camara_adapter: CamaraAdapterPort,
        senado_adapter: SenadoAdapterPort,
    ):
        self.cobertura_repo = cobertura_repo
        self.proposicao_repo = proposicao_repo
        self.camara_adapter = camara_adapter
        self.senado_adapter = senado_adapter

    async def atualizar_snapshot(
        self, ano: int, tipo_proposicao: str, origem: str
    ) -> CoberturaSnapshot:
        """
        Consulta a API oficial (origem = 'camara' ou 'senado') e persiste o snapshot
        de total oficial vinculado à fonte.

        A `origem` normalizada é salva como `fonte` no snapshot, de modo que futuras
        leituras saibam qual casa legislativa foi consultada.
        """
        fonte = _normalizar_fonte(origem)
        total_api_oficial = 0

        try:
            if fonte == "camara":
                total_api_oficial = await self.camara_adapter.obter_total(
                    tipo_proposicao, ano
                )
            elif fonte == "senado":
                total_api_oficial = await self.senado_adapter.obter_total(
                    tipo_proposicao, ano
                )
            else:
                logger.error(f"Origem desconhecida: {origem}")
        except Exception as e:
            logger.error(
                f"Erro ao obter total oficial de {origem} para {tipo_proposicao} {ano}: {e}"
            )

        # Se falhar e já existir um snapshot, mantemos o valor antigo para evitar sobregravar com 0
        if total_api_oficial == 0:
            existing = self.cobertura_repo.buscar_por_ano_tipo_e_fonte(
                ano, tipo_proposicao, fonte
            )
            if existing:
                total_api_oficial = existing.total_api_oficial

        snapshot = CoberturaSnapshot(
            ano=ano,
            tipo_proposicao=tipo_proposicao,
            fonte=fonte,
            total_api_oficial=total_api_oficial,
            data_atualizacao=datetime.now(UTC),
        )
        return self.cobertura_repo.salvar(snapshot)

    def obter_metricas_cobertura(
        self, ano: int, tipo_proposicao: str, fonte: str = ""
    ) -> dict:
        """
        Retorna a métrica de cobertura: proposições locais / total oficial.

        Quando `fonte` é especificada ("camara" ou "senado"), o `total_local`
        é calculado filtrando apenas proposições daquela casa legislativa,
        evitando a soma cruzada que gerava cobertura > 100%.
        """
        fonte_normalizada = _normalizar_fonte(fonte) if fonte else ""
        orgao_nome = _ORGAO_NOME_POR_FONTE.get(fonte_normalizada)

        # Busca o snapshot correto pela tripla (ano, tipo, fonte) quando disponível
        if fonte_normalizada:
            snapshot = self.cobertura_repo.buscar_por_ano_tipo_e_fonte(
                ano, tipo_proposicao, fonte_normalizada
            )
        else:
            snapshot = self.cobertura_repo.buscar_por_ano_e_tipo(ano, tipo_proposicao)

        total_local = self.proposicao_repo.contar(
            tipo=tipo_proposicao, ano=ano, orgao_origem=orgao_nome
        )

        total_api_oficial = snapshot.total_api_oficial if snapshot else 0
        percentual = (
            (total_local / total_api_oficial * 100) if total_api_oficial > 0 else 0.0
        )

        return {
            "ano": ano,
            "tipo_proposicao": tipo_proposicao,
            "fonte": fonte_normalizada or (snapshot.fonte if snapshot else ""),
            "total_local": total_local,
            "total_api_oficial": total_api_oficial,
            "percentual_cobertura": round(percentual, 2),
            "data_atualizacao": snapshot.data_atualizacao if snapshot else None,
        }

    def obter_todas_metricas_cobertura(self) -> list[dict]:
        """
        Calcula e retorna a métrica de cobertura para todos os snapshots registrados.

        Para cada snapshot, o `total_local` é filtrado pelo `orgao_origem` correspondente
        à `fonte` do snapshot — garantindo que Câmara e Senado sejam contados separadamente.
        """
        snapshots = self.cobertura_repo.buscar_todos()
        resultados = []
        for snapshot in snapshots:
            fonte_normalizada = _normalizar_fonte(snapshot.fonte)
            orgao_nome = _ORGAO_NOME_POR_FONTE.get(fonte_normalizada)

            total_local = self.proposicao_repo.contar(
                tipo=snapshot.tipo_proposicao,
                ano=snapshot.ano,
                orgao_origem=orgao_nome,
            )
            percentual = (
                (total_local / snapshot.total_api_oficial * 100)
                if snapshot.total_api_oficial > 0
                else 0.0
            )
            resultados.append(
                {
                    "ano": snapshot.ano,
                    "tipo_proposicao": snapshot.tipo_proposicao,
                    "fonte": fonte_normalizada,
                    "total_local": total_local,
                    "total_api_oficial": snapshot.total_api_oficial,
                    "percentual_cobertura": round(percentual, 2),
                    "data_atualizacao": snapshot.data_atualizacao,
                }
            )
        return resultados


def _normalizar_fonte(origem: str) -> str:
    """Normaliza 'Câmara dos Deputados' ou 'camara' → 'camara'; 'senado' → 'senado'."""
    if not origem:
        return ""
    s = origem.lower().strip()
    if "câmara" in s or "camara" in s:
        return "camara"
    if "senado" in s:
        return "senado"
    return s
