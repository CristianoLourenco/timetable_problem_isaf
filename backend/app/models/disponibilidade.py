# Implementa: RF05 (UC05) — ver docs/04_04_analise_desenvolvimento.md
# RN07: ausência de registo para um professor = totalmente disponível (fallback aplicado no solver, não aqui)
#
# dia_semana + turno + periodo em vez de slot_id (não existe tabela Slot — ver
# app/core/calendario.py). periodo reinicia em 1 a cada turno, por isso turno faz
# sempre parte da chave.
from sqlmodel import Field, SQLModel


class Disponibilidade(SQLModel, table=True):
    professor_id: int = Field(foreign_key="professor.id", primary_key=True)
    dia_semana: str = Field(primary_key=True)
    turno: str = Field(primary_key=True)
    periodo: int = Field(primary_key=True)
