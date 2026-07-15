# Corresponde ao conjunto formal T (|T| = 45) da definição UCTP — ver docs/06_arquitetura_backend.md
from datetime import time

from sqlmodel import Field, SQLModel


class Slot(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    dia_semana: str  # "segunda".."sexta"
    tempo_ordem: int  # 1..9
    hora_inicio: time
    hora_fim: time
