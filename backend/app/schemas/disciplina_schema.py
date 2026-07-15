# Implementa: RF03 (UC03) — ver docs/analise_requisitos_v5.0.md
from sqlmodel import SQLModel


class DisciplinaBase(SQLModel):
    codigo: str
    nome: str


class DisciplinaCreate(DisciplinaBase):
    pass


class DisciplinaUpdate(SQLModel):
    codigo: str | None = None
    nome: str | None = None


class DisciplinaRead(DisciplinaBase):
    id: int
