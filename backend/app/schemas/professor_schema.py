# Implementa: RF01 (UC01) — ver docs/analise_requisitos_v5.0.md
from sqlmodel import Field, SQLModel


class ProfessorBase(SQLModel):
    nome: str
    email: str
    classificacao: int = Field(ge=1, le=5, default=3)
    vinculo_casa: bool = False


class ProfessorCreate(ProfessorBase):
    pass


class ProfessorUpdate(SQLModel):
    nome: str | None = None
    email: str | None = None
    classificacao: int | None = Field(default=None, ge=1, le=5)
    vinculo_casa: bool | None = None


class ProfessorRead(ProfessorBase):
    id: int
