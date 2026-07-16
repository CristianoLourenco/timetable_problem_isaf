# Implementa: RF05 (UC05) — grelha estática dia/turno/período (ver app/core/calendario.py)
from datetime import time

from sqlmodel import SQLModel


class TempoRead(SQLModel):
    dia_semana: str
    turno: str
    periodo: int
    hora_inicio: time
    hora_fim: time


class TempoChave(SQLModel):
    """Identifica um tempo letivo sem hora — usado onde só a chave (dia/turno/período)
    é necessária, ex. RF05 (disponibilidade) e RF11/RF12 (alocação)."""

    dia_semana: str
    turno: str
    periodo: int
