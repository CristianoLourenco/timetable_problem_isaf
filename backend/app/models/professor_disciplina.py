# Qualificação docente — filtro obrigatório da modelagem esparsa do solver
from sqlmodel import Field, SQLModel


class ProfessorDisciplina(SQLModel, table=True):
    professor_id: int = Field(foreign_key="professor.id", primary_key=True)
    disciplina_id: int = Field(foreign_key="disciplina.id", primary_key=True)
