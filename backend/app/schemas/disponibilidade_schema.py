# Implementa: RF05 (UC05) — ver docs/analise_requisitos_v5.0.md
from sqlmodel import SQLModel


class DisponibilidadeSetSchema(SQLModel):
    slot_ids: list[int]


class DisponibilidadeReadSchema(SQLModel):
    slot_ids: list[int]
