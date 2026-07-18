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

    def listar_por_disciplina(self, disciplina_id: int) -> list[int]:
        """RF13 — dropdown de alocação manual: só professores qualificados."""
        rows = self.session.exec(
            select(ProfessorDisciplina.professor_id).where(ProfessorDisciplina.disciplina_id == disciplina_id)
        )
        return list(rows)

    def listar_todas(self) -> list[ProfessorDisciplina]:
        return list(self.session.exec(select(ProfessorDisciplina)))

    def substituir(self, professor_id: int, disciplina_ids: list[int]) -> None:
        self.session.exec(delete(ProfessorDisciplina).where(ProfessorDisciplina.professor_id == professor_id))
        for disciplina_id in disciplina_ids:
            self.session.add(ProfessorDisciplina(professor_id=professor_id, disciplina_id=disciplina_id))
        self.session.commit()

    def existe(self, professor_id: int, disciplina_id: int) -> bool:
        return (
            self.session.exec(
                select(ProfessorDisciplina).where(
                    ProfessorDisciplina.professor_id == professor_id,
                    ProfessorDisciplina.disciplina_id == disciplina_id,
                )
            ).first()
            is not None
        )

    def adicionar(self, professor_id: int, disciplina_id: int) -> None:
        """Insere um par sem apagar os já existentes — usado pela importação
        em massa (RF06/RF08), que é aditiva e idempotente por par, ao contrário
        de `substituir` (usado pelo diálogo manual, que troca o conjunto todo)."""
        self.session.add(ProfessorDisciplina(professor_id=professor_id, disciplina_id=disciplina_id))
        self.session.commit()
