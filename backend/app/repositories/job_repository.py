# Implementa: RF09, RF10, RF13 (UC08, UC09, UC10) — ver docs/analise_requisitos_v5.0.md
from datetime import datetime

from sqlmodel import Session, select

from app.models.job import Job, JobStatus


class JobRepository:
    def __init__(self, session: Session):
        self.session = session

    def criar(self) -> Job:
        job = Job()
        self.session.add(job)
        self.session.commit()
        self.session.refresh(job)
        return job

    def obter(self, job_id: str) -> Job | None:
        return self.session.get(Job, job_id)

    def obter_ultimo_concluido(self) -> Job | None:
        """RF11/RF12 — o horário "atual" é sempre o resultado do Job DONE mais recente."""
        return self.session.exec(
            select(Job).where(Job.status == JobStatus.DONE).order_by(Job.concluido_em.desc())
        ).first()

    def atualizar_status(
        self,
        job: Job,
        status: JobStatus,
        *,
        diagnostico: str | None = None,
        concluido_em: datetime | None = None,
    ) -> Job:
        job.status = status
        job.diagnostico = diagnostico
        job.concluido_em = concluido_em
        self.session.add(job)
        self.session.commit()
        self.session.refresh(job)
        return job
