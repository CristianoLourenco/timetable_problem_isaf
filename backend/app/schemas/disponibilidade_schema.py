# Implementa: RF05 (UC05) — ver docs/relatorio/04_analise_desenvolvimento/
from sqlmodel import SQLModel

from app.schemas.tempo_schema import TempoChave


class DisponibilidadeSetSchema(SQLModel):
    tempos: list[TempoChave]


class DisponibilidadeReadSchema(SQLModel):
    tempos: list[TempoChave]
