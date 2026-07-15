# Qualificação docente — filtro obrigatório da modelagem esparsa do solver
from sqlmodel import Session, delete, select

from app.models.professor_disciplina import ProfessorDisciplina


class ProfessorDisciplinaRepository:
    def __init__(self, session: Session):
        self.session = session

    def listar_por_professor(self, professor_id: int) -> list[int]:
        rows = self.session.exec(
            select(ProfessorDisciplina.disciplina_id).where(ProfessorDisciplina.professor_id == professor_id)
        )
        return list(rows)

    def listar_todas(self) -> list[ProfessorDisciplina]:
        return list(self.session.exec(select(ProfessorDisciplina)))

    def substituir(self, professor_id: int, disciplina_ids: list[int]) -> None:
        self.session.exec(delete(ProfessorDisciplina).where(ProfessorDisciplina.professor_id == professor_id))
        for disciplina_id in disciplina_ids:
            self.session.add(ProfessorDisciplina(professor_id=professor_id, disciplina_id=disciplina_id))
        self.session.commit()
