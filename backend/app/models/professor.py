# Implementa: RF01 (UC01) — ver docs/analise_requisitos_v5.0.md
from sqlmodel import Field, SQLModel


class Professor(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    email: str = Field(unique=True, index=True)  # chave de idempotência (RF08) e validação RN10
    # Fórmula de prioridade docente (docs/analise_requisitos_v5.0.md secção 7):
    # classificacao (50%) + vinculo_casa (30%) + escassez de disponibilidade (20%, calculada em runtime)
    classificacao: int = Field(ge=1, le=5, default=3)
    vinculo_casa: bool = Field(default=False)
