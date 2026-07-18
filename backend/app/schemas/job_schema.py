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
    # RF13 — UNKNOWN por tempo esgotado é sempre "precisa de mais tempo", nunca
    # impossibilidade estrutural; o Gestor escolhe entre 3 opções, nunca um valor
    # livre (evita tempos de procura fora do que foi testado/documentado).
    tempo_maximo_minutos: Literal[1, 5, 10] = 5


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
    tempo_maximo_minutos: int
