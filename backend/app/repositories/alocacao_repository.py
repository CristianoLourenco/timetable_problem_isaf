# Implementa: RF11, RF12 (UC11, UC12) — ver docs/analise_requisitos_v5.0.md
from sqlmodel import Session, select

from app.models.alocacao import Alocacao


class AlocacaoRepository:
    def __init__(self, session: Session):
        self.session = session

    def criar_em_lote(self, alocacoes: list[Alocacao]) -> None:
        self.session.add_all(alocacoes)
        self.session.commit()

    def listar_por_job(self, job_id: str) -> list[Alocacao]:
        return list(self.session.exec(select(Alocacao).where(Alocacao.job_id == job_id)))
