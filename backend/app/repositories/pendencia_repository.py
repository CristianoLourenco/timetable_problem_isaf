# Implementa: RF13 (UC09) — persistência de pendências (ver app/models/pendencia.py)
from typing import TypedDict

from sqlmodel import Session, select

from app.models.pendencia import Pendencia


class PendenciaDict(TypedDict):
    turma_id: int
    disciplina_id: int
    tempos_em_falta: int
    razao: str
    professores_conflitantes: tuple[int, ...]
    turmas_conflitantes: tuple[int, ...]


class PendenciaRepository:
    def __init__(self, session: Session):
        self.session = session

    def criar_em_lote(self, job_id: str, pendencias: list[PendenciaDict]) -> None:
        registos = [
            Pendencia(
                job_id=job_id,
                turma_id=p["turma_id"],
                disciplina_id=p["disciplina_id"],
                tempos_em_falta=p["tempos_em_falta"],
                razao=p["razao"],
                professores_conflitantes=",".join(str(x) for x in p["professores_conflitantes"]),
                turmas_conflitantes=",".join(str(x) for x in p["turmas_conflitantes"]),
            )
            for p in pendencias
        ]
        self.session.add_all(registos)
        self.session.commit()

    def listar_por_job(self, job_id: str) -> list[Pendencia]:
        return list(self.session.exec(select(Pendencia).where(Pendencia.job_id == job_id)))

    def listar_por_job_e_turma(self, job_id: str, turma_id: int) -> list[Pendencia]:
        return list(
            self.session.exec(
                select(Pendencia).where(Pendencia.job_id == job_id, Pendencia.turma_id == turma_id)
            )
        )

    def remover_por_job(self, job_id: str) -> None:
        """Botão "limpar horário" (RF09) — apaga todas as Pendencia deste Job antes
        de o Job em si poder ser removido (FK job_id sem ondelete=CASCADE)."""
        for pendencia in self.listar_por_job(job_id):
            self.session.delete(pendencia)
        self.session.commit()

    def remover_por_turma_disciplina(self, job_id: str, turma_id: int, disciplina_id: int) -> None:
        pendencias = self.session.exec(
            select(Pendencia).where(
                Pendencia.job_id == job_id,
                Pendencia.turma_id == turma_id,
                Pendencia.disciplina_id == disciplina_id,
            )
        ).all()
        for p in pendencias:
            self.session.delete(p)
        self.session.commit()
