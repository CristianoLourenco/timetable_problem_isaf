# Implementa: RF01 (UC01) — ver docs/04_04_analise_desenvolvimento.md
from sqlmodel import Field, SQLModel


class Professor(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    email: str = Field(unique=True, index=True)  # chave de idempotência (RF08) e validação RN10
    # Fórmula de prioridade docente (RN12, docs/04_04_analise_desenvolvimento.md secção 4.1.2):
    # classificacao (50%) + vinculo_casa (30%) + escassez de disponibilidade (20%, calculada em
    # runtime — ver app/solver/prioridade_docente.py)
    classificacao: int = Field(ge=1, le=5, default=3)
    vinculo_casa: bool = Field(default=False)
