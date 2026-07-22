# Implementa: RF02 (UC02) — ver docs/relatorio/04_analise_desenvolvimento/
from sqlmodel import Field, SQLModel


class PlanoCurricularBase(SQLModel):
    curso_id: int
    ano: int
    semestre: str


class PlanoCurricularCreate(PlanoCurricularBase):
    pass


class PlanoCurricularUpdate(SQLModel):
    curso_id: int | None = None
    ano: int | None = None
    semestre: str | None = None


class PlanoCurricularRead(PlanoCurricularBase):
    id: int


class ItemPlanoCurricular(SQLModel):
    disciplina_id: int
    carga_horaria_semanal: int = Field(gt=0)


class PlanoCurricularDisciplinaSetSchema(SQLModel):
    itens: list[ItemPlanoCurricular]


class PlanoCurricularDisciplinaReadSchema(SQLModel):
    itens: list[ItemPlanoCurricular]
