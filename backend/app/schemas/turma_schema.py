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


class TurmaDetalhadaSchema(TurmaBase):
    """RF02 — Turma enriquecida com o curso e o ano curricular (1..4) do seu
    PlanoCurricular, resolvidos no backend para o frontend nunca ter de fazer
    múltiplos pedidos (Turma -> PlanoCurricular -> Curso) para montar um único
    card/linha — causa provável de "turmas às vezes não trazem os seus dados"
    quando essa junção falha silenciosamente do lado do cliente.

    `ano_curricular` (1..4, de PlanoCurricular.ano) não deve ser confundido com
    `ano_letivo` (ano civil, ex: 2026, já herdado de TurmaBase) — bug real visto
    no frontend (card mostrando o ano civil onde deveria mostrar 1º/2º/3º/4º ano)."""

    id: int
    curso_codigo: str
    curso_nome: str
    ano_curricular: int
