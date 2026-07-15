# Implementa: RF02 (UC02) — ver docs/analise_requisitos_v5.0.md
from sqlmodel import Field, SQLModel


class Turma(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    codigo: str = Field(unique=True, index=True)  # chave de idempotência (RF08)
    nome: str
    ano_letivo: int
    turno: str
    numero_alunos: int
    curso_id: int = Field(foreign_key="curso.id")
