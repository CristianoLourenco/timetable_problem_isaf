# Implementa: RF11, RF12 (UC11, UC12) — ver docs/analise_requisitos_v5.0.md
# Entidade de output — resultado do solver persistido, ausente enquanto dado de entrada.
from sqlmodel import Field, SQLModel


class Alocacao(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    job_id: str = Field(foreign_key="job.id", index=True)
    turma_id: int = Field(foreign_key="turma.id")
    disciplina_id: int = Field(foreign_key="disciplina.id")
    professor_id: int = Field(foreign_key="professor.id")
    sala_id: int = Field(foreign_key="sala.id")
    slot_id: int = Field(foreign_key="slot.id")
    penalizacao_aplicada: float = 0.0  # rastreio de RN04/RN08 para auditoria
