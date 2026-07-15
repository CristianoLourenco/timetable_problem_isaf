# Implementa: RF04 (UC04) — ver docs/analise_requisitos_v5.0.md
from sqlmodel import SQLModel


class SalaBase(SQLModel):
    codigo: str
    nome: str
    capacidade: int


class SalaCreate(SalaBase):
    pass


class SalaUpdate(SQLModel):
    codigo: str | None = None
    nome: str | None = None
    capacidade: int | None = None


class SalaRead(SalaBase):
    id: int
