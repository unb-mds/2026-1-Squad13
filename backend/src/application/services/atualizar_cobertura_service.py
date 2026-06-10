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


class AtualizarCoberturaService:
    """
    Serviço que atualiza e expõe os snapshots de cobertura analítica.
    Mede a relação de ingestão local contra o volume total oficial disponível nas APIs.
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
        Consulta a API oficial (origem = 'camara' ou 'senado') e persiste o snapshot de total oficial.
        """
        total_api_oficial = 0
        try:
            if origem.lower() == "camara" or "câmara" in origem.lower():
                total_api_oficial = await self.camara_adapter.obter_total(
                    tipo_proposicao, ano
                )
            elif origem.lower() == "senado":
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
            existing = self.cobertura_repo.buscar_por_ano_e_tipo(ano, tipo_proposicao)
            if existing:
                total_api_oficial = existing.total_api_oficial

        snapshot = CoberturaSnapshot(
            ano=ano,
            tipo_proposicao=tipo_proposicao,
            total_api_oficial=total_api_oficial,
            data_atualizacao=datetime.now(UTC),
        )
        return self.cobertura_repo.salvar(snapshot)

    def obter_metricas_cobertura(self, ano: int, tipo_proposicao: str) -> dict:
        """
        Retorna a métrica de cobertura: proposições locais / total oficial.
        """
        snapshot = self.cobertura_repo.buscar_por_ano_e_tipo(ano, tipo_proposicao)
        total_local = self.proposicao_repo.contar(tipo=tipo_proposicao, ano=ano)

        total_api_oficial = snapshot.total_api_oficial if snapshot else 0
        percentual = (
            (total_local / total_api_oficial * 100) if total_api_oficial > 0 else 0.0
        )

        return {
            "ano": ano,
            "tipo_proposicao": tipo_proposicao,
            "total_local": total_local,
            "total_api_oficial": total_api_oficial,
            "percentual_cobertura": round(percentual, 2),
            "data_atualizacao": snapshot.data_atualizacao if snapshot else None,
        }

    def obter_todas_metricas_cobertura(self) -> list[dict]:
        """
        Calcula e retorna a métrica de cobertura para todos os snapshots registrados.
        """
        snapshots = self.cobertura_repo.buscar_todos()
        resultados = []
        for snapshot in snapshots:
            total_local = self.proposicao_repo.contar(
                tipo=snapshot.tipo_proposicao, ano=snapshot.ano
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
                    "total_local": total_local,
                    "total_api_oficial": snapshot.total_api_oficial,
                    "percentual_cobertura": round(percentual, 2),
                    "data_atualizacao": snapshot.data_atualizacao,
                }
            )
        return resultados
