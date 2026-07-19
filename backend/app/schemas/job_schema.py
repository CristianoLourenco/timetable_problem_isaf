# Implementa: RF09, RF10 (UC08, UC10) — ver docs/analise_requisitos_v5.0.md
from datetime import datetime
from typing import Literal

from sqlmodel import SQLModel

from app.models.job import JobStatus


class GerarHorarioRequest(SQLModel):
    """RF09 — âmbito da geração: um Job gera sempre o horário completo de todas as
    turmas de um único (ano_letivo, semestre) de uma só vez.

    Não recebe tempo de procura — job_runner.py escala automaticamente por
    2/5/10 min (RF13, ver ESCALONAMENTO_TEMPO_MINUTOS), sempre começando pelo
    valor mais baixo, nunca uma escolha do Gestor."""

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
    # Última tentativa de tempo de procura usada pelo escalonamento automático
    # (RF13) — auditoria/UI ("resolvido em 5 min"), nunca um input do Gestor.
    tempo_maximo_minutos: int
