# Implementa: RF13 (UC09) — schemas dos endpoints de alocação manual
from sqlmodel import SQLModel


class PendenciaRead(SQLModel):
    turma_id: int
    disciplina_id: int
    tempos_em_falta: int
    razao: str
    professores_conflitantes: list[int]
    turmas_conflitantes: list[int]


class ProfessorQualificadoRead(SQLModel):
    id: int
    nome: str
    classificacao: int
    vinculo_casa: bool


class BlocoVagoRead(SQLModel):
    dia_semana: str
    turno: str
    periodos: list[int]


class CriarAlocacaoManualRequest(SQLModel):
    job_id: str
    turma_id: int
    disciplina_id: int
    professor_id: int
    sala_id: int
    dia_semana: str
    turno: str
    periodos: list[int]


class AlocacaoRead(SQLModel):
    id: int
    job_id: str
    turma_id: int
    disciplina_id: int
    professor_id: int
    sala_id: int
    dia_semana: str
    periodo: int


class MoverAlocacaoRequest(SQLModel):
    dia_semana: str
    periodo: int
