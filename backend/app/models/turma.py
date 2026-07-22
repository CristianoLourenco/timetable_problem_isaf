# Implementa: RF02 (UC02) — ver docs/relatorio/04_analise_desenvolvimento/
from sqlmodel import Field, SQLModel

from app.core.calendario import TurnoEnum


class Turma(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    codigo: str = Field(unique=True, index=True)  # chave de idempotência (RF08)
    nome: str
    ano_letivo: int  # ano civil (ex: 2026) — distinto de PlanoCurricular.ano (ano curricular 1..4)
    # Define o turno em que a turma tem aulas — o solver só gera variáveis nos
    # tempos desse turno (ver app/solver/builder.py) e a numeração de periodo
    # reinicia em 1 a cada turno (ver app/core/calendario.py).
    turno: TurnoEnum
    numero_alunos: int
    # curso_id não é campo próprio — obtém-se via plano_curricular_id -> PlanoCurricular.curso_id
    # (seria dependência transitiva, violação de 3FN — ver docs/media/src/diagrama_er.puml).
    plano_curricular_id: int = Field(foreign_key="planocurricular.id")
