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
    # Âmbito da geração — cada Job cobre sempre um único (ano_letivo, semestre): as
    # turmas desse par são geradas de uma só vez (ver services/horario_service.py).
    # Sem isto não é possível distinguir turmas de anos/semestres diferentes, nem
    # saber qual Job responde por qual turma em RF11/RF12.
    ano_letivo: int
    semestre: str  # "1" | "2"
