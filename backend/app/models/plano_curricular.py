# Implementa: RF02 (UC02) — grade curricular oficial por curso+ano+semestre,
# partilhada por todas as turmas desse ano (substitui TurmaDisciplina — ver
# docs/04_04_analise_desenvolvimento.md secção 4.2.3/4.2.4).
from sqlmodel import Field, SQLModel, UniqueConstraint


class PlanoCurricular(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("curso_id", "ano", "semestre"),)

    id: int | None = Field(default=None, primary_key=True)
    curso_id: int = Field(foreign_key="curso.id")
    ano: int  # ano curricular (1..4) — não confundir com Turma.ano_letivo (ano civil)
    semestre: str  # "1" | "2" | "Anual"
