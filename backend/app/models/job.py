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
