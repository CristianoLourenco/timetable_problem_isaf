# Implementa: RF05 (UC05) — ver docs/analise_requisitos_v5.0.md
# RN07: ausência de registo para um professor = totalmente disponível (fallback aplicado no solver, não aqui)
from sqlmodel import Field, SQLModel


class Disponibilidade(SQLModel, table=True):
    professor_id: int = Field(foreign_key="professor.id", primary_key=True)
    slot_id: int = Field(foreign_key="slot.id", primary_key=True)
