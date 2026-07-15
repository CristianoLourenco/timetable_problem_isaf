# Implementa: RF06, RF07, RF08 (UC06, UC07) — ver docs/analise_requisitos_v5.0.md
from sqlmodel import SQLModel


class ErroImportacaoSchema(SQLModel):
    linha: int
    campo: str
    motivo: str


class RelatorioImportacaoSchema(SQLModel):
    total_linhas: int = 0
    importados: int = 0
    ignorados_idempotencia: int = 0
    erros: list[ErroImportacaoSchema] = []
