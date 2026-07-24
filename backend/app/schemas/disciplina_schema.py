# Implementa: RF03 (UC03) — ver docs/analise_requisitos_v5.0.md
from sqlmodel import SQLModel


class DisciplinaBase(SQLModel):
    codigo: str
    nome: str


class DisciplinaCreate(DisciplinaBase):
    # Opcional — Disciplina.model_post_init gera automaticamente a partir do
    # nome quando omitido (ver core/abreviacoes.py); o Gestor pode fornecer
    # o seu próprio valor se o automático ficar confuso.
    nome_curto: str | None = None


class DisciplinaUpdate(SQLModel):
    codigo: str | None = None
    nome: str | None = None
    nome_curto: str | None = None


class DisciplinaRead(DisciplinaBase):
    id: int
    nome_curto: str
