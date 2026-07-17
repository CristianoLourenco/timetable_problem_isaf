# Implementa: RF09, RF10 (UC08, UC10) — ver docs/analise_requisitos_v5.0.md
from datetime import datetime
from typing import Literal

from sqlmodel import SQLModel

from app.models.job import JobStatus


class GerarHorarioRequest(SQLModel):
    """RF09 — âmbito da geração: um Job gera sempre o horário completo de todas as
    turmas de um único (ano_letivo, semestre) de uma só vez."""

    ano_letivo: int
    semestre: Literal["1", "2"]


class GerarHorarioResponse(SQLModel):
    job_id: str
    status: JobStatus


class JobRead(SQLModel):
    id: str
    status: JobStatus
    criado_em: datetime
    concluido_em: datetime | None
    diagnostico: str | None
    ano_letivo: int
    semestre: str
