# Qualificação docente — filtro obrigatório da modelagem esparsa do solver
from sqlmodel import SQLModel


class ProfessorDisciplinaSetSchema(SQLModel):
    disciplina_ids: list[int]


class ProfessorDisciplinaReadSchema(SQLModel):
    disciplina_ids: list[int]
