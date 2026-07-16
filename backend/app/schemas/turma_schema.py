# Implementa: RF02 (UC02) — ver docs/04_04_analise_desenvolvimento.md
from sqlmodel import SQLModel

from app.core.calendario import TurnoEnum


class TurmaBase(SQLModel):
    codigo: str
    nome: str
    ano_letivo: int
    turno: TurnoEnum
    numero_alunos: int
    plano_curricular_id: int


class TurmaCreate(TurmaBase):
    pass


class TurmaUpdate(SQLModel):
    codigo: str | None = None
    nome: str | None = None
    ano_letivo: int | None = None
    turno: TurnoEnum | None = None
    numero_alunos: int | None = None
    plano_curricular_id: int | None = None


class TurmaRead(TurmaBase):
    id: int
