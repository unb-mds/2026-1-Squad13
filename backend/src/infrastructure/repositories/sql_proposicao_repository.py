from typing import List, Optional

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

    def buscar_por_id(self, id: str) -> Optional[Proposicao]:
        model = self.session.get(ProposicaoModel, id)
        return self._to_entity(model) if model else None

    def buscar_por_codigo(
        self, tipo: str, numero: str, ano: int
    ) -> Optional[Proposicao]:
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
        tipo: Optional[str] = None,
        numero: Optional[str] = None,
        ano: Optional[int] = None,
        autor: Optional[str] = None,
        uf_autor: Optional[str] = None,
        status: Optional[str] = None,
        busca: Optional[str] = None,
        orgao_origem: Optional[str] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Proposicao]:
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
        tipo: Optional[str] = None,
        numero: Optional[str] = None,
        ano: Optional[int] = None,
        autor: Optional[str] = None,
        uf_autor: Optional[str] = None,
        status: Optional[str] = None,
        busca: Optional[str] = None,
        orgao_origem: Optional[str] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
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

    def buscar_historico_dias_aprovacao(self, tipo: str, tema: str) -> List[int]:
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
