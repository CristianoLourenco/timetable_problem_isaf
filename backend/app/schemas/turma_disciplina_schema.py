# Grade curricular — pré-requisito de dados do solver (conjunto E da definição formal UCTP)
from sqlmodel import Field, SQLModel


class ItemGradeCurricular(SQLModel):
    disciplina_id: int
    carga_horaria_semanal: int = Field(gt=0)


class TurmaDisciplinaSetSchema(SQLModel):
    itens: list[ItemGradeCurricular]


class TurmaDisciplinaReadSchema(SQLModel):
    itens: list[ItemGradeCurricular]
