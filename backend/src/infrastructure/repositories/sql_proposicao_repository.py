from typing import List, Optional
from sqlalchemy import func
from sqlmodel import Session, select
from domain.entities.proposicao import Proposicao


class SQLProposicaoRepository:
    """
    Implementação do repositório utilizando SQLModel e PostgreSQL.
    """

    def __init__(self, session: Session):
        self.session = session

    def salvar(self, proposicao: Proposicao) -> Proposicao:
        """Salva ou atualiza uma proposição no banco."""
        self.session.add(proposicao)
        self.session.commit()
        self.session.refresh(proposicao)
        return proposicao

    def buscar_por_id(self, id: str) -> Optional[Proposicao]:
        return self.session.get(Proposicao, id)

    def buscar_por_codigo(
        self, tipo: str, numero: str, ano: int
    ) -> Optional[Proposicao]:
        """Busca uma proposição pelo conjunto único Tipo, Número e Ano."""
        statement = select(Proposicao).where(
            func.lower(Proposicao.tipo) == tipo.lower(),
            Proposicao.numero == str(numero),
            Proposicao.ano == ano,
        )
        return self.session.exec(statement).first()

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
        statement = select(Proposicao)

        if tipo:
            statement = statement.where(func.lower(Proposicao.tipo) == tipo.lower())
        if numero:
            statement = statement.where(Proposicao.numero == str(numero))
        if ano:
            statement = statement.where(Proposicao.ano == ano)
        if autor:
            statement = statement.where(
                func.lower(Proposicao.autor).contains(autor.lower())
            )
        if uf_autor:
            statement = statement.where(
                func.lower(Proposicao.uf_autor) == uf_autor.lower()
            )
        if status:
            statement = statement.where(func.lower(Proposicao.status) == status.lower())
        if orgao_origem:
            statement = statement.where(
                func.lower(Proposicao.orgao_origem) == orgao_origem.lower()
            )
        if data_inicio:
            statement = statement.where(Proposicao.data_apresentacao >= data_inicio)
        if data_fim:
            statement = statement.where(Proposicao.data_apresentacao <= data_fim)

        if busca:
            termo = f"%{busca}%"
            statement = statement.where(
                (Proposicao.ementa.ilike(termo))
                | (Proposicao.numero.ilike(termo))
                | (Proposicao.autor.ilike(termo))
            )

        statement = statement.order_by(Proposicao.id)

        if offset is not None:
            statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)

        return list(self.session.exec(statement).all())

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
        statement = select(func.count()).select_from(Proposicao)

        if tipo:
            statement = statement.where(func.lower(Proposicao.tipo) == tipo.lower())
        if numero:
            statement = statement.where(Proposicao.numero == str(numero))
        if ano:
            statement = statement.where(Proposicao.ano == ano)
        if autor:
            statement = statement.where(
                func.lower(Proposicao.autor).contains(autor.lower())
            )
        if uf_autor:
            statement = statement.where(
                func.lower(Proposicao.uf_autor) == uf_autor.lower()
            )
        if status:
            statement = statement.where(func.lower(Proposicao.status) == status.lower())
        if orgao_origem:
            statement = statement.where(
                func.lower(Proposicao.orgao_origem) == orgao_origem.lower()
            )
        if data_inicio:
            statement = statement.where(Proposicao.data_apresentacao >= data_inicio)
        if data_fim:
            statement = statement.where(Proposicao.data_apresentacao <= data_fim)

        if busca:
            termo = f"%{busca}%"
            statement = statement.where(
                (Proposicao.ementa.ilike(termo))
                | (Proposicao.numero.ilike(termo))
                | (Proposicao.autor.ilike(termo))
            )

        return self.session.exec(statement).one()

    def buscar_historico_dias_aprovacao(self, tipo: str, tema: str) -> List[int]:
        """
        Busca cirúrgica: traz apenas a coluna de tempo em dias de proposições
        que já foram concluídas e que casam com o tipo e tema solicitados.
        """
        # Explicação Pedagógica: select(Proposicao.tempo_total_dias) em vez de select(Proposicao)
        # faz com que o SQLModel gere um 'SELECT tempo_total_dias' apenas.
        # Isso evita carregar strings gigantes de 'ementa' ou JSONs pesados na memória do Python.
        statement = select(Proposicao.tempo_total_dias).where(
            func.lower(Proposicao.tipo) == tipo.lower(),
            # Postgres JSONB contains: busca o tema dentro da lista de tags
            Proposicao.tags.contains([tema]),
            # Apenas proposições concluídas têm um tempo de aprovação "final"
            Proposicao.status.in_(["Concluída (Lei)", "Sancionada", "Aprovada"]),
            Proposicao.tempo_total_dias > 0,
        )

        results = self.session.exec(statement).all()
        # Garante que não retornamos None e limpamos a lista
        return [int(d) for d in results if d is not None]
