# Implementa: RF11, RF12 (UC11, UC12) — ver docs/04_04_analise_desenvolvimento.md
#
# Resposta estruturada por dia/tempo, pronta para o Flutter desserializar — nunca
# linhas soltas de Alocacao (ver backend/docs/CONVENCOES.md, Fase 5).
from datetime import time

from sqlmodel import SQLModel


class HorarioItemSchema(SQLModel):
    dia_semana: str
    turno: str
    periodo: int
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
    # RF13 — id da Alocacao de origem, para a UI poder chamar PATCH/DELETE
    # /alocacoes/{id} (mover/remover) diretamente a partir da grade consultada.
    alocacao_id: int


class HorarioDiaSchema(SQLModel):
    dia_semana: str
    tempos: list[HorarioItemSchema]


class HorarioResponseSchema(SQLModel):
    job_id: str
    dias: list[HorarioDiaSchema]
