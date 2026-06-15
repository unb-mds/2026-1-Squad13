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

    def upsert_em_lote_por_numero_canonico(self, proposicoes: list[Proposicao]) -> None:
        """
        Executa um upsert em lote garantindo idempotência com alta performance.
        Busca todos os registros existentes em uma única query e processa em memória.
        """
        if not proposicoes:
            return

        # 1. Extrai chaves canônicas únicas do lote
        chaves_lote = []
        for p in proposicoes:
            if p.tipo and p.numero and p.ano:
                chaves_lote.append((p.tipo.lower(), str(p.numero), p.ano))

        if not chaves_lote:
            return

        # 2. Busca todos os registros existentes que batem com as chaves do lote em uma única query
        # Nota: SQLModel/SQLAlchemy lidam com tuplas em IN clauses de forma eficiente no Postgres
        from sqlalchemy import tuple_

        statement = select(ProposicaoModel).where(
            tuple_(
                func.lower(ProposicaoModel.tipo),
                ProposicaoModel.numero,
                ProposicaoModel.ano,
            ).in_(chaves_lote)
        )
        existentes = self.session.exec(statement).all()

        # 3. Mapeia os existentes em um dicionário para busca O(1)
        mapa_existentes = {
            (m.tipo.lower(), str(m.numero), m.ano): m for m in existentes
        }

        # 4. Processa o upsert
        for prop in proposicoes:
            chave = (prop.tipo.lower(), str(prop.numero), prop.ano)
            model_novo = self._to_model(prop)

            existing = mapa_existentes.get(chave)

            if existing:
                # Atualiza os dados preservando ID e chaves canônicas
                for key, value in model_novo.model_dump(
                    exclude={"id", "tipo", "numero", "ano"}
                ).items():
                    if value is not None:
                        setattr(existing, key, value)
                self.session.add(existing)
                # Propaga o ID persistido de volta para a entidade de domínio em memória
                prop.id = existing.id
            else:
                # Caso não exista, é um insert
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
