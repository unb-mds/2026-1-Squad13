from sqlalchemy import func
from sqlmodel import Session, select

from domain.entities.proposicao import Proposicao
from infrastructure.database.models.proposicao_model import ProposicaoModel


class SQLProposicaoRepository:
    """
    Implementação do repositório utilizando SQLModel e PostgreSQL.
    Opera sobre ProposicaoModel (infra) e retorna Proposicao (domínio).
    """

    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: ProposicaoModel) -> Proposicao:
        return Proposicao.model_validate(model.model_dump())

    def _to_model(self, entity: Proposicao) -> ProposicaoModel:
        return ProposicaoModel.model_validate(entity.model_dump())

    def salvar(self, proposicao: Proposicao) -> Proposicao:
        """Salva ou atualiza uma proposição no banco."""
        model = self._to_model(proposicao)
        # Tenta buscar se já existe para fazer merge
        if model.id:
            existing = self.session.get(ProposicaoModel, model.id)
            if existing:
                for key, value in model.model_dump(exclude={"id"}).items():
                    setattr(existing, key, value)
                model = existing

        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def _obter_chave_busca(
        self, tipo: str, numero: str, ano: int, orgao_origem: str | None
    ) -> tuple:
        """
        Retorna a chave de busca para controle de unicidade no banco de dados.
        Proposições bicamerais (PL, PEC) a partir de 2019 (Ato Conjunto 1/2018)
        são unificadas globalmente. Matérias anteriores a 2019 ou monocamerais
        possuem chaves isoladas por órgão de origem para evitar colisões.
        """
        tipo_l = tipo.lower() if tipo else ""
        num_s = str(numero) if numero else "0"
        orgao_l = orgao_origem.lower() if orgao_origem else ""

        tipos_bicamerais = {"pl", "pec"}
        if ano and ano >= 2019 and tipo_l in tipos_bicamerais:
            return (tipo_l, num_s, ano, None)
        return (tipo_l, num_s, ano, orgao_l)

    def upsert_em_lote_por_numero_canonico(self, proposicoes: list[Proposicao]) -> None:
        """
        Executa um upsert em lote garantindo idempotência com alta performance.
        Busca todos os registros existentes em uma única query (por tipo/número/ano ou ID físico)
        e processa em memória com base nos regimes de tramitação (Ato Conjunto 1/2018).
        """
        if not proposicoes:
            return

        # 1. Extrai tuplas básicas e IDs do lote para buscar no banco em lote
        chaves_basicas = []
        ids_lote = []
        for p in proposicoes:
            if p.tipo and p.numero and p.ano:
                chaves_basicas.append((p.tipo.lower(), str(p.numero), p.ano))
            if p.id:
                ids_lote.append(p.id)

        if not chaves_basicas and not ids_lote:
            return

        # 2. Busca todos os registros existentes que batem com tipo, numero e ano, ou com ID físico
        from sqlalchemy import tuple_

        condicoes = []
        if chaves_basicas:
            condicoes.append(
                tuple_(
                    func.lower(ProposicaoModel.tipo),
                    ProposicaoModel.numero,
                    ProposicaoModel.ano,
                ).in_(chaves_basicas)
            )
        if ids_lote:
            condicoes.append(ProposicaoModel.id.in_(ids_lote))

        statement = select(ProposicaoModel).where(
            condicoes[0] if len(condicoes) == 1 else (condicoes[0] | condicoes[1])
        )
        existentes = self.session.exec(statement).all()

        # 3. Mapeia os existentes em O(1) por ID físico e por chave refinada
        mapa_por_id = {m.id: m for m in existentes if m.id}
        mapa_existentes = {}
        for m in existentes:
            chave = self._obter_chave_busca(m.tipo, m.numero, m.ano, m.orgao_origem)
            mapa_existentes[chave] = m

        # 4. Processa o upsert com mesclagem inteligente
        campos_preservar = {
            "id",
            "tipo",
            "numero",
            "ano",
            "orgao_origem",
            "autor",
            "data_apresentacao",
        }

        for prop in proposicoes:
            model_novo = self._to_model(prop)

            # Busca prioritariamente por ID físico para evitar UniqueViolation
            existing = None
            if prop.id:
                existing = mapa_por_id.get(prop.id)

            # Fallback para chave refinada caso não encontre por ID físico
            if not existing:
                chave = self._obter_chave_busca(
                    prop.tipo, prop.numero, prop.ano, prop.orgao_origem
                )
                existing = mapa_existentes.get(chave)

            if existing:
                # Verifica se a nova coleta vem de uma casa/origem diferente (cruzamento de fontes)
                casa_existente = getattr(existing, "orgao_origem", None)
                casa_nova = getattr(model_novo, "orgao_origem", None)

                mesma_origem = True
                if casa_existente and casa_nova:
                    exist_lower = casa_existente.lower()
                    nova_lower = casa_nova.lower()

                    is_exist_camara = "camara" in exist_lower or "câmara" in exist_lower
                    is_nova_camara = "camara" in nova_lower or "câmara" in nova_lower
                    is_exist_senado = "senado" in exist_lower
                    is_nova_senado = "senado" in nova_lower

                    # Se um é da Câmara e o outro é do Senado (cruzamento bicameral)
                    if (is_exist_camara and is_nova_senado) or (
                        is_exist_senado and is_nova_camara
                    ):
                        mesma_origem = False

                # Atualiza os dados preservando campos históricos se a origem for diferente
                for key, value in model_novo.model_dump().items():
                    # O ID da chave primária física nunca deve ser alterado no banco
                    if key == "id":
                        continue

                    if not mesma_origem and key in campos_preservar:
                        # Se for de origem diferente, não sobrescreve os metadados da casa iniciadora
                        if getattr(existing, key, None) is not None:
                            continue

                    if value is not None:
                        setattr(existing, key, value)
                self.session.add(existing)
                # Propaga o ID persistido de volta para a entidade de domínio em memória
                prop.id = existing.id
            else:
                # Caso não exista, realiza o insert
                self.session.add(model_novo)

        self.session.commit()

    def buscar_por_id(self, id: str) -> Proposicao | None:
        model = self.session.get(ProposicaoModel, id)
        return self._to_entity(model) if model else None

    def buscar_por_codigo(self, tipo: str, numero: str, ano: int) -> Proposicao | None:
        """Busca uma proposição pelo conjunto único Tipo, Número e Ano."""
        statement = select(ProposicaoModel).where(
            func.lower(ProposicaoModel.tipo) == tipo.lower(),
            ProposicaoModel.numero == str(numero),
            ProposicaoModel.ano == ano,
        )
        model = self.session.exec(statement).first()
        return self._to_entity(model) if model else None

    def filtrar(
        self,
        tipo: str | None = None,
        numero: str | None = None,
        ano: int | None = None,
        autor: str | None = None,
        uf_autor: str | None = None,
        status: str | None = None,
        busca: str | None = None,
        orgao_origem: str | None = None,
        data_inicio: str | None = None,
        data_fim: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Proposicao]:
        statement = select(ProposicaoModel)

        if tipo:
            statement = statement.where(
                func.lower(ProposicaoModel.tipo) == tipo.lower()
            )
        if numero:
            statement = statement.where(ProposicaoModel.numero == str(numero))
        if ano:
            statement = statement.where(ProposicaoModel.ano == ano)
        if autor:
            statement = statement.where(
                func.lower(ProposicaoModel.autor).contains(autor.lower())
            )
        if uf_autor:
            statement = statement.where(
                func.lower(ProposicaoModel.uf_autor) == uf_autor.lower()
            )
        if status:
            statement = statement.where(
                func.lower(ProposicaoModel.status) == status.lower()
            )
        if orgao_origem:
            statement = statement.where(
                func.lower(ProposicaoModel.orgao_origem) == orgao_origem.lower()
            )
        if data_inicio:
            statement = statement.where(
                ProposicaoModel.data_apresentacao >= data_inicio
            )
        if data_fim:
            statement = statement.where(ProposicaoModel.data_apresentacao <= data_fim)

        if busca:
            termo = f"%{busca}%"
            statement = statement.where(
                (ProposicaoModel.ementa.ilike(termo))
                | (ProposicaoModel.numero.ilike(termo))
                | (ProposicaoModel.autor.ilike(termo))
            )

        statement = statement.order_by(ProposicaoModel.id)

        if offset is not None:
            statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)

        models = self.session.exec(statement).all()
        return [self._to_entity(m) for m in models]

    def contar(
        self,
        tipo: str | None = None,
        numero: str | None = None,
        ano: int | None = None,
        autor: str | None = None,
        uf_autor: str | None = None,
        status: str | None = None,
        busca: str | None = None,
        orgao_origem: str | None = None,
        data_inicio: str | None = None,
        data_fim: str | None = None,
    ) -> int:
        statement = select(func.count()).select_from(ProposicaoModel)

        if tipo:
            statement = statement.where(
                func.lower(ProposicaoModel.tipo) == tipo.lower()
            )
        if numero:
            statement = statement.where(ProposicaoModel.numero == str(numero))
        if ano:
            statement = statement.where(ProposicaoModel.ano == ano)
        if autor:
            statement = statement.where(
                func.lower(ProposicaoModel.autor).contains(autor.lower())
            )
        if uf_autor:
            statement = statement.where(
                func.lower(ProposicaoModel.uf_autor) == uf_autor.lower()
            )
        if status:
            statement = statement.where(
                func.lower(ProposicaoModel.status) == status.lower()
            )
        if orgao_origem:
            statement = statement.where(
                func.lower(ProposicaoModel.orgao_origem) == orgao_origem.lower()
            )
        if data_inicio:
            statement = statement.where(
                ProposicaoModel.data_apresentacao >= data_inicio
            )
        if data_fim:
            statement = statement.where(ProposicaoModel.data_apresentacao <= data_fim)

        if busca:
            termo = f"%{busca}%"
            statement = statement.where(
                (ProposicaoModel.ementa.ilike(termo))
                | (ProposicaoModel.numero.ilike(termo))
                | (ProposicaoModel.autor.ilike(termo))
            )

        return self.session.exec(statement).one()

    def buscar_historico_dias_aprovacao(self, tipo: str, tema: str) -> list[int]:
        """
        Busca cirúrgica: traz apenas a coluna de tempo em dias de proposições
        que já foram concluídas e que casam com o tipo e tema solicitados.
        """
        statement = select(ProposicaoModel.tempo_total_dias).where(
            func.lower(ProposicaoModel.tipo) == tipo.lower(),
            # Postgres JSONB contains: busca o tema dentro da lista de tags
            ProposicaoModel.tags.contains([tema]),
            # Apenas proposições concluídas têm um tempo de aprovação "final"
            ProposicaoModel.status.in_(["Concluída (Lei)", "Sancionada", "Aprovada"]),
            ProposicaoModel.tempo_total_dias > 0,
        )

        results = self.session.exec(statement).all()
        return [int(d) for d in results if d is not None]
