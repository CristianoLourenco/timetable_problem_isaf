# Implementa: RF11, RF12 (UC11, UC12) — ver docs/analise_requisitos_v5.0.md
#
# Resposta estruturada por dia/slot, pronta para o Flutter desserializar — nunca
# linhas soltas de Alocacao (ver backend/CLAUDE.md, Fase 5).
from datetime import time

from sqlmodel import SQLModel


class HorarioItemSchema(SQLModel):
    slot_id: int
    dia_semana: str
    tempo_ordem: int
    hora_inicio: time
    hora_fim: time
    turma_id: int
    turma_nome: str
    disciplina_id: int
    disciplina_nome: str
    professor_id: int
    professor_nome: str
    sala_id: int
    sala_nome: str


class HorarioDiaSchema(SQLModel):
    dia_semana: str
    tempos: list[HorarioItemSchema]


class HorarioResponseSchema(SQLModel):
    job_id: str
    dias: list[HorarioDiaSchema]
