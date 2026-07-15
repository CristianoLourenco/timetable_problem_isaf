# Implementa: RF02 (UC02) — ver docs/analise_requisitos_v5.0.md
from sqlmodel import SQLModel


class TurmaBase(SQLModel):
    codigo: str
    nome: str
    ano_letivo: int
    turno: str
    numero_alunos: int
    curso_id: int


class TurmaCreate(TurmaBase):
    pass


class TurmaUpdate(SQLModel):
    codigo: str | None = None
    nome: str | None = None
    ano_letivo: int | None = None
    turno: str | None = None
    numero_alunos: int | None = None
    curso_id: int | None = None


class TurmaRead(TurmaBase):
    id: int
