# Implementa: RF04 (UC04) — ver docs/analise_requisitos_v5.0.md
from sqlmodel import Field, SQLModel


class Sala(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    codigo: str = Field(unique=True, index=True)  # chave de idempotência (RF08)
    nome: str
    capacidade: int
