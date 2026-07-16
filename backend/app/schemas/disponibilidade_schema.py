# Implementa: RF05 (UC05) — ver docs/04_04_analise_desenvolvimento.md
from sqlmodel import SQLModel

from app.schemas.tempo_schema import TempoChave


class DisponibilidadeSetSchema(SQLModel):
    tempos: list[TempoChave]


class DisponibilidadeReadSchema(SQLModel):
    tempos: list[TempoChave]
