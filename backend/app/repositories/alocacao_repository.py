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

    def listar_por_job_e_turma(self, job_id: str, turma_id: int) -> list[Alocacao]:
        """RF11 — consulta de horário por turma."""
        return list(
            self.session.exec(
                select(Alocacao).where(Alocacao.job_id == job_id, Alocacao.turma_id == turma_id)
            )
        )

    def listar_por_job_e_professor(self, job_id: str, professor_id: int) -> list[Alocacao]:
        """RF12 — consulta de horário por professor."""
        return list(
            self.session.exec(
                select(Alocacao).where(Alocacao.job_id == job_id, Alocacao.professor_id == professor_id)
            )
        )
