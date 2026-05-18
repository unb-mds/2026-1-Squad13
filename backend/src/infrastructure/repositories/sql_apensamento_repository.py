from typing import List, Optional
from sqlmodel import Session, select
from domain.entities.apensamento import Apensamento

class SQLApensamentoRepository:
    def __init__(self, session: Session):
        self.session = session

    def salvar(self, apensamento: Apensamento) -> Apensamento:
        self.session.add(apensamento)
        self.session.commit()
        self.session.refresh(apensamento)
        return apensamento

    def buscar_por_materia_apensada(self, materia_id: str) -> Optional[Apensamento]:
        statement = select(Apensamento).where(Apensamento.materia_apensada_id == materia_id)
        return self.session.exec(statement).first()

    def buscar_por_materia_principal(self, materia_id: str) -> List[Apensamento]:
        statement = select(Apensamento).where(Apensamento.materia_principal_id == materia_id)
        return list(self.session.exec(statement).all())
