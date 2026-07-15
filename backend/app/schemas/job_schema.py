# Implementa: RF09, RF10 (UC08, UC10) — ver docs/analise_requisitos_v5.0.md
from datetime import datetime

from sqlmodel import SQLModel

from app.models.job import JobStatus


class GerarHorarioResponse(SQLModel):
    job_id: str
    status: JobStatus


class JobRead(SQLModel):
    id: str
    status: JobStatus
    criado_em: datetime
    concluido_em: datetime | None
    diagnostico: str | None
