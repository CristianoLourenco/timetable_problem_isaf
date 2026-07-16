# Implementa: RF11, RF12 (UC11, UC12) — ver docs/04_04_analise_desenvolvimento.md
# Entidade de output — resultado do solver persistido, ausente enquanto dado de entrada.
#
# dia_semana + periodo em vez de slot_id (não existe tabela Slot — ver
# app/core/calendario.py para o cálculo das horas reais a partir destes campos).
# turno não é campo próprio: é sempre o turno da Turma alocada (turma_id), guardá-lo
# aqui seria dependência transitiva, violação de 3FN — obtém-se por join a Turma.
from sqlmodel import Field, SQLModel


class Alocacao(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    job_id: str = Field(foreign_key="job.id", index=True)
    turma_id: int = Field(foreign_key="turma.id")
    disciplina_id: int = Field(foreign_key="disciplina.id")
    professor_id: int = Field(foreign_key="professor.id")
    sala_id: int = Field(foreign_key="sala.id")
    dia_semana: str
    periodo: int
    penalizacao_aplicada: float = 0.0  # rastreio de RN04/RN08 para auditoria
