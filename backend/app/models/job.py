# Implementa: RF09, RF10 (UC08, UC10) — ver docs/analise_requisitos_v5.0.md
import uuid
from datetime import datetime
from enum import StrEnum

from sqlmodel import Field, SQLModel


class JobStatus(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    INFEASIBLE = "INFEASIBLE"


class Job(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    status: JobStatus = Field(default=JobStatus.PENDING)
    criado_em: datetime = Field(default_factory=datetime.utcnow)
    concluido_em: datetime | None = Field(default=None)
    diagnostico: str | None = Field(default=None)  # relatório de conflitos quando INFEASIBLE (RF13)
    # Âmbito da geração — cada Job cobre sempre um único (curso, ano_letivo, semestre):
    # as turmas desse âmbito são geradas de uma só vez (ver services/horario_service.py).
    # curso_id é obrigatório desde que se confirmou, à escala real do ISAF, que gerar
    # vários cursos em simultâneo pode ser genuinamente INFEASIBLE mesmo sem nenhum erro
    # de modelagem — coortes pequenas com corpo docente muito reduzido/partilhado entre
    # turmas paralelas tornam impossível encaixar as agendas de cursos não relacionados
    # ao mesmo tempo (não faz sentido otimizá-los em conjunto de qualquer forma, já que
    # não partilham turmas/salas/grade curricular entre si).
    curso_id: int = Field(foreign_key="curso.id")
    ano_letivo: int
    semestre: str  # "1" | "2"
